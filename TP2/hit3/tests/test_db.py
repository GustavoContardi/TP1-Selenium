"""
tests/test_db.py — Tests para db.py (Capacidad 3).

Todos los tests mockean get_connection completamente.
No se requiere una instancia Postgres real.
"""

from unittest.mock import MagicMock, patch, call
import os

import pytest

from db import save_results, postgres_enabled, run_migrations


class TestPostgresEnabled:
    def test_habilitado_con_host_definido(self, monkeypatch):
        """postgres_enabled() es True cuando POSTGRES_HOST está en el entorno."""
        monkeypatch.setenv("POSTGRES_HOST", "postgres")
        assert postgres_enabled() is True

    def test_deshabilitado_sin_host(self, monkeypatch):
        """postgres_enabled() es False cuando POSTGRES_HOST no está definido."""
        monkeypatch.delenv("POSTGRES_HOST", raising=False)
        assert postgres_enabled() is False

    def test_deshabilitado_con_host_vacio(self, monkeypatch):
        """POSTGRES_HOST vacío ("") también da False (bool("") == False)."""
        monkeypatch.setenv("POSTGRES_HOST", "")
        assert postgres_enabled() is False


class TestSaveResults:
    def test_lista_vacia_retorna_cero(self):
        """save_results con lista vacía retorna 0 sin intentar conectar."""
        with patch("db.get_connection") as mock_conn:
            result = save_results([], "producto", "chrome")
        assert result == 0
        mock_conn.assert_not_called()

    def _make_mock_conn(self):
        """Helper: crea un mock de conexión psycopg2 compatible con context-manager."""
        mock_cur = MagicMock()
        mock_cur.__enter__ = MagicMock(return_value=mock_cur)
        mock_cur.__exit__ = MagicMock(return_value=False)

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cur

        return mock_conn, mock_cur

    def test_inserta_cada_resultado(self):
        """save_results con un item hace exactamente un execute de INSERT."""
        mock_conn, mock_cur = self._make_mock_conn()
        items = [
            {
                "titulo": "Notebook Lenovo",
                "precio": 1500000.0,
                "link": "https://ml.com/a",
                "tienda_oficial": "Lenovo Store",
                "envio_gratis": True,
                "cuotas_sin_interes": "12 cuotas sin interés",
            }
        ]
        with patch("db.get_connection", return_value=mock_conn):
            count = save_results(items, "notebook lenovo", "chrome")

        assert count == 1
        assert mock_cur.execute.called

    def test_retorna_cantidad_insertada(self):
        """save_results retorna el número correcto de filas insertadas."""
        mock_conn, mock_cur = self._make_mock_conn()
        items = [
            {"titulo": f"Item {i}", "precio": float(i * 100),
             "link": f"https://ml.com/{i}", "tienda_oficial": None,
             "envio_gratis": False, "cuotas_sin_interes": None}
            for i in range(5)
        ]
        with patch("db.get_connection", return_value=mock_conn):
            count = save_results(items, "producto", "firefox")

        assert count == 5

    def test_cierra_conexion_siempre(self):
        """La conexión debe cerrarse incluso si ocurre un error en el INSERT."""
        mock_conn, mock_cur = self._make_mock_conn()
        # Hacer que execute falle para simular error de DB
        mock_cur.execute.side_effect = Exception("DB error simulado")

        items = [{"titulo": "A", "precio": 100.0, "link": "https://ml.com/a",
                  "tienda_oficial": None, "envio_gratis": False,
                  "cuotas_sin_interes": None}]

        with patch("db.get_connection", return_value=mock_conn):
            count = save_results(items, "producto", "chrome")

        # En caso de error la función retorna 0 pero debe haber llamado close
        mock_conn.close.assert_called_once()

    def test_campos_none_se_pasan_correctamente(self):
        """Los campos opcionales None deben pasarse como NULL a la query."""
        mock_conn, mock_cur = self._make_mock_conn()
        items = [
            {"titulo": "Item con nulos", "precio": None,
             "link": None, "tienda_oficial": None,
             "envio_gratis": None, "cuotas_sin_interes": None}
        ]
        with patch("db.get_connection", return_value=mock_conn):
            save_results(items, "prod", "chrome")

        # Verificar que execute fue llamado con la tupla correcta
        args = mock_cur.execute.call_args_list[-1][0][1]
        assert args[0] == "prod"          # producto
        assert args[1] == "Item con nulos"  # titulo
        assert args[2] is None             # precio → NULL
        assert args[7] == "chrome"         # browser


class TestRunMigrations:
    def test_crea_tabla_schema_migrations(self):
        """run_migrations debe ejecutar CREATE TABLE IF NOT EXISTS schema_migrations."""
        mock_conn, mock_cur = MagicMock(), MagicMock()
        mock_cur.__enter__ = MagicMock(return_value=mock_cur)
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cur
        # fetchone retorna None → no hay migrations previas, pero glob no encuentra nada
        mock_cur.fetchone.return_value = None

        with patch("db.get_connection", return_value=mock_conn), \
             patch("glob.glob", return_value=[]):
            run_migrations("migrations")

        # Debe haberse llamado CREATE TABLE
        calls_sql = [str(c) for c in mock_cur.execute.call_args_list]
        assert any("schema_migrations" in s for s in calls_sql)

    def test_idempotente_no_reaaplica_migration_ya_aplicada(self):
        """Una migration ya en schema_migrations no debe ejecutarse de nuevo."""
        mock_conn, mock_cur = MagicMock(), MagicMock()
        mock_cur.__enter__ = MagicMock(return_value=mock_cur)
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cur
        # Simular que la migration ya está aplicada
        mock_cur.fetchone.return_value = (1,)

        fake_sql_path = "migrations/001_initial_schema.sql"

        with patch("db.get_connection", return_value=mock_conn), \
             patch("glob.glob", return_value=[fake_sql_path]):
            run_migrations("migrations")

        # No debe haberse llamado open() para leer el SQL
        # (verificamos que execute fue llamado sólo para CREATE TABLE y SELECT,
        #  no para el INSERT de nueva migration)
        exec_calls = [str(c) for c in mock_cur.execute.call_args_list]
        insert_calls = [c for c in exec_calls if "INSERT INTO schema_migrations" in c]
        assert len(insert_calls) == 0
