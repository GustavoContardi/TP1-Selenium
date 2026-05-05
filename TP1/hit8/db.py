"""
db.py — Capacidad 3: Histórico con PostgreSQL en k3s.

Funciones:
  - postgres_enabled: verifica si POSTGRES_HOST está definido.
  - get_connection: abre conexión a Postgres con psycopg2.
  - run_migrations: aplica archivos .sql en migrations/ de forma idempotente.
  - save_results: inserta los resultados de una corrida en scrape_results.

La escritura a Postgres es OPCIONAL: si POSTGRES_HOST no está definido el
scraper continúa funcionando sin base de datos para preservar compatibilidad
con los Hits anteriores.
"""

import os
import glob
import logging

import psycopg2

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Feature flag
# ---------------------------------------------------------------------------

def postgres_enabled() -> bool:
    """Retorna True si POSTGRES_HOST está definido en el entorno.

    Permite ejecutar el scraper sin Postgres (compatibilidad con Hits anteriores).
    """
    return bool(os.getenv("POSTGRES_HOST"))


# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------

def get_connection():
    """Abre y retorna una conexión psycopg2 a la base de datos configurada.

    Lee los parámetros desde variables de entorno con valores por defecto
    aptos para el cluster k3s (donde el Service headless resuelve 'postgres').

    Returns:
        psycopg2.connection — Debe cerrarse por el caller (preferiblemente
        usando 'with' o llamando a .close() en un bloque finally).

    Raises:
        psycopg2.OperationalError si no puede conectar dentro de 10 segundos.
    """
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "scraper_db"),
        user=os.getenv("POSTGRES_USER", "scraper"),
        password=os.getenv("POSTGRES_PASSWORD", "scraper_pass_dev_only"),
        connect_timeout=10,
    )


# ---------------------------------------------------------------------------
# Runner de migrations idempotente
# ---------------------------------------------------------------------------

def run_migrations(migrations_dir: str = "migrations") -> None:
    """Aplica todos los archivos .sql en `migrations_dir` que no se hayan aplicado.

    Mantiene la tabla `schema_migrations` como registro de archivos ya
    aplicados. Es idempotente: puede ejecutarse múltiples veces sin error
    ni duplicación.

    Args:
        migrations_dir: Ruta al directorio que contiene los archivos .sql.
                        Por defecto "migrations" relativo al CWD.
    """
    conn = get_connection()
    try:
        with conn:
            # Crear tabla de control si no existe
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        filename   TEXT PRIMARY KEY,
                        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                """)

            # Aplicar cada migration en orden léxico
            for path in sorted(glob.glob(f"{migrations_dir}/*.sql")):
                filename = os.path.basename(path)
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM schema_migrations WHERE filename = %s",
                        (filename,),
                    )
                    if cur.fetchone():
                        logger.debug(
                            "Migration ya aplicada, saltando: %s", filename
                        )
                        continue

                    with open(path, encoding="utf-8") as f:
                        sql = f.read()

                    cur.execute(sql)
                    cur.execute(
                        "INSERT INTO schema_migrations (filename) VALUES (%s)",
                        (filename,),
                    )
                    logger.info("Migration aplicada: %s", filename)

        logger.info("Migrations completadas")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Persistencia de resultados de scraping
# ---------------------------------------------------------------------------

def save_results(results: list[dict], product: str, browser: str) -> int:
    """Inserta los resultados de una corrida de scraping en `scrape_results`.

    Cada llamada inserta nuevas filas, permitiendo que el histórico se
    acumule entre corridas del CronJob.

    Args:
        results: Lista de dicts con los campos del item scrapeado.
        product: Nombre del producto (se almacena en la columna 'producto').
        browser: Identificador del browser usado ("chrome" | "firefox").

    Returns:
        Número de filas insertadas exitosamente.
    """
    if not results:
        logger.warning(
            "Sin resultados para persistir | producto=%s", product
        )
        return 0

    conn = get_connection()
    inserted = 0
    try:
        with conn:
            with conn.cursor() as cur:
                for r in results:
                    cur.execute(
                        """
                        INSERT INTO scrape_results
                            (producto, titulo, precio, link,
                             tienda_oficial, envio_gratis,
                             cuotas_sin_interes, browser)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            product,
                            r.get("titulo"),
                            r.get("precio"),
                            r.get("link"),
                            r.get("tienda_oficial"),
                            r.get("envio_gratis"),
                            r.get("cuotas_sin_interes"),
                            browser,
                        ),
                    )
                    inserted += 1
        logger.info(
            "Resultados persistidos | producto=%s | filas=%d",
            product, inserted,
        )
    except Exception as e:
        logger.error(
            "Error persistiendo resultados | producto=%s | %s",
            product, e,
            exc_info=True,
        )
    finally:
        conn.close()

    return inserted
