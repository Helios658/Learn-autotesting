from pages.login_page import LoginPage
from pages.password_recovery_page import PasswordRecoveryPage
from pages.mail_page import MailPage
from pages.new_password_page import NewPasswordPage
from services.password_service import PasswordService
from config import config


class PasswordRecoveryFlow:
    def __init__(self, driver, mail_page: MailPage | None = None):
        self.driver = driver
        self.login_page = LoginPage(driver)
        self.recovery_page = PasswordRecoveryPage(driver)
        self.new_password_page = NewPasswordPage(driver)
        self.password_service = PasswordService()
        # Обратная совместимость: параметр принимаем, но для recovery всегда
        # используем свежую вкладку почты после отправки запроса.
        self._mail_page_compat = mail_page

    def run(self) -> bool:
        # 1. Открываем логин
        self.login_page.open()

        # 2. Переход к восстановлению пароля
        self.login_page.go_to_password_recovery()

        # 3. Запрос восстановления
        self.recovery_page.request_password_recovery(config.USER_EMAIL)

        # 4. Забираем письмо и ссылку через IMAP (UI почты не используется).
        mail_page = MailPage()
        mail_page.login()
        reset_link = mail_page.get_password_reset_link(wait_for_email=True)

        # 5. Переход по ссылке
        self.driver.goto(reset_link)

        # 6. Генерация и установка нового пароля
        new_password = self.password_service.generate_and_persist_password()
        self.new_password_page.set_new_password(new_password)
        self.new_password_page.go_to_login()

        # 7. Логин с новым паролем
        self.login_page.enter_username(config.USER_EMAIL)
        self.login_page.enter_password(new_password)
        self.login_page.click_login_button()

        return self.login_page.wait_for_successful_login(timeout=config.EXPLICIT_WAIT * 2)