from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.mercadolibre.com.ar"
QUERY = "bicicleta rodado 29"
TIMEOUT = 15

def main():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, TIMEOUT)
    try:
        driver.get(URL)
        box = wait.until(EC.element_to_be_clickable((By.NAME, "as_word")))
        box.send_keys(QUERY, Keys.RETURN)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "ol.ui-search-layout li.ui-search-layout__item")
        ))
        items = driver.find_elements(
            By.CSS_SELECTOR,
            "ol.ui-search-layout li.ui-search-layout__item h3.poly-component__title-wrapper a, "
            "ol.ui-search-layout li.ui-search-layout__item a.poly-component__title"
        )[:5]
        for i, el in enumerate(items, 1):
            print(f"{i}. {el.text.strip()}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()