-- migrations/001_initial_schema.sql
-- Schema inicial para almacenar el histórico de resultados de scraping.
-- Idempotente: usa IF NOT EXISTS en todas las sentencias.

CREATE TABLE IF NOT EXISTS scrape_results (
    id                  BIGSERIAL     PRIMARY KEY,
    producto            TEXT          NOT NULL,
    titulo              TEXT          NOT NULL,
    precio              NUMERIC(12,2),
    link                TEXT,
    tienda_oficial      TEXT,
    envio_gratis        BOOLEAN,
    cuotas_sin_interes  TEXT,
    scraped_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- Índice para consultas de histórico por producto y fecha (orden DESC para
-- facilitar la query "últimas N corridas por producto").
CREATE INDEX IF NOT EXISTS idx_scrape_results_producto_fecha
    ON scrape_results (producto, scraped_at DESC);

-- Índice parcial sobre precio para acelerar estadísticas agregadas,
-- excluyendo NULLs para mantener el índice pequeño.
CREATE INDEX IF NOT EXISTS idx_scrape_results_precio
    ON scrape_results (precio)
    WHERE precio IS NOT NULL;
