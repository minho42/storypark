import os
import time
from functools import wraps

from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def timeit(func):
    @wraps(func)
    def closure(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()
        print("<%s> took %0.3fs." % (func.__name__, te - ts))
        return result

    return closure


def get_chromedriver(headless: bool = True) -> object:
    options = webdriver.ChromeOptions()
    prefs = {}
    # prefs = {"profile.managed_default_content_settings.images": 2}
    if headless:
        options.add_argument("headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_experimental_option("prefs", prefs)

    chrome_driver_path = os.environ.get("CHROME_DRIVER_PATH")
    assert chrome_driver_path
    try:
        driver = webdriver.Chrome(chrome_driver_path, options=options)
    except WebDriverException:
        driver = None

    return driver
