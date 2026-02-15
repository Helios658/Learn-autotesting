from selenium.common.exceptions import TimeoutException
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
            (By.CSS_SELECTOR, "[e2e-id='recovery-password-page.login-input']"),
            (By.CSS_SELECTOR, "[e2e-id*='recovery'][e2e-id*='input']"),
            (By.CSS_SELECTOR, "input[placeholder*='логин']"),
            (By.CSS_SELECTOR, "input[placeholder*='e-mail']"),
            (By.CSS_SELECTOR, "input[placeholder*='email']"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[type='text']"),
        ]
        self.SUBMIT_BUTTON_LOCATORS = [
            (By.CSS_SELECTOR, "[e2e-id='recovery-password-page.button']"),
            (By.CSS_SELECTOR, "[e2e-id*='recovery'][e2e-id*='button']"),
            (By.CSS_SELECTOR, "[e2e-id*='password-recovery'][e2e-id*='button']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//*[self::button or self::a][contains(., 'Получить письмо') or contains(., 'Get email') or contains(., 'Отправить') or contains(., 'Send') or contains(., 'Восстановить') or contains(., 'Recover')]")
        ]

    def _find_first(self, locators, clickable=True):
        condition = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
        for locator in locators:
            try:
                return WebDriverWait(self.driver, 3).until(condition(locator))
            except TimeoutException:
                continue
        raise TimeoutError(f"Не удалось найти элемент по локаторам: {locators}")

    def request_password_recovery(self, email):
        """Запрос восстановления пароля"""
        email_field = self._find_first(self.EMAIL_INPUT_LOCATORS, clickable=False)

        tag = (email_field.tag_name or '').lower()
        if tag not in {'input', 'textarea'}:
            nested = email_field.find_elements(By.CSS_SELECTOR, 'input, textarea')
            if nested:
                email_field = nested[0]

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_field)
        email_field.click()
        email_field.clear()
        email_field.send_keys(email)

        submit_btn = self._find_first(self.SUBMIT_BUTTON_LOCATORS, clickable=True)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        try:
            submit_btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", submit_btn)

        print(f"✅ Запрос восстановления отправлен для: {email}")
        return self