from config import config


class NewPasswordPage:
    def __init__(self, page):
        self.page = page
        self.NEW_PASSWORD_INPUT = "xpath=//input[@placeholder='Введите новый пароль']"
        self.CONFIRM_PASSWORD_INPUT = "xpath=//input[@placeholder='Повторите пароль']"
        self.SAVE_BUTTON = "xpath=//span[contains(text(), 'Изменить пароль')]"
        self.LOGIN_LINK = "xpath=//a[contains(text(), 'Вход в систему')]"

    def set_new_password(self, new_password):
        self.page.locator(self.NEW_PASSWORD_INPUT).first.fill(new_password)
        self.page.locator(self.CONFIRM_PASSWORD_INPUT).first.fill(new_password)
        self.page.locator(self.SAVE_BUTTON).first.click()
        self.page.wait_for_timeout(1000)

    def go_to_login(self):
        login_link = self.page.locator(self.LOGIN_LINK).first
        if login_link.count() > 0:
            login_link.click()
        self.page.wait_for_url("**/login", timeout=config.EXPLICIT_WAIT * 1000)