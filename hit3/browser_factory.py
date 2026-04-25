import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def build_driver(name=None):
    name = (name or os.getenv("BROWSER", "chrome")).lower()
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    if name == "chrome":
        opts = ChromeOptions()
        if headless: opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        opts.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )
        driver = webdriver.Chrome(options=opts)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
        )
        return driver
    if name == "firefox":
        opts = FirefoxOptions()
        if headless: opts.add_argument("-headless")
        opts.add_argument("--width=1440")
        opts.add_argument("--height=900")
        opts.set_preference("dom.webdriver.enabled", False)
        opts.set_preference("useAutomationExtension", False)
        return webdriver.Firefox(options=opts)
    raise ValueError(f"Browser no soportado: {name}")