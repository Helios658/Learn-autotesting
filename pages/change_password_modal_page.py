import time

from config import config
from pages.base_page import BasePage


class ChangePasswordModalPage(BasePage):
    SETTINGS_LINK = "[e2e-id='shared-core.navigation-menu.settings']"
    PROFILE_LINK = "[e2e-id='settings-page.list.profile']"
    CHANGE_PASSWORD_LINK = "[e2e-id='settings-page.profile.cng-pwd-link']"
    OLD_PASSWORD_INPUT = "[e2e-id='settings-page.change-password-modal.old-password-input']"
    NEW_PASSWORD_INPUT = "[e2e-id='settings-page.change-password-modal.new-password-input']"
    CONFIRM_PASSWORD_INPUT = "[e2e-id='settings-page.change-password-modal.new-password-confirm-input']"
    SAVE_PASSWORD_BUTTON = "[e2e-id='settings-page.change-password-modal.save-btn']"
    LOGOUT_LINK = "[e2e-id='settings-page.profile.logout-link']"

    def _locator(self, selector: str):
        return self.page.locator(selector).first

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join((text or "").split()).lower()

    def open_from_profile(self):
        self._locator(self.SETTINGS_LINK).click()
        self._locator(self.PROFILE_LINK).click()
        self._locator(self.CHANGE_PASSWORD_LINK).click()
        self._locator(self.OLD_PASSWORD_INPUT).wait_for(
            state="visible",
            timeout=config.EXPLICIT_WAIT * 1000,
        )
        return self

    def fill_form(self, old_password=None, new_password=None, confirm_password=None):
        old_input = self._locator(self.OLD_PASSWORD_INPUT)
        new_input = self._locator(self.NEW_PASSWORD_INPUT)
        confirm_input = self._locator(self.CONFIRM_PASSWORD_INPUT)

        old_input.fill("")
        new_input.fill("")
        confirm_input.fill("")

        if old_password is not None:
            old_input.fill(old_password)

        if new_password is not None:
            new_input.fill(new_password)

        if confirm_password is not None:
            confirm_input.fill(confirm_password)

        return self

    def save(self):
        self._locator(self.SAVE_PASSWORD_BUTTON).click()
        return self

    def logout_from_profile(self):
        self._locator(self.LOGOUT_LINK).click()
        return self

    def has_any_error_text(self, variants, timeout=5):
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                normalized_body = self._normalize_text(self.page.locator("body").inner_text())
                for text in variants:
                    if self._normalize_text(text) in normalized_body:
                        return True
            except Exception:
                pass

            self.page.wait_for_timeout(250)

        return False

    def assert_any_error_text(self, variants, timeout=5, message=None):
        if self.has_any_error_text(variants, timeout=timeout):
            return self

        try:
            body_excerpt = self.page.locator("body").inner_text()[:2000]
        except Exception:
            body_excerpt = "<не удалось получить body.inner_text()>"

        expected = " | ".join(variants)
        raise AssertionError(message or f"Не нашли ожидаемый текст ошибки: {expected}\n\nФрагмент страницы:\n{body_excerpt}")