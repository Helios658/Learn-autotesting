from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PasswordRecoveryPage:
    """Page Object для страницы восстановления пароля"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # ✅ ИСПРАВЛЕНО: относительные локаторы
        self.EMAIL_INPUT = (By.XPATH, "//input[@placeholder='Введите логин или е-mail']")
        self.SUBMIT_BUTTON = (By.XPATH, "//span[contains(text(), 'Получить письмо')]")

    def request_password_recovery(self, email):
        """Запрос восстановления пароля"""
        # Ждем и заполняем email
        email_field = self.wait.until(
            EC.element_to_be_clickable(self.EMAIL_INPUT)
        )
        email_field.clear()
        email_field.send_keys(email)

        # Находим кнопку по span тексту
        submit_btn = self.driver.find_element(*self.SUBMIT_BUTTON)
        submit_btn.click()

        print(f"✅ Запрос восстановления отправлен для: {email}")
        return self