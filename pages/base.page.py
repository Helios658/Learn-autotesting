from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_for_element(self, locator, timeout=10):
        """Ожидание элемента"""
        return self.wait.until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_clickable(self, locator, timeout=10):
        """Ожидание кликабельности"""
        return self.wait.until(
            EC.element_to_be_clickable(locator)
        )