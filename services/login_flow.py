from pages.login_page import LoginPage
from config import config
from pages.mail_page import MailPage


class LoginFlow:
    def __init__(self, driver):
        self.driver = driver
        self.login_page = LoginPage(driver)
        self.login_page.open(url=config.LOGIN_2FA_URL)

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

    def login_with_2fa(
        self,
        username: str,
        password: str,
        mail_username: str | None = None,
        mail_password: str | None = None,
        timeout: int | None = None,
    ) -> int:
        timeout = timeout or config.EXPLICIT_WAIT

        # 1. Открываем страницу логина и вводим логин/пароль
        self.login_page.open(url=config.LOGIN_2FA_URL)
        self.login_page.enter_username(username)
        self.login_page.enter_password(password)

        if not self.login_page.is_login_button_enabled():
            raise AssertionError("Кнопка 'Войти' должна быть активна")

        # 2. Нажимаем логин и ждём шаг 2FA на этой же странице
        self.login_page.click_login_button()
        self.login_page.wait_for_2fa_step(timeout=timeout)

        # 3. Открываем почту в НОВОМ окне/вкладке
        mail_browser_page = self.driver.context.new_page()
        mail_page = MailPage(mail_browser_page)

        try:
            mail_page.login(
                username=mail_username or config.MAIL_USERNAME,
                password=mail_password or config.MAIL_PASSWORD,
            )
            code_2fa = mail_page.get_2fa_code_from_email(wait_for_email=True)
        finally:
            mail_browser_page.close()

        # 4. Возвращаемся к исходной странице логина и вводим код
        self.login_page.enter_2fa_code(code_2fa)
        self.login_page.click_login_button_2fa()

        # 5. Проверяем финальный успешный вход
        if self.login_page.wait_for_successful_login(timeout=timeout * 2):
            return 0

        error_code = self.login_page.get_network_error()
        raise AssertionError(
            f"2FA логин неуспешен: URL={self.driver.url}, network_error={error_code}"
        )