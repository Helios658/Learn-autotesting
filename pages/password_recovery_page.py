from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import config


class PasswordRecoveryPage:
    """Page Object для страницы восстановления пароля"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

        self.EMAIL_INPUT_LOCATORS = [
            (By.CSS_SELECTOR, "[e2e-id*='recovery'][e2e-id*='input']"),
            (By.CSS_SELECTOR, "input[placeholder*='логин']"),
            (By.CSS_SELECTOR, "input[placeholder*='e-mail']"),
            (By.CSS_SELECTOR, "input[placeholder*='email']"),
            (By.CSS_SELECTOR, "input[type='email']"),
        ]
        self.SUBMIT_BUTTON_LOCATORS = [
            (By.CSS_SELECTOR, "[e2e-id='recovery-password-page.button']"),
            (By.CSS_SELECTOR, "[e2e-id*='recovery'][e2e-id*='button']"),
            (By.CSS_SELECTOR, "[e2e-id*='password-recovery'][e2e-id*='button']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH,
             "//*[self::button or self::a][contains(., 'Получить письмо') or contains(., 'Get email') or contains(., 'Отправить') or contains(., 'Send') or contains(., 'Восстановить') or contains(., 'Recover')]")
        ]

    def _find_first_clickable(self, locators, timeout=None):
        waiter = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        for locator in locators:
            try:
                return waiter.until(EC.element_to_be_clickable(locator))
            except TimeoutException:
                continue
        raise TimeoutError(f"Не удалось найти кликабельный элемент по локаторам: {locators}")

    def request_password_recovery(self, email):
        """Запрос восстановления пароля"""
        # Ждем и заполняем email
        email_field = self._find_first_clickable(self.EMAIL_INPUT_LOCATORS)
        email_field.clear()
        email_field.send_keys(email)

        submit_btn = self._find_first_clickable(self.SUBMIT_BUTTON_LOCATORS)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        try:
            submit_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", submit_btn)

        print(f"✅ Запрос восстановления отправлен для: {email}")
        return self