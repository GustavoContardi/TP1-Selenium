import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.mercadolibre.com.ar"
QUERY = "bicicleta rodado 29"
TIMEOUT = 15

# Configuración del sistema de logs
logging.basicConfig(
    level=logging.INFO, # Nivel mínimo de log (INFO, WARNING, ERROR, DEBUG)
    format='%(asctime)s [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Iniciando el scraper...")
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, TIMEOUT)
    try:
        logger.info(f"Navegando a la URL: {URL}")
        driver.get(URL)
        
        logger.info(f"Ingresando búsqueda: '{QUERY}'")
        box = wait.until(EC.element_to_be_clickable((By.NAME, "as_word")))
        box.send_keys(QUERY, Keys.RETURN)
        
        logger.info("Esperando que carguen los resultados...")
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "ol.ui-search-layout li.ui-search-layout__item")
        ))
        
        logger.info("Extrayendo los primeros 5 resultados...")
        items = driver.find_elements(
            By.CSS_SELECTOR,
            "ol.ui-search-layout li.ui-search-layout__item h3.poly-component__title-wrapper a, "
            "ol.ui-search-layout li.ui-search-layout__item a.poly-component__title"
        )[:5]
        
        if not items:
            logger.warning("No se encontraron resultados para la búsqueda.")
        else:
            for i, el in enumerate(items, 1):
                logger.info(f"Resultado {i}: {el.text.strip()}")
                
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado durante el scraping: {e}", exc_info=True)
    finally:
        logger.info("Cerrando el navegador...")
        driver.quit()
        logger.info("Scraper finalizado exitosamente.")

if __name__ == "__main__":
    main()