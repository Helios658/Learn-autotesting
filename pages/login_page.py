from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    """
    Page Object для страницы логина
    Каждая страница = один класс
    """

    def __init__(self, driver):
        """
        Конструктор принимает driver
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

        # ЛОКАТОРЫ - все селекторы в одном месте
        self.URL = "https://gamma.hi-tech.org/v2/login"
        self.USERNAME_INPUT = (By.CSS_SELECTOR, "[e2e-id='login-page.login-form.login-input']")
        self.PASSWORD_INPUT = (By.CSS_SELECTOR, "[e2e-id='login-page.login-form.password-input']")
        self.LOGIN_BUTTON = (By.CSS_SELECTOR, "[e2e-id='login-form__login-button']")
        self.ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")

    def open(self):
        """
        Открыть страницу логина
        """
        self.driver.get(self.URL)
        return self  # Возвращаем self для цепочки вызовов

    def enter_username(self, username):
        """
        Ввести логин
        """
        element = self.wait.until(
            EC.element_to_be_clickable(self.USERNAME_INPUT)
        )
        element.clear()
        element.send_keys(username)
        return self

    def enter_password(self, password):
        """
        Ввести пароль
        """
        element = self.wait.until(
            EC.element_to_be_clickable(self.PASSWORD_INPUT)
        )
        element.clear()
        element.send_keys(password)
        return self

    def click_login_button(self):
        """
        Нажать кнопку входа
        """
        element = self.wait.until(
            EC.element_to_be_clickable(self.LOGIN_BUTTON)
        )
        element.click()
        return self

    def login(self, username="admin@admin1.ru", password="123456"):
        """
        Полный процесс логина
        Использование: page.login("user", "pass")
        """
        self.open()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

        # Ждем успешного логина (уходим со страницы login)
        self.wait.until(lambda d: "login" not in d.current_url)
        return True

    def get_error_message(self):
        """
        Получить текст сообщения об ошибке
        """
        try:
            element = self.wait.until(
                EC.visibility_of_element_located(self.ERROR_MESSAGE)
            )
            return element.text
        except:
            return None

    def is_on_login_page(self):
        """
        Проверить что находимся на странице логина
        """
        return "login" in self.driver.current_url