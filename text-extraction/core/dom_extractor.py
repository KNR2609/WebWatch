import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


CHROME_DRIVER_PATH = None


def set_chrome_driver_path(path):
    global CHROME_DRIVER_PATH
    CHROME_DRIVER_PATH = path


def create_driver():
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    service = Service(CHROME_DRIVER_PATH)

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        }
    )

    driver.set_page_load_timeout(40)

    return driver


def human_like_scroll(driver):
    total_height = driver.execute_script(
        "return document.body.scrollHeight"
    )

    current_position = 0

    while current_position < total_height:

        step = random.randint(700, 1200)

        driver.execute_script(
            f"window.scrollBy(0, {step});"
        )

        current_position += step

        # Reduced delay
        time.sleep(0.1)

        new_height = driver.execute_script(
            "return document.body.scrollHeight"
        )

        if new_height > total_height:
            total_height = new_height

    driver.execute_script("window.scrollTo(0, 0);")

    time.sleep(0.3)


def extract_visible_text_from_dom(url):

    driver = None

    try:
        driver = create_driver()

        driver.get(url)

        # Reduced page wait time
        time.sleep(2)

        human_like_scroll(driver)

        raw_text = driver.execute_script("""
            return document.body.innerText;
        """)

        return raw_text.strip()

    except Exception as e:
        print(f"Extraction failed for {url}")
        print(e)

        return ""

    finally:
        if driver:
            driver.quit()