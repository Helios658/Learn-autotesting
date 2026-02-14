from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PasswordRecoveryPage:
    """Page Object для страницы восстановления пароля"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        self.EMAIL_INPUT_LOCATORS = [
            (By.CSS_SELECTOR, "[e2e-id*='recovery'][e2e-id*='input']"),
            (By.CSS_SELECTOR, "input[placeholder*='логин']"),
            (By.CSS_SELECTOR, "input[placeholder*='e-mail']"),
            (By.CSS_SELECTOR, "input[placeholder*='email']"),
            (By.CSS_SELECTOR, "input[type='email']"),
        ]
        self.SUBMIT_BUTTON_LOCATORS = [
            (By.CSS_SELECTOR, "[e2e-id*='recovery'][e2e-id*='button']"),
            (By.XPATH, "//button[contains(., 'Получить письмо') or contains(., 'Get email')]")
        ]

    def _find_first_clickable(self, locators):
        for locator in locators:
            try:
                return self.wait.until(EC.element_to_be_clickable(locator))
            except Exception:
                continue
        raise TimeoutError(f"Не удалось найти кликабельный элемент по локаторам: {locators}")

    def request_password_recovery(self, email):
        """Запрос восстановления пароля"""
        # Ждем и заполняем email
        email_field = self._find_first_clickable(self.EMAIL_INPUT_LOCATORS)
        email_field.clear()
        email_field.send_keys(email)

        submit_btn = self._find_first_clickable(self.SUBMIT_BUTTON_LOCATORS)
        submit_btn.click()

        print(f"✅ Запрос восстановления отправлен для: {email}")
        return self