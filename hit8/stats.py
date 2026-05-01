"""
stats.py — Capacidad 2: Estadísticas de precios por producto.

Funciones:
  - compute_stats: calcula min, max, mediana, promedio y desvío estándar.
  - print_stats_table: imprime tabla formateada en stdout (solo stdlib).
  - save_stats: persiste el array de estadísticas en output/stats.json.
"""

import os
import json
import logging
import statistics

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Cálculo de estadísticas
# ---------------------------------------------------------------------------

def compute_stats(results: list[dict], product: str) -> dict:
    """Calcula estadísticas de precios sobre los resultados de un producto.

    Solo considera precios numéricos estrictamente positivos (> 0).
    Precios None o <= 0 son ignorados en los cálculos pero sí se cuentan
    en `n_resultados`.

    Args:
        results: Lista de dicts con campo 'precio' (float | None).
        product: Nombre del producto (usado como clave en el resultado).

    Returns:
        Dict con keys: producto, n_resultados, n_precios_validos,
        precio_minimo, precio_maximo, precio_mediana, precio_promedio,
        precio_desvio_std. Todos los campos de precio son None cuando
        no hay precios válidos.
    """
    precios = [
        r["precio"]
        for r in results
        if r.get("precio") is not None and r["precio"] > 0
    ]

    if not precios:
        logger.warning(
            "Sin precios válidos para estadísticas | producto=%s", product
        )
        return {
            "producto": product,
            "n_resultados": len(results),
            "n_precios_validos": 0,
            "precio_minimo": None,
            "precio_maximo": None,
            "precio_mediana": None,
            "precio_promedio": None,
            "precio_desvio_std": None,
        }

    return {
        "producto": product,
        "n_resultados": len(results),
        "n_precios_validos": len(precios),
        "precio_minimo": min(precios),
        "precio_maximo": max(precios),
        "precio_mediana": statistics.median(precios),
        "precio_promedio": round(statistics.mean(precios), 2),
        "precio_desvio_std": (
            round(statistics.stdev(precios), 2) if len(precios) > 1 else 0.0
        ),
    }


# ---------------------------------------------------------------------------
# Tabla formateada en stdout (solo stdlib, sin tabulate ni rich)
# ---------------------------------------------------------------------------

def print_stats_table(all_stats: list[dict]) -> None:
    """Imprime una tabla de resumen de estadísticas de precios en stdout.

    Usa únicamente `print()` y la stdlib; no requiere dependencias externas.

    Args:
        all_stats: Lista de dicts producidos por `compute_stats`.
    """
    col_widths = [30, 8, 8, 15, 15, 15, 15, 15]
    headers = [
        "Producto", "N", "Válidos",
        "Mínimo", "Máximo", "Mediana", "Promedio", "Desvío Std",
    ]

    def row(cols: list) -> str:
        return " | ".join(str(c).ljust(w) for c, w in zip(cols, col_widths))

    separator = "-+-".join("-" * w for w in col_widths)

    print("\n" + "=" * len(separator))
    print("RESUMEN DE PRECIOS (ARS)")
    print("=" * len(separator))
    print(row(headers))
    print(separator)

    for s in all_stats:
        cols = [
            s["producto"][:29],
            s["n_resultados"],
            s["n_precios_validos"],
            f"{s['precio_minimo']:,.0f}"    if s["precio_minimo"]    is not None else "N/A",
            f"{s['precio_maximo']:,.0f}"    if s["precio_maximo"]    is not None else "N/A",
            f"{s['precio_mediana']:,.0f}"   if s["precio_mediana"]   is not None else "N/A",
            f"{s['precio_promedio']:,.0f}"  if s["precio_promedio"]  is not None else "N/A",
            f"{s['precio_desvio_std']:,.0f}" if s["precio_desvio_std"] is not None else "N/A",
        ]
        print(row(cols))

    print("=" * len(separator) + "\n")


# ---------------------------------------------------------------------------
# Persistencia en output/stats.json
# ---------------------------------------------------------------------------

def save_stats(all_stats: list[dict], output_dir: str = "output") -> None:
    """Escribe el array de estadísticas en `output_dir/stats.json`.

    El archivo se sobreescribe en cada ejecución (representa la corrida actual).

    Args:
        all_stats: Lista de dicts producidos por `compute_stats`.
        output_dir: Directorio de salida (default="output").
    """
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "stats.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2)
    logger.info("Estadísticas guardadas en %s", path)
