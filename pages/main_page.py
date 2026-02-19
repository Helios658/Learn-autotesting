from .base_page import BasePage


class MainPage(BasePage):
    CALL_BUTTON = "[e2e-id*='call'], [data-testid*='call']"
    PHONE_INPUT = "input[type='tel'], [placeholder*='номер']"
    START_CALL_BUTTON = "button[type='submit'], [class*='start-call']"

    def start_call(self, phone_number):
        self.page.locator(self.CALL_BUTTON).first.click()
        self.page.locator(self.PHONE_INPUT).first.fill(phone_number)
        self.page.locator(self.START_CALL_BUTTON).first.click()

        from .call_page import CallPage

        return CallPage(self.page)