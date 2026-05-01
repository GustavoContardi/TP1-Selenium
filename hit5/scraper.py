import os
import sys
import json
import logging
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from logging_setup import setup_logging
from retry import with_backoff
from browser_factory import build_driver
import dom_selectors as selectors
import extractors

URL = "https://www.mercadolibre.com.ar"
TIMEOUT = 20
OUTPUT_DIR = Path(__file__).parent / "output"

PRODUCT_FILENAMES = {
    "bicicleta rodado 29": "bicicleta_rodado_29",
    "iPhone 16 Pro Max": "iphone_16_pro_max",
    "GeForce RTX 5090": "geforce_5090",
}

logger = logging.getLogger(__name__)

def wait_results(wait):
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, selectors.SELECTOR_RESULT_ITEM)
    ))

def click_with_scroll(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)

@with_backoff(max_attempts=3, base_delay=2.0)
def load_search_page(driver, wait, query: str) -> None:
    # Intenta cargar la pagina de busqueda y esperar resultados
    driver.get(URL)
    box = wait.until(EC.element_to_be_clickable((By.NAME, "as_word")))
    box.clear()
    box.send_keys(query, Keys.RETURN)
    wait_results(wait)

def apply_condition_nuevo(driver, wait):
    try:
        el = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//aside//a[normalize-space()='Nuevo']")
        ))
        click_with_scroll(driver, el)
        wait_results(wait)
    except Exception:
        pass

def apply_tienda_oficial(driver, wait):
    try:
        el = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//aside//a[normalize-space()='Solo tiendas oficiales']")
        ))
        click_with_scroll(driver, el)
        wait_results(wait)
    except Exception:
        pass

def apply_sort_relevancia(driver, wait):
    try:
        trigger = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.andes-dropdown__trigger")
        ))
        click_with_scroll(driver, trigger)
        opt = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//li[contains(@class,'andes-list__item')]"
             "//*[normalize-space()='Más relevantes']")
        ))
        click_with_scroll(driver, opt)
        wait_results(wait)
    except Exception:
        pass

def extract_all_fields(card, context):
    return {
        "titulo": extractors.extract_titulo(card, context),
        "precio": extractors.extract_precio(card, context),
        "link": extractors.extract_link(card, context),
        "tienda_oficial": extractors.extract_tienda_oficial(card, context),
        "envio_gratis": extractors.extract_envio_gratis(card, context),
        "cuotas_sin_interes": extractors.extract_cuotas(card, context),
    }

def process_product(driver, wait, query, browser):
    logger.info("Inicio de scraping del producto: %s", query)
    
    try:
        load_search_page(driver, wait, query)
    except Exception as e:
        logger.error("Fallo total al cargar búsqueda para %s", query, exc_info=True)
        return []

    apply_condition_nuevo(driver, wait)
    apply_tienda_oficial(driver, wait)
    apply_sort_relevancia(driver, wait)

    items = driver.find_elements(By.CSS_SELECTOR, selectors.SELECTOR_RESULT_ITEM)[:10]
    results = []
    
    for idx, card in enumerate(items):
        context = {"producto": query, "browser": browser, "resultado_index": idx}
        try:
            logger.debug("Procesando resultado %d de %s", idx, query)
            item = extract_all_fields(card, context)
            results.append(item)
        except Exception as e:
            logger.error(
                "Resultado %d descartado por error inesperado | producto=%s | %s",
                idx, query, e, exc_info=True
            )
            continue
            
    if len(results) < 10:
        logger.warning(
            "Se extrajeron %d resultados, pero se esperaban 10 para el producto %s",
            len(results), query
        )
        
    return results

def main():
    setup_logging()
    logger.info("Iniciando scraper")
    
    browser = sys.argv[1] if len(sys.argv) > 1 else os.getenv("BROWSER", "firefox")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    driver = build_driver(browser)
    wait = WebDriverWait(driver, TIMEOUT)
    
    try:
        for query, filename in PRODUCT_FILENAMES.items():
            results = process_product(driver, wait, query, browser)
            if results:
                out_path = OUTPUT_DIR / f"{filename}.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                logger.info("JSON escrito exitosamente -> %s", out_path)
    finally:
        driver.quit()
        logger.info("Scraper finalizado")

if __name__ == "__main__":
    main()
