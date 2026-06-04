from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import VIEWPORT_WIDTH, VIEWPORT_HEIGHT, PAGE_LOAD_TIMEOUT


def get_browser():
    options = Options()

    options.add_argument("--headless")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    options.page_load_strategy = "eager"

    prefs = {
        "profile.managed_default_content_settings.images": 2
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    return driver