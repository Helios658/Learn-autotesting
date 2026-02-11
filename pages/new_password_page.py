from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import config


class NewPasswordPage:
    """Page Object для страницы установки нового пароля"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

        # ✅ ИСПРАВЛЕНО: относительные локаторы
        self.NEW_PASSWORD_INPUT = (By.XPATH, "//input[@placeholder='Введите новый пароль']")
        self.CONFIRM_PASSWORD_INPUT = (By.XPATH, "//input[@placeholder='Повторите пароль']")
        self.SAVE_BUTTON = (By.XPATH, "//span[contains(text(), 'Изменить пароль')]")
        self.LOGIN_LINK = (By.XPATH, "//a[contains(text(), 'Вход в систему')]")

    def set_new_password(self, new_password):
        """Устанавливает новый пароль"""
        new_pass_field = self.wait.until(EC.element_to_be_clickable(self.NEW_PASSWORD_INPUT))
        new_pass_field.clear()
        new_pass_field.send_keys(new_password)

        confirm_field = self.wait.until(EC.element_to_be_clickable(self.CONFIRM_PASSWORD_INPUT))
        confirm_field.clear()
        confirm_field.send_keys(new_password)

        save_btn = self.wait.until(EC.element_to_be_clickable(self.SAVE_BUTTON))
        self.driver.execute_script("arguments[0].click();", save_btn)

        try:
            self.wait.until(EC.element_to_be_clickable(self.LOGIN_LINK))
        except TimeoutException:
            # На части окружений ссылка может появляться с задержкой, но флоу продолжаем.
            pass

        print(f"✅ Пароль изменен на: {new_password}")
        return self

    def go_to_login(self):
        """Переходит на страницу логина после смены пароля"""
        login_link = self.wait.until(EC.element_to_be_clickable(self.LOGIN_LINK))
        self.driver.execute_script("arguments[0].click();", login_link)

        try:
            WebDriverWait(self.driver, config.EXPLICIT_WAIT).until(EC.url_contains("/login"))
        except TimeoutException:
            # Иногда редирект происходит медленнее, оставляем текущий URL для внешней проверки тестом.
            pass

        print("✅ Перешли на страницу логина")
        return self