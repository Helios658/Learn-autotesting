from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from config import config


class MailPage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

        # Локаторы для входа на почту (исправленные)
        self.LOGIN_INPUT = (By.ID, "username")
        self.PASSWORD_INPUT = (By.ID, "password")
        self.SIGNIN_BUTTON = (By.CLASS_NAME, "signinTxt")

        # Локаторы для поиска письма
        self.EMAIL_SUBJECT = (By.XPATH, "//*[contains(text(), 'Восстановление пароля')]")

    def login(self, username=None, password=None):
        username = username or config.MAIL_USERNAME
        password = password or config.MAIL_PASSWORD
        """Вход на почту"""
        self.driver.get(config.MAIL_URL)

        # ✅ ДОБАВЬТЕ ЯВНОЕ ОЖИДАНИЕ загрузки страницы
        self.wait.until(
            EC.presence_of_element_located(self.LOGIN_INPUT)
        )

        print(f"⏳ Страница почты загружена, вводим данные для: {username}")

        # Вводим логин
        username_field = self.wait.until(
            EC.element_to_be_clickable(self.LOGIN_INPUT)
        )
        username_field.send_keys(username)

        # Вводим пароль
        password_field = self.driver.find_element(*self.PASSWORD_INPUT)
        password_field.send_keys(password)

        # Нажимаем войти
        signin_button = self.wait.until(
            EC.element_to_be_clickable(self.SIGNIN_BUTTON)
        )
        signin_button.click()

        # ✅ Ждем успешного входа (появление интерфейса почты)
        try:
            self.wait.until(
                EC.url_contains("/mail/")  # или другой признак успешного входа
            )
            print(f"✅ Успешный вход на почту: {username}")
        except:
            print(f"⚠️ Возможно проблемы со входом, но продолжаем...")

        return self

    def wait_for_recovery_email(self, timeout=60):
        """Ждет письмо с восстановлением пароля"""
        print(f"⏳ Ждем письмо (макс {timeout} сек)...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Обновляем страницу почты
                self.driver.refresh()
                time.sleep(3)

                # Ищем письмо
                if self.driver.find_elements(*self.EMAIL_SUBJECT):
                    print("✅ Письмо найдено!")
                    return True

            except:
                pass

            time.sleep(5)  # Проверяем каждые 5 секунд

        print(f"❌ Письмо не пришло за {timeout} секунд")
        return False

    def get_password_reset_link(self, wait_for_email=True):
        """Получает ссылку восстановления из письма"""

        if wait_for_email:
            # Ждем письмо
            if not self.wait_for_recovery_email():
                raise Exception("Письмо с восстановлением не пришло")

        # Ждем и кликаем на письмо
        email_element = self.wait.until(
            EC.element_to_be_clickable(self.EMAIL_SUBJECT)
        )
        email_element.click()
        time.sleep(3)

        # Ищем ссылку в письме
        page_source = self.driver.page_source
        match = re.search(r'https://gamma\.hi-tech\.org/v2/login/new-password[^\s<>"\']+', page_source)

        if match:
            reset_link = match.group()
            print(f"✅ Нашли ссылку: {reset_link}")
            return reset_link
        else:
            raise Exception("Не нашли ссылку восстановления в письме")