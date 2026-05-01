-- migrations/002_add_browser_column.sql
-- Agrega la columna 'browser' a scrape_results para registrar qué browser
-- fue usado en cada corrida del scraper.
-- Idempotente: usa ADD COLUMN IF NOT EXISTS (Postgres >= 9.6).

ALTER TABLE scrape_results
    ADD COLUMN IF NOT EXISTS browser TEXT;

COMMENT ON COLUMN scrape_results.browser IS 'chrome | firefox — browser usado en la corrida';
