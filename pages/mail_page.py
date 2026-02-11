from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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
        """Вход на почту."""
        username = username or config.MAIL_USERNAME
        password = password or config.MAIL_PASSWORD

        self.driver.get(config.MAIL_URL)

        self.wait.until(EC.presence_of_element_located(self.LOGIN_INPUT))

        print(f"⏳ Страница почты загружена, вводим данные для: {username}")

        username_field = self.wait.until(EC.element_to_be_clickable(self.LOGIN_INPUT))
        username_field.send_keys(username)

        password_field = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_INPUT))
        password_field.send_keys(password)

        signin_button = self.wait.until(EC.element_to_be_clickable(self.SIGNIN_BUTTON))
        signin_button.click()

        try:
            self.wait.until(EC.url_contains("/mail/"))
            print(f"✅ Успешный вход на почту: {username}")
        except TimeoutException:
            print("⚠️ Возможно проблемы со входом, но продолжаем...")

        return self

    def wait_for_recovery_email(self, timeout=60):
        """Ждет письмо с восстановлением пароля."""
        print(f"⏳ Ждем письмо (макс {timeout} сек)...")

        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                self.driver.refresh()
                remaining = max(1, int(deadline - time.time()))
                wait_timeout = min(7, remaining)

                WebDriverWait(self.driver, wait_timeout).until(
                    EC.presence_of_element_located(self.EMAIL_SUBJECT)
                )
                print("✅ Письмо найдено!")
                return True
            except TimeoutException:
                continue
            except WebDriverException:
                continue

        print(f"❌ Письмо не пришло за {timeout} секунд")
        return False

    def get_password_reset_link(self, wait_for_email=True):
        """Получает ссылку восстановления из письма."""

        if wait_for_email and not self.wait_for_recovery_email():
            raise Exception("Письмо с восстановлением не пришло")

        email_element = self.wait.until(EC.element_to_be_clickable(self.EMAIL_SUBJECT))
        email_element.click()

        try:
            WebDriverWait(self.driver, config.EXPLICIT_WAIT).until(
                lambda d: re.search(
                    r'https://gamma\.hi-tech\.org/v2/login/new-password[^\s<>"\']+',
                    d.page_source,
                )
                is not None
            )
        except TimeoutException as exc:
            raise Exception("Не нашли ссылку восстановления в письме") from exc

        page_source = self.driver.page_source
        match = re.search(r'https://gamma\.hi-tech\.org/v2/login/new-password[^\s<>"\']+', page_source)

        if match:
            reset_link = match.group()
            print(f"✅ Нашли ссылку: {reset_link}")
            return reset_link

        raise Exception("Не нашли ссылку восстановления в письме")