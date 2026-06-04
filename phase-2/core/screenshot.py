import time
from config import SCREENSHOT_DELAY


def capture_screenshot(driver, path):
    time.sleep(SCREENSHOT_DELAY)
    driver.save_screenshot(path)