import os, sys, json
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def process_product(driver, wait, query):
    driver.get(URL)
    box = wait.until(EC.element_to_be_clickable((By.NAME, "as_word")))
    box.clear()
    box.send_keys(query, Keys.RETURN)
    wait_results(wait)

    apply_condition_nuevo(driver, wait)
    apply_tienda_oficial(driver, wait)
    apply_sort_relevancia(driver, wait)

    items = driver.find_elements(By.CSS_SELECTOR, selectors.SELECTOR_RESULT_ITEM)[:10]
    results = []
    
    for item in items:
        prod_data = {
            "titulo": extractors.extract_titulo(item),
            "precio": extractors.extract_precio(item),
            "link": extractors.extract_link(item),
            "tienda_oficial": extractors.extract_tienda_oficial(item),
            "envio_gratis": extractors.extract_envio_gratis(item),
            "cuotas_sin_interes": extractors.extract_cuotas(item),
        }
        results.append(prod_data)
        
    return results

def main():
    browser = sys.argv[1] if len(sys.argv) > 1 else os.getenv("BROWSER", "chrome")
    OUTPUT_DIR.mkdir(exist_ok=True)
    driver = build_driver(browser)
    wait = WebDriverWait(driver, TIMEOUT)
    
    try:
        for query, filename in PRODUCT_FILENAMES.items():
            print(f"Procesando: {query}")
            results = process_product(driver, wait, query)
            out_path = OUTPUT_DIR / f"{filename}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Guardado -> {out_path}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
