from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from config import config
from pages.base_page import BasePage


class PasswordRecoveryPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.EMAIL_INPUT_LOCATORS = [
            "[e2e-id='recovery-password-page.login-input']",
            "[e2e-id*='recovery'][e2e-id*='input']",
            "input[placeholder*='логин']",
            "input[placeholder*='e-mail']",
            "input[placeholder*='email']",
            "input[type='email']",
            "input[type='text']",
        ]
        self.SUBMIT_BUTTON_LOCATORS = [
            "[e2e-id='recovery-password-page.button']",
            "[e2e-id*='recovery'][e2e-id*='button']",
            "[e2e-id*='password-recovery'][e2e-id*='button']",
            "[e2e-id*='recovery-password'] button",
            "[e2e-id*='recovery'] button",
            "button[type='submit']",
            "button",
            "xpath=//*[self::button or self::a][contains(., 'Получить письмо') or contains(., 'Get email') or contains(., 'Отправить') or contains(., 'Send') or contains(., 'Восстановить') or contains(., 'Recover')]",
        ]

    def request_password_recovery(self, email):
        email_field = self._find_first_visible(self.EMAIL_INPUT_LOCATORS, timeout=config.EXPLICIT_WAIT * 1000)
        email_field.fill(email)

        try:
            submit_btn = self._find_first_visible(self.SUBMIT_BUTTON_LOCATORS, timeout=3000)
            submit_btn.click()
        except PlaywrightTimeoutError:
            email_field.press("Enter")

        print(f"✅ Запрос восстановления отправлен для: {email}")
        return self