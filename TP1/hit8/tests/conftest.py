import pytest
from unittest.mock import MagicMock
import json
import os
import sys

# Agrega el directorio raíz de hit8 al path para importar módulos
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)


@pytest.fixture
def mock_element():
    el = MagicMock()
    el.text = ""
    el.get_attribute.return_value = ""
    el.find_element.return_value = el
    return el


@pytest.fixture
def context():
    return {
        "producto": "iPhone 16 Pro Max",
        "browser": "chrome",
        "resultado_index": 0,
    }


@pytest.fixture
def sample_item():
    return {
        "titulo": "Apple iPhone 16 Pro Max 256GB",
        "precio": 2500000.0,
        "link": "https://www.mercadolibre.com.ar/p/MLA123456",
        "tienda_oficial": "Apple Store",
        "envio_gratis": True,
        "cuotas_sin_interes": "12 cuotas sin interés",
    }


@pytest.fixture
def sample_results(sample_item):
    return [sample_item] * 10


@pytest.fixture
def output_json_file(tmp_path, sample_results):
    f = tmp_path / "iphone_16_pro_max.json"
    f.write_text(
        json.dumps(sample_results, ensure_ascii=False), encoding="utf-8"
    )
    return str(f)
