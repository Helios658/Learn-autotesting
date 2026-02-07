from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class NewPasswordPage:
    """Page Object для страницы установки нового пароля"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # ✅ ИСПРАВЛЕНО: относительные локаторы
        self.NEW_PASSWORD_INPUT = (By.XPATH, "//input[@placeholder='Введите новый пароль']")
        self.CONFIRM_PASSWORD_INPUT = (By.XPATH, "//input[@placeholder='Повторите пароль']")
        self.SAVE_BUTTON = (By.XPATH, "//span[contains(text(), 'Изменить пароль')]")
        self.LOGIN_LINK = (By.XPATH, "//a[contains(text(), 'Вход в систему')]")

    def set_new_password(self, new_password):
        """Устанавливает новый пароль"""
        time.sleep(2)

        # Вводим новый пароль
        new_pass_field = self.wait.until(
            EC.element_to_be_clickable(self.NEW_PASSWORD_INPUT)
        )
        new_pass_field.send_keys(new_password)

        # Подтверждаем пароль
        confirm_field = self.driver.find_element(*self.CONFIRM_PASSWORD_INPUT)
        confirm_field.send_keys(new_password)

        # Сохраняем
        save_btn = self.driver.find_element(*self.SAVE_BUTTON)
        self.driver.execute_script("arguments[0].click();", save_btn)

        time.sleep(3)
        print(f"✅ Пароль изменен на: {new_password}")
        return self

    def go_to_login(self):
        """Переходит на страницу логина после смены пароля"""
        login_link = self.wait.until(
            EC.element_to_be_clickable(self.LOGIN_LINK)
        )
        self.driver.execute_script("arguments[0].click();", login_link)
        time.sleep(2)
        print("✅ Перешли на страницу логина")
        return self