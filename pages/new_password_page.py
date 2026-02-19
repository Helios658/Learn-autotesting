from config import config


class NewPasswordPage:
    def __init__(self, page):
        self.page = page
        self.NEW_PASSWORD_INPUTS = [
            "xpath=//input[@placeholder='Введите новый пароль']",
            "xpath=//input[contains(@placeholder,'нов') and @type='password']",
            "input[type='password'][name*='new']",
            "input[type='password'][autocomplete='new-password']",
            "[e2e-id*='new-password'] input[type='password']",
        ]
        self.CONFIRM_PASSWORD_INPUTS = [
            "xpath=//input[@placeholder='Повторите пароль']",
            "xpath=//input[contains(@placeholder,'Повтор') and @type='password']",
            "input[type='password'][name*='confirm']",
            "[e2e-id*='confirm'] input[type='password']",
        ]
        self.SAVE_BUTTONS = [
            "xpath=//span[contains(text(), 'Изменить пароль')]/ancestor::button[1]",
            "xpath=//button[contains(., 'Изменить пароль') or contains(., 'Сохранить') or contains(., 'Save')]",
            "button[type='submit']",
        ]
        self.LOGIN_LINKS = [
            "xpath=//a[contains(text(), 'Вход в систему')]",
            "xpath=//a[contains(@href, '/login')]",
            "[e2e-id*='login']",
        ]

    def _first_visible(self, selectors, timeout_ms=None):
        timeout_ms = timeout_ms or config.EXPLICIT_WAIT * 1000
        for selector in selectors:
            locator = self.page.locator(selector).first
            try:
                locator.wait_for(state="visible", timeout=timeout_ms)
                return locator
            except Exception:
                continue
        raise TimeoutError(f"Не удалось найти элемент по селекторам: {selectors}")

    def set_new_password(self, new_password):
        new_password_input = self._first_visible(self.NEW_PASSWORD_INPUTS)
        confirm_password_input = self._first_visible(self.CONFIRM_PASSWORD_INPUTS)

        new_password_input.fill(new_password)
        confirm_password_input.fill(new_password)

        save_button = self._first_visible(self.SAVE_BUTTONS)
        try:
            save_button.click(timeout=5000)
        except Exception:
            save_button.click(force=True)

        self.page.wait_for_timeout(1000)

    def go_to_login(self):
        for selector in self.LOGIN_LINKS:
            link = self.page.locator(selector).first
            if link.count() > 0:
                try:
                    link.click(timeout=2000)
                    break
                except Exception:
                    try:
                        link.click(force=True)
                        break
                    except Exception:
                        continue

        self.page.wait_for_url("**/login", timeout=config.EXPLICIT_WAIT * 1000)