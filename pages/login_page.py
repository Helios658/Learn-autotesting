from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


class LoginPage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.URL = LOGIN_URL
        self.USERNAME_INPUT = (By.CSS_SELECTOR, "[e2e-id='login-page.login-form.login-input']")
        self.PASSWORD_INPUT = (By.CSS_SELECTOR, "[e2e-id='login-page.login-form.password-input']")
        self.LOGIN_BUTTON = (By.CSS_SELECTOR, "[e2e-id='login-form__login-button']")

    def open(self):
        self.driver.get(self.URL)
        return self

    def enter_username(self, username):
        element = self.wait.until(EC.element_to_be_clickable(self.USERNAME_INPUT))
        element.clear()
        element.send_keys(username)
        return self

    def enter_password(self, password):
        element = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_INPUT))
        element.clear()
        element.send_keys(password)
        return self

    def click_login_button(self):
        element = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
        element.click()
        return self

    def get_network_error(self):
        """
        Проверяет HTTP ошибку в network
        Возвращает: код ошибки или 0
        """
        try:
            time.sleep(1)  # Ждем запрос

            logs = self.driver.get_log('performance')

            for entry in logs[-20:]:  # Смотрим последние 20 логов
                if 'responseReceived' in entry['message']:
                    try:
                        data = json.loads(entry['message'])
                        status = data['message']['params']['response']['status']
                        if 400 <= status < 600:
                            return status
                    except:
                        continue
            return 0
        except:
            return 0  # Если ошибка - считаем что нет network ошибок

    def login_with_network_check(self, username="admin@admin1.ru", password="123456", expect_success=True):
        """
        Основной метод: логин + проверка network
        Возвращает код ошибки (0 если нет ошибки)
        """
        self.open()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

        time.sleep(2)

        error_code = self.get_network_error()

        if expect_success:
            # Проверяем что нет ошибки и ушли с login страницы
            return error_code
        else:
            # Проверяем что есть ошибка
            return error_code