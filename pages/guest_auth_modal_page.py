import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

class GuestAuthModalPage():
    USERNAME_INPUT_LOCATORS = "[e2e-id='login-page.login-form.login-input']"
    PASSWORD_INPUT_LOCATORS = "[e2e-id='login-page.login-form.password-input']"
    LOGIN_BUTTON_LOCATORS = "[e2e-id='login-form__login-button']"

    def __init__(self, page):
        self.page = page

    def _find_visible(self, selectors, timeout_ms: int = 10_000):
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            for selector in selectors:
                try:
                    locator = self.page.locator(selector)
                    if locator.count() > 0 and locator.first.is_visible():
                        return locator.first
                except PlaywrightError:
                    pass

                for frame in self.page.frames:
                    try:
                        frame_locator = frame.locator(selector)
                        if frame_locator.count() > 0 and frame_locator.first.is_visible():
                            return frame_locator.first
                    except PlaywrightError:
                        continue

            self.page.wait_for_timeout(200)

        raise AssertionError(f"Не найден видимый элемент по локаторам: {selectors}")

    def wait_opened(self):
        self._find_visible(self.USERNAME_INPUT_LOCATORS, timeout_ms=12_000)
        self._find_visible(self.PASSWORD_INPUT_LOCATORS, timeout_ms=12_000)
        return self

    def login(self, username: str, password: str):
        username_input = self._find_visible(self.USERNAME_INPUT_LOCATORS, timeout_ms=12_000)
        username_input.fill(username)

        password_input = self._find_visible(self.PASSWORD_INPUT_LOCATORS, timeout_ms=12_000)
        password_input.fill(password)

        self._find_visible(self.LOGIN_BUTTON_LOCATORS, timeout_ms=8_000).click()
        return self