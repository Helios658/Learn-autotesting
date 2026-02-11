from selenium.webdriver.common.by import By

from .base_page import BasePage


class CallPage(BasePage):
    """Page Object для страницы активного звонка."""

    CALL_STATUS = (By.CSS_SELECTOR, "[class*='status'], [class*='connecting']")
    END_CALL_BUTTON = (By.CSS_SELECTOR, "[class*='end-call'], [title*='завершить']")
    MICROPHONE_BUTTON = (
        By.CSS_SELECTOR,
        "[class*='microphone'], button[aria-label*='микрофон']",
    )

    def is_call_active(self):
        """Проверяет, активен ли звонок."""
        try:
            status_element = self.wait_for_element(self.CALL_STATUS)
            status_text = status_element.text.lower()
            return "соединение" in status_text or "звонок" in status_text
        except Exception:
            return False

    def end_call(self):
        """Завершает звонок и возвращает Page Object главной страницы."""
        self.wait_for_clickable(self.END_CALL_BUTTON).click()

        from .main_page import MainPage

        return MainPage(self.driver)