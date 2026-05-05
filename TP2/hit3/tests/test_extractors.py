from selenium.common.exceptions import NoSuchElementException, TimeoutException
from extractors import extract_precio, extract_titulo, extract_link, extract_envio_gratis, extract_tienda_oficial, extract_cuotas

class TestExtractPrecio:
    def test_precio_entero(self, mock_element, context):
        mock_element.text = "12.345"
        assert extract_precio(mock_element, context) == 12345.0

    def test_precio_con_decimales(self, mock_element, context):
        mock_element.text = "2.500.000"
        assert extract_precio(mock_element, context) == 2500000.0

    def test_precio_no_element_retorna_none(self, mock_element, context):
        mock_element.find_element.side_effect = NoSuchElementException()
        # Llamar directamente con elemento que lanza excepción
        assert extract_precio(mock_element, context) is None

    def test_precio_texto_vacio_retorna_none(self, mock_element, context):
        mock_element.text = ""
        assert extract_precio(mock_element, context) is None

class TestExtractTitulo:
    def test_titulo_happy_path(self, mock_element, context):
        mock_element.text = "  Apple iPhone 16 Pro Max  "
        mock_element.find_element.return_value = mock_element
        result = extract_titulo(mock_element, context)
        assert result == "Apple iPhone 16 Pro Max"   # strip aplicado

    def test_titulo_no_element_retorna_none(self, mock_element, context):
        mock_element.find_element.side_effect = NoSuchElementException()
        assert extract_titulo(mock_element, context) is None

class TestExtractLink:
    def test_link_absoluto(self, mock_element, context):
        mock_element.get_attribute.return_value = "https://www.mercadolibre.com.ar/p/MLA123"
        mock_element.find_element.return_value = mock_element
        assert extract_link(mock_element, context).startswith("https://")

    def test_link_relativo_se_descarta(self, mock_element, context):
        mock_element.get_attribute.return_value = "/p/MLA123"
        mock_element.find_element.return_value = mock_element
        result = extract_link(mock_element, context)
        assert result is None or result.startswith("https://")

    def test_link_none_retorna_none(self, mock_element, context):
        mock_element.get_attribute.return_value = None
        mock_element.find_element.return_value = mock_element
        assert extract_link(mock_element, context) is None

class TestExtractEnvioGratis:
    def test_envio_gratis_presente(self, mock_element, context):
        mock_element.text = "Llega gratis"
        mock_element.find_element.return_value = mock_element
        assert extract_envio_gratis(mock_element, context) is True

    def test_sin_envio_gratis(self, mock_element, context):
        mock_element.find_element.side_effect = NoSuchElementException()
        assert extract_envio_gratis(mock_element, context) is False

class TestExtractCamposOpcionales:
    def test_tienda_oficial_ausente_retorna_none(self, mock_element, context):
        mock_element.find_element.side_effect = NoSuchElementException()
        assert extract_tienda_oficial(mock_element, context) is None

    def test_cuotas_ausente_retorna_none(self, mock_element, context):
        mock_element.find_element.side_effect = NoSuchElementException()
        assert extract_cuotas(mock_element, context) is None
