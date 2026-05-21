from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import logging
from selenium.webdriver.firefox.options import Options as FirefoxOptions

logger = logging.getLogger(__name__)

def build_chrome_options(headless: bool) -> ChromeOptions:
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

    # Anti-detección
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Reducir consumo de memoria para evitar crashes
    options.add_argument("--disable-images")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--js-flags=--max-old-space-size=512")

    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return options

def build_firefox_options(headless: bool) -> FirefoxOptions:
    options = FirefoxOptions()
    if headless:
        options.add_argument("--headless")
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    )
    return options

def build_driver(browser: str, headless: bool) -> webdriver.Remote:
    browser = browser.lower()
    logger.info("Iniciando driver", extra={"event": "driver_init_start", "browser": browser, "headless": headless})
    try:
        if browser == "chrome":
            options = build_chrome_options(headless)
            driver = webdriver.Chrome(options=options)
        elif browser == "firefox":
            options = build_firefox_options(headless)
            driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"browser desconocido: {browser}")
        logger.info("Driver inicializado exitosamente", extra={"event": "driver_init_success", "browser": browser})
        return driver
    except Exception as e:
        logger.error("Error al inicializar el driver", extra={"event": "driver_init_error", "browser": browser, "error": type(e).__name__}, exc_info=True)
        raise
