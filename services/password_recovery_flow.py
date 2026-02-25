from pages.login_page import LoginPage
from pages.password_recovery_page import PasswordRecoveryPage
from pages.mail_page import MailPage
from pages.new_password_page import NewPasswordPage
from services.password_service import PasswordService
from config import config


class PasswordRecoveryFlow:
    def __init__(self, driver):
        self.driver = driver
        self.login_page = LoginPage(driver)
        self.recovery_page = PasswordRecoveryPage(driver)
        self.mail_page = MailPage(driver)
        self.new_password_page = NewPasswordPage(driver)
        self.password_service = PasswordService()

    def run(self) -> bool:
        # 1. Открываем логин
        self.login_page.open()

        # 2. Переход к восстановлению пароля
        self.driver.locator(
            "[e2e-id='login-page.login-form.recovery-password-link']"
        ).first.click()

        # 3. Запрос восстановления
        self.recovery_page.request_password_recovery(config.USER_EMAIL)

        # 4. Забираем письмо и ссылку
        self.mail_page.login()
        reset_link = self.mail_page.get_password_reset_link(wait_for_email=True)

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