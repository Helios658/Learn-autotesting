from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class NewPasswordPage:
    """Page Object для страницы установки нового пароля"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # Локаторы
        self.NEW_PASSWORD_INPUT = (By.XPATH,
                                   "/html/body/app-root/div/div/app-new-password/app-login-wrapper/section/div/div/div[1]/div[1]/app-input-password-with-validation/div/label/div/input")
        self.CONFIRM_PASSWORD_INPUT = (By.XPATH,
                                       "/html/body/app-root/div/div/app-new-password/app-login-wrapper/section/div/div/div[1]/div[2]/app-input-password/div/label/div/input")
        self.SAVE_BUTTON = (By.XPATH,
                            "/html/body/app-root/div/div/app-new-password/app-login-wrapper/section/div/div/div[2]/button/span[2]")
        self.LOGIN_LINK = (By.XPATH,
                           "/html/body/app-root/div/div/app-new-password/app-password-successfully-changed/app-login-wrapper/section/div/div/a")

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

        # Сохраняем - ИСПОЛЬЗУЕМ JavaScript клик для headless режима
        save_btn = self.driver.find_element(*self.SAVE_BUTTON)

        # Способ 1: JavaScript клик (работает в headless)
        self.driver.execute_script("arguments[0].click();", save_btn)

        # ИЛИ Способ 2: Обычный клик с проверкой видимости
        # if save_btn.is_displayed() and save_btn.is_enabled():
        #     save_btn.click()
        # else:
        #     self.driver.execute_script("arguments[0].click();", save_btn)

        time.sleep(3)
        print(f"✅ Пароль изменен на: {new_password}")
        return self

    def go_to_login(self):
        """Переходит на страницу логина после смены пароля"""
        login_link = self.wait.until(
            EC.element_to_be_clickable(self.LOGIN_LINK)
        )
        # Используем JavaScript клик для надежности
        self.driver.execute_script("arguments[0].click();", login_link)
        time.sleep(2)
        print("✅ Перешли на страницу логина")
        return self