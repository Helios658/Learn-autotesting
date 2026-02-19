from .base_page import BasePage


class CallPage(BasePage):
    CALL_STATUS = "[class*='status'], [class*='connecting']"
    END_CALL_BUTTON = "[class*='end-call'], [title*='завершить']"

    def is_call_active(self):
        if self.page.locator(self.CALL_STATUS).count() == 0:
            return False
        status_text = self.page.locator(self.CALL_STATUS).first.inner_text().lower()
        return "соединение" in status_text or "звонок" in status_text

    def end_call(self):
        self.page.locator(self.END_CALL_BUTTON).first.click()

        from .main_page import MainPage

        return MainPage(self.page)