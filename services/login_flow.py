from pages.login_page import LoginPage
from config import config


class LoginFlow:
    def __init__(self, driver):
        self.driver = driver
        self.login_page = LoginPage(driver)

    def login(self, username: str, password: str, expect_success: bool = True, timeout: int | None = None) -> int:
        timeout = timeout or config.EXPLICIT_WAIT

        # Используем твой трекинг ответов, он уже встроен в open()
        self.login_page.open()
        self.login_page.enter_username(username)
        self.login_page.enter_password(password)

        if not self.login_page.is_login_button_enabled():
            raise AssertionError("Кнопка 'Войти' должна быть активна")

        self.login_page.click_login_button()

        if expect_success:
            if self.login_page.wait_for_successful_login(timeout=timeout * 2):
                return 0

            error_code = self.login_page.get_network_error()
            raise AssertionError(
                f"Логин неуспешен: URL={self.driver.url}, network_error={error_code}"
            )

        self.login_page.check_400_error(timeout=timeout)
        return self.login_page.get_network_error()