import os, sys, re
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from browser_factory import build_driver

URL = "https://www.mercadolibre.com.ar"
QUERY = "bicicleta rodado 29"
TIMEOUT = 20
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def wait_results(wait):
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "ol.ui-search-layout li.ui-search-layout__item")
    ))


def click_with_scroll(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def apply_condition_nuevo(driver, wait):
    el = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//aside//a[normalize-space()='Nuevo']")
    ))
    click_with_scroll(driver, el)
    wait_results(wait)


def apply_tienda_oficial(driver, wait):
    el = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//aside//a[normalize-space()='Solo tiendas oficiales']")
    ))
    click_with_scroll(driver, el)
    wait_results(wait)


def apply_sort_relevancia(driver, wait):
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



# MAIN
def main():
    browser = sys.argv[1] if len(sys.argv) > 1 else os.getenv("BROWSER", "chrome")
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    driver = build_driver(browser)
    wait = WebDriverWait(driver, TIMEOUT)
    try:
        driver.get(URL)
        box = wait.until(EC.element_to_be_clickable((By.NAME, "as_word")))
        box.send_keys(QUERY, Keys.RETURN)
        wait_results(wait)

        apply_condition_nuevo(driver, wait)
        apply_tienda_oficial(driver, wait)
        apply_sort_relevancia(driver, wait)

        path = SCREENSHOT_DIR / f"{slug(QUERY)}_{browser}.png"
        driver.save_screenshot(str(path))

        items = driver.find_elements(
            By.CSS_SELECTOR,
            "ol.ui-search-layout li.ui-search-layout__item a.poly-component__title"
        )[:5]
        for i, el in enumerate(items, 1):
            print(f"{i}. {el.text.strip()}")
        print(f"Screenshot: {path}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()