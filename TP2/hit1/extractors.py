import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import dom_selectors as selectors

logger = logging.getLogger(__name__)

def extract_titulo(element, context: dict):
    try:
        try:
            return element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_TITULO).text.strip()
        except NoSuchElementException:
            return element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_LINK).text.strip()
    except Exception as e:
        logger.warning(
            "event=field_extraction_error | field='titulo' | producto='%s' | browser='%s' | error='%s'",
            context.get("producto"), context.get("browser"), type(e).__name__
        )
        return None

def extract_precio(element, context: dict):
    try:
        precio_str = element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_PRECIO).text
        precio_str = precio_str.replace(".", "").replace(",", ".")
        return float(precio_str)
    except Exception as e:
        logger.warning(
            "event=field_extraction_error | field='precio' | producto='%s' | browser='%s' | error='%s'",
            context.get("producto"), context.get("browser"), type(e).__name__
        )
        return None

def extract_link(element, context: dict):
    try:
        url = element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_LINK).get_attribute("href")
        if not url or not url.startswith("http"):
            return None
        return url
    except Exception as e:
        logger.warning(
            "event=field_extraction_error | field='link' | producto='%s' | browser='%s' | error='%s'",
            context.get("producto"), context.get("browser"), type(e).__name__
        )
        return None

def extract_tienda_oficial(element, context: dict):
    try:
        text = element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_TIENDA_OFICIAL).text.strip()
        if text.lower().startswith("por "):
            return text[4:] or None
        return text or None
    except Exception as e:
        logger.warning(
            "event=field_missing | field='tienda_oficial' | producto='%s' | browser='%s' | error='%s'",
            context.get("producto"), context.get("browser"), type(e).__name__
        )
        return None

def extract_envio_gratis(element, context: dict):
    try:
        element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_ENVIO_GRATIS)
        return True
    except Exception as e:
        # Envio gratis es usualmente False si no esta, no lo tratamos como error pero devolvemos False
        # Igual dejamos un debug log por si acaso, pero warning capaz es mucho, aunque el prompt
        # dice "Cada función en extractors.py debe cumplir este contrato explicito: [...] loggear en nivel WARNING"
        # Así que loggeamos warning.
        logger.warning(
            "event=field_missing | field='envio_gratis' | producto='%s' | browser='%s' | error='%s'",
            context.get("producto"), context.get("browser"), type(e).__name__
        )
        return False

def extract_cuotas(element, context: dict):
    try:
        return element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_CUOTAS).text.strip() or None
    except Exception as e:
        logger.warning(
            "event=field_missing | field='cuotas_sin_interes' | producto='%s' | browser='%s' | error='%s'",
            context.get("producto"), context.get("browser"), type(e).__name__
        )
        return None
