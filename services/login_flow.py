from pages.login_page import LoginPage
from config import config


class LoginFlow:
    def __init__(self, driver):
        self.driver = driver
        self.login_page = LoginPage(driver)

    def login(self, username: str, password: str, expect_success: bool = True, timeout: int | None = None) -> int:
        """
        Возвращает network_error_code (0 если успех).
        Для expect_success=True — бросает AssertionError при неуспехе.
        Для expect_success=False — НЕ падает, возвращает код (если был), иначе 0.
        """
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

        # Негативный кейс: ждём чуть-чуть и возвращаем, что поймали
        self.driver.wait_for_timeout(2000)
        return self.login_page.get_network_error()