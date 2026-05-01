"""
tests/test_pagination.py — Tests para pagination.py (Capacidad 1).

Cubre build_page_url y deduplicate sin requerir un WebDriver real.
"""

from unittest.mock import MagicMock, patch

import pytest

from pagination import build_page_url, deduplicate


class TestBuildPageUrl:
    def test_primera_pagina_sin_offset(self):
        """Página 1 (offset=0) no debe incluir el sufijo _Desde_."""
        url = build_page_url("bicicleta rodado 29", offset=0)
        assert "bicicleta" in url.lower()
        assert "_Desde_" not in url

    def test_primera_pagina_contiene_base_url(self):
        """La URL debe apuntar al dominio correcto de MercadoLibre Argentina."""
        url = build_page_url("notebook lenovo", offset=0)
        assert url.startswith("https://listado.mercadolibre.com.ar/")

    def test_segunda_pagina_con_offset(self):
        """Offset > 0 debe generar la URL con el sufijo _Desde_{offset+1}."""
        url = build_page_url("bicicleta rodado 29", offset=10)
        assert "_Desde_" in url
        assert "_Desde_11_" in url

    def test_tercera_pagina_offset_correcto(self):
        """Offset 20 → _Desde_21."""
        url = build_page_url("notebook lenovo", offset=20)
        assert "_Desde_21_" in url

    def test_producto_con_espacios_url_encoded(self):
        """Los espacios deben codificarse (+ o %20), no aparecer literales."""
        url = build_page_url("iPhone 16 Pro Max", offset=0)
        assert " " not in url

    def test_noindex_true_en_paginas_siguientes(self):
        """Las páginas 2+ deben incluir NoIndex_True para evitar indexación duplicada."""
        url = build_page_url("auriculares bluetooth", offset=10)
        assert "NoIndex_True" in url

    def test_noindex_ausente_en_primera_pagina(self):
        """La primera página NO debe incluir NoIndex_True."""
        url = build_page_url("auriculares bluetooth", offset=0)
        assert "NoIndex_True" not in url


class TestDeduplicate:
    def test_elimina_duplicados_por_link(self):
        """Dos resultados con el mismo link deben reducirse a uno."""
        items = [
            {"link": "https://ml.com/a", "titulo": "A"},
            {"link": "https://ml.com/a", "titulo": "A"},
            {"link": "https://ml.com/b", "titulo": "B"},
        ]
        result = deduplicate(items)
        assert len(result) == 2

    def test_preserva_orden_de_primera_aparicion(self):
        """El primer elemento visto debe conservarse, no el duplicado."""
        items = [
            {"link": "https://ml.com/x", "titulo": "Primero"},
            {"link": "https://ml.com/y", "titulo": "Y"},
            {"link": "https://ml.com/x", "titulo": "Segundo"},
        ]
        result = deduplicate(items)
        assert result[0]["titulo"] == "Primero"

    def test_sin_link_se_incluye(self):
        """Resultados sin link (None) se incluyen aunque haya varios."""
        items = [{"link": None, "titulo": "A"}, {"link": None, "titulo": "B"}]
        result = deduplicate(items)
        assert len(result) == 2

    def test_link_vacio_tratado_como_sin_link(self):
        """Link vacío ("") también se trata como 'sin link' y se incluye."""
        items = [{"link": "", "titulo": "A"}, {"link": "", "titulo": "B"}]
        result = deduplicate(items)
        assert len(result) == 2

    def test_lista_vacia(self):
        """Lista vacía debe retornar lista vacía."""
        assert deduplicate([]) == []

    def test_sin_duplicados_retorna_todos(self):
        """Lista sin duplicados debe retornar todos los elementos."""
        items = [
            {"link": "https://ml.com/1", "titulo": "Uno"},
            {"link": "https://ml.com/2", "titulo": "Dos"},
            {"link": "https://ml.com/3", "titulo": "Tres"},
        ]
        assert len(deduplicate(items)) == 3

    def test_todos_duplicados_retorna_uno(self):
        """Si todos los items tienen el mismo link, retorna sólo uno."""
        items = [{"link": "https://ml.com/a", "titulo": str(i)} for i in range(5)]
        assert len(deduplicate(items)) == 1
