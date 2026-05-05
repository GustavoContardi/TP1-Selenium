from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import dom_selectors as selectors

def extract_titulo(element):
    try:
        try:
            return element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_TITULO).text.strip()
        except NoSuchElementException:
            return element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_LINK).text.strip()
    except Exception:
        return None

def extract_precio(element):
    try:
        precio_str = element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_PRECIO).text
        precio_str = precio_str.replace(".", "").replace(",", ".")
        return float(precio_str)
    except Exception:
        return None

def extract_link(element):
    try:
        return element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_LINK).get_attribute("href")
    except Exception:
        return None

def extract_tienda_oficial(element):
    try:
        text = element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_TIENDA_OFICIAL).text.strip()
        if text.lower().startswith("por "):
            return text[4:]
        return text
    except Exception:
        return None

def extract_envio_gratis(element):
    try:
        # Si encuentra el elemento, asumimos que tiene envío gratis
        element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_ENVIO_GRATIS)
        return True
    except Exception:
        return False

def extract_cuotas(element):
    try:
        return element.find_element(By.CSS_SELECTOR, selectors.SELECTOR_CUOTAS).text.strip()
    except Exception:
        return None
