# pages/base_page.py
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)  # значение по умолчанию

    def _find_first_clickable(self, locators, timeout=3):
        waiter = WebDriverWait(self.driver, timeout)
        for locator in locators:
            try:
                return waiter.until(EC.element_to_be_clickable(locator))
            except TimeoutException:
                continue
        return None

    def _safe_click(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)