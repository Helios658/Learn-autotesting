# login_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from config import config


class LoginPage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.EXPLICIT_WAIT)
        self.URL = config.LOGIN_URL
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

    def get_entered_username(self):
        element = self.wait.until(EC.presence_of_element_located(self.USERNAME_INPUT))
        return element.get_attribute("value")

    def get_entered_password(self):
        element = self.wait.until(EC.presence_of_element_located(self.PASSWORD_INPUT))
        return element.get_attribute("value")

    def is_login_button_enabled(self):
        element = self.wait.until(EC.presence_of_element_located(self.LOGIN_BUTTON))
        return element.is_enabled()

    def wait_for_successful_login(self, timeout=None):
        """
        Ожидает успешный вход: исчезновение кнопки логина
        или уход со страницы /login.
        Возвращает True при успехе, иначе False.
        """
        timeout = timeout or config.EXPLICIT_WAIT
        waiter = WebDriverWait(self.driver, timeout)

        try:
            waiter.until(
                lambda d: ('/login' not in d.current_url.lower())
                or EC.invisibility_of_element_located(self.LOGIN_BUTTON)(d)
            )
            return True
        except Exception:
            return False

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
            wait_for_logs = WebDriverWait(self.driver, 3)

            logs = []
            start_time = time.time()
            while time.time() - start_time < 3:
                logs = self.driver.get_log('performance')
                if logs:
                    break

            for entry in logs[-20:]:
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
            return 0

    def login_with_network_check(self, username=None, password=None, expect_success=True):
        """
        Основной метод: логин + проверка network
        Возвращает код ошибки (0 если нет ошибки)
        """
        username = username or config.ADMIN_EMAIL
        password = password or config.ADMIN_PASSWORD

        self.open()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

        error_code = 0
        if expect_success:
            try:
                self.wait.until(
                    EC.invisibility_of_element_located(self.LOGIN_BUTTON)
                )
                print("✅ Успешный вход, ожидание завершено.")
            except Exception as e:
                print(f"⚠️ Не дождались успешного входа: {e}")
                error_code = self.get_network_error()
            else:
                error_code = self.get_network_error()
            return error_code
        else:
            # Для случая когда НЕ ожидаем успешного входа
            time.sleep(2)
            error_code = self.get_network_error()
            return error_code

    def check_400_error(self):
        """
        Ищет ошибку 400 в network логах
        Возвращает True если найдена ошибка 400
        """
        import time
        import json
        import re

        # Ждем выполнения запроса
        time.sleep(3)

        # Получаем логи performance
        try:
            logs = self.driver.get_log('performance')
        except:
            return False

        # Ищем ошибку 400
        for entry in logs[-50:]:  # Проверяем последние 50 записей
            message = entry.get('message', '')

            # Простой поиск через регулярные выражения
            if re.search(r'"status"\s*:\s*400\b', message) or '400 Bad Request' in message:
                print("✅ Найдена ошибка 400 в network логах")
                return True

            # Пробуем распарсить JSON
            try:
                data = json.loads(message)
                # Проверяем разные форматы логов
                status = None

                if 'message' in data and 'params' in data['message']:
                    params = data['message']['params']
                    if 'response' in params:
                        status = params['response'].get('status')

                if status == 400:
                    print("✅ Найдена ошибка 400 (JSON парсинг)")
                    return True

            except json.JSONDecodeError:
                continue
            except Exception:
                continue

        print("⚠️ Ошибка 400 не найдена в логах")
        return False