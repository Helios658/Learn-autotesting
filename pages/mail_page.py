# pages/mail_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time


class MailPage:
    """Page Object для почтового ящика hi-tech.org"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # Локаторы для входа на почту
        self.LOGIN_INPUT = (By.XPATH, "/html/body/form/div/div[2]/div/div[3]/input")
        self.PASSWORD_INPUT = (By.XPATH, "/html/body/form/div/div[2]/div/div[5]/input")
        self.SIGNIN_BUTTON = (By.XPATH, "/html/body/form/div/div[2]/div/div[9]/div/span")

        # Локаторы для поиска письма
        self.EMAIL_SUBJECT = (By.XPATH, "//*[contains(text(), 'Восстановление пароля')]")

    def login(self, username, password):
        """Вход на почту"""
        self.driver.get("https://mail.hi-tech.org")
        time.sleep(2)

        # Вводим логин
        self.driver.find_element(*self.LOGIN_INPUT).send_keys(username)

        # Вводим пароль
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)

        # Нажимаем войти
        self.driver.find_element(*self.SIGNIN_BUTTON).click()

        time.sleep(3)
        print(f"✅ Вошли на почту: {username}")
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