import json
import re
import pytest

REQUIRED_FIELDS = {"titulo", "precio", "link", "tienda_oficial", "envio_gratis", "cuotas_sin_interes"}
URL_PATTERN = re.compile(r"^https://")

class TestSchemaResultado:
    def test_tiene_todos_los_campos_requeridos(self, sample_item):
        assert REQUIRED_FIELDS.issubset(sample_item.keys())

    def test_titulo_es_string_no_vacio(self, sample_item):
        assert isinstance(sample_item["titulo"], str)
        assert len(sample_item["titulo"]) > 0

    def test_precio_es_numero_positivo(self, sample_item):
        assert isinstance(sample_item["precio"], (int, float))
        assert sample_item["precio"] > 0

    def test_link_es_url_absoluta(self, sample_item):
        assert isinstance(sample_item["link"], str)
        assert URL_PATTERN.match(sample_item["link"])

    def test_tienda_oficial_es_string_o_none(self, sample_item):
        val = sample_item["tienda_oficial"]
        assert val is None or isinstance(val, str)

    def test_envio_gratis_es_booleano(self, sample_item):
        assert isinstance(sample_item["envio_gratis"], bool)

    def test_cuotas_es_string_o_none(self, sample_item):
        val = sample_item["cuotas_sin_interes"]
        assert val is None or isinstance(val, str)

class TestSchemaListaResultados:
    def test_minimo_10_resultados(self, sample_results):
        assert len(sample_results) >= 10

    def test_todos_los_precios_positivos(self, sample_results):
        precios = [r["precio"] for r in sample_results if r["precio"] is not None]
        assert all(p > 0 for p in precios)

    def test_todos_los_links_absolutos(self, sample_results):
        links = [r["link"] for r in sample_results if r["link"] is not None]
        assert all(URL_PATTERN.match(l) for l in links)

    def test_json_file_parseable(self, output_json_file):
        with open(output_json_file, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) >= 1

class TestSchemaNullsOpcionales:
    def test_item_sin_tienda_oficial_es_valido(self, sample_item):
        sample_item["tienda_oficial"] = None
        assert REQUIRED_FIELDS.issubset(sample_item.keys())  # campo existe, valor null

    def test_item_sin_cuotas_es_valido(self, sample_item):
        sample_item["cuotas_sin_interes"] = None
        assert REQUIRED_FIELDS.issubset(sample_item.keys())
