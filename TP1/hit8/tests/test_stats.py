"""
tests/test_stats.py — Tests para stats.py (Capacidad 2).

Cubre compute_stats con distintos escenarios de precios.
No requiere Selenium ni Postgres.
"""

import pytest

from stats import compute_stats


class TestComputeStats:
    def test_stats_con_precios_validos(self):
        """Verifica min, max, mediana, promedio y n_precios_validos con datos limpios."""
        results = [{"precio": float(p)} for p in [100, 200, 300, 400, 500]]
        s = compute_stats(results, "test")
        assert s["precio_minimo"] == 100
        assert s["precio_maximo"] == 500
        assert s["precio_mediana"] == 300
        assert s["precio_promedio"] == 300.0
        assert s["n_precios_validos"] == 5
        assert s["n_resultados"] == 5
        assert s["producto"] == "test"

    def test_stats_ignora_precios_none(self):
        """Precios None no deben contar como válidos."""
        results = [{"precio": 100}, {"precio": None}, {"precio": 200}]
        s = compute_stats(results, "test")
        assert s["n_precios_validos"] == 2
        assert s["n_resultados"] == 3

    def test_stats_ignora_precios_cero_o_negativos(self):
        """Precios <= 0 se descartan del cálculo."""
        results = [{"precio": 0}, {"precio": -100}, {"precio": 500}]
        s = compute_stats(results, "test")
        assert s["n_precios_validos"] == 1
        assert s["precio_minimo"] == 500
        assert s["precio_maximo"] == 500

    def test_stats_sin_precios_validos_retorna_none(self):
        """Sin precios válidos, todos los campos de precio deben ser None."""
        results = [{"precio": None}]
        s = compute_stats(results, "test")
        assert s["precio_minimo"] is None
        assert s["precio_maximo"] is None
        assert s["precio_mediana"] is None
        assert s["precio_promedio"] is None
        assert s["precio_desvio_std"] is None
        assert s["n_precios_validos"] == 0
        assert s["n_resultados"] == 1

    def test_desvio_std_un_solo_precio_es_cero(self):
        """Con un único precio válido, el desvío estándar debe ser 0.0."""
        results = [{"precio": 1000.0}]
        s = compute_stats(results, "test")
        assert s["precio_desvio_std"] == 0.0

    def test_desvio_std_multiples_precios(self):
        """Con múltiples precios, el desvío estándar debe ser > 0."""
        results = [{"precio": float(p)} for p in [100, 300, 500]]
        s = compute_stats(results, "test")
        assert s["precio_desvio_std"] > 0

    def test_resultados_lista_vacia(self):
        """Lista vacía: todos None, n_resultados=0."""
        s = compute_stats([], "vacío")
        assert s["n_resultados"] == 0
        assert s["n_precios_validos"] == 0
        assert s["precio_minimo"] is None

    def test_producto_se_preserva_en_resultado(self):
        """El nombre de producto debe aparecer en el dict de salida."""
        results = [{"precio": 999.0}]
        s = compute_stats(results, "Mi Producto")
        assert s["producto"] == "Mi Producto"

    def test_todos_los_keys_presentes(self):
        """El dict retornado siempre tiene todas las claves esperadas."""
        expected_keys = {
            "producto", "n_resultados", "n_precios_validos",
            "precio_minimo", "precio_maximo", "precio_mediana",
            "precio_promedio", "precio_desvio_std",
        }
        s = compute_stats([], "test")
        assert set(s.keys()) == expected_keys
