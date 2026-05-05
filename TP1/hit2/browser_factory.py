import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def build_driver(name: str = None):
    name = (name or os.getenv("BROWSER", "chrome")).lower()
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    if name == "chrome":
        opts = ChromeOptions()
        if headless: opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1440,900")
        return webdriver.Chrome(options=opts)
    if name == "firefox":
        opts = FirefoxOptions()
        if headless: opts.add_argument("-headless")
        opts.add_argument("--width=1440")
        opts.add_argument("--height=900")
        return webdriver.Firefox(options=opts)
    raise ValueError(f"Browser no soportado: {name}")