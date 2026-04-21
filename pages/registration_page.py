import re
import time
from playwright.sync_api import Error as PlaywrightError


class RegistrationPage:
    EMAIL_INPUT_LOCATORS = [
        "input[type='email']",
        "input[placeholder*='email' i]",
        "input[name='email']",
    ]

    REGISTER_BUTTON_LOCATORS = [
        "[e2e-id='conference-registration__register-button']",
        "button[e2e-id='conference-registration__register-button']",
        "button:has-text('Зарегистрироваться')",
    ]

    REGISTER_MODAL_LOCATORS = [
        ".register-form",
        "app-self-registration",
        ".iva-core-modal-window",
    ]

    REGISTER_MODAL_SUBMIT_LOCATORS = [
        "button.register-form__submit-button",
        "button:has-text('Зарегистрироваться')",
    ]

    SUCCESS_INDICATORS = [
        ".conference-session",
        "[ivamover='conference-session-pip']",
        "video",
        "[e2e-id*='conference']",
    ]

    NAME_INPUT_LOCATORS = [
        "input[placeholder='Введите ваше имя']",
        "input[placeholder*='имя' i]",
        "input[maxlength='255'][type='text']",
    ]

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

    def enter_email(self, email: str):
        self._find_visible(self.EMAIL_INPUT_LOCATORS, timeout_ms=12_000).fill(email)

    def enter_name(self, name: str):
        self._find_visible(self.NAME_INPUT_LOCATORS, timeout_ms=12_000).fill(name)

    def click_register_after_name(self):
        register_btn = None
        for modal_selector in self.REGISTER_MODAL_LOCATORS:
            try:
                modal = self.page.locator(modal_selector).first
                if modal.count() == 0 or not modal.is_visible():
                    continue

                for btn_selector in self.REGISTER_MODAL_SUBMIT_LOCATORS:
                    btn = modal.locator(btn_selector).first
                    if btn.count() > 0 and btn.is_visible():
                        register_btn = btn
                        break
                if register_btn is not None:
                    break
            except PlaywrightError:
                continue

        if register_btn is None:
            register_btn = self._find_visible(self.REGISTER_MODAL_SUBMIT_LOCATORS, timeout_ms=10_000)

        deadline = time.time() + 8
        while time.time() < deadline:
            try:
                if register_btn.is_enabled():
                    break
            except PlaywrightError:
                pass
            self.page.wait_for_timeout(250)

        register_btn.click()

    def complete_name_step(self, name: str = "Auto User"):
        self.enter_name(name)
        self.click_register_after_name()

    def click_register(self):
        self._find_visible(self.REGISTER_BUTTON_LOCATORS, timeout_ms=10_000).click()

    def click_register_if_visible(self, timeout_ms: int = 7_000) -> bool:
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            for selector in self.REGISTER_BUTTON_LOCATORS:
                try:
                    btn = self.page.locator(selector).first
                    if btn.count() == 0 or not btn.is_visible():
                        continue
                    if btn.is_enabled():
                        btn.click()
                        return True
                except PlaywrightError:
                    continue
            self.page.wait_for_timeout(200)
        return False

    def is_registration_completed(self, timeout_ms: int = 15_000) -> bool:
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            current_url = self.page.url or ""
            if "/v2/iva/home/conferences" in current_url and "conferenceSessionId=" in current_url:
                return True

            for selector in self.SUCCESS_INDICATORS:
                try:
                    locator = self.page.locator(selector)
                    if locator.count() > 0 and locator.first.is_visible():
                        return True
                except PlaywrightError:
                    pass

            self.page.wait_for_timeout(250)

        return False

    def wait_until_event_starts_and_enter(self, timeout_ms: int = 90_000) -> bool:
        deadline = time.time() + timeout_ms / 1000

        while time.time() < deadline:
            current_url = self.page.url or ""

            if "/v2/iva/home/conferences" in current_url and "conferenceSessionId=" in current_url:
                return True

            try:
                register_btn = self.page.locator("[e2e-id='conference-registration__register-button']").first
                if register_btn.count() > 0 and register_btn.is_visible():
                    try:
                        register_btn.click(force=True)
                    except PlaywrightError:
                        pass
            except PlaywrightError:
                pass

            try:
                self.page.reload(wait_until="domcontentloaded")
            except PlaywrightError:
                pass

            if self.is_registration_completed(timeout_ms=3000):
                return True

            self.page.wait_for_timeout(3000)

        return False