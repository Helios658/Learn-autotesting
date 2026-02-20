from config import config


class NewPasswordPage:
    def __init__(self, page):
        self.page = page
        self.NEW_PASSWORD_INPUTS = [
            "xpath=//input[@placeholder='Введите новый пароль']",
            "xpath=//input[contains(@placeholder,'нов') and @type='password']",
            "xpath=//label[contains(.,'Новый пароль')]/following::input[@type='password'][1]",
            "input[type='password'][name*='new']",
            "input[type='password'][id*='new']",
            "input[type='password'][autocomplete='new-password']",
            "[e2e-id*='new-password'] input[type='password']",
        ]
        self.CONFIRM_PASSWORD_INPUTS = [
            "xpath=//input[@placeholder='Повторите пароль']",
            "xpath=//input[contains(@placeholder,'Повтор') and @type='password']",
            "xpath=//label[contains(.,'Подтверд')]/following::input[@type='password'][1]",
            "input[type='password'][name*='confirm']",
            "input[type='password'][id*='confirm']",
            "[e2e-id*='confirm'] input[type='password']",
        ]
        self.SAVE_BUTTONS = [
            "xpath=//span[contains(text(), 'Изменить пароль')]/ancestor::button[1]",
            "xpath=//button[.//span[contains(normalize-space(.), 'Изменить пароль')]]",
            "xpath=//button[contains(., 'Изменить пароль') or contains(., 'Сохранить') or contains(., 'Save')]",
            "button[type='submit']",
            "button.iva-button",
            "[e2e-id*='save']",
        ]
        self.LOGIN_LINKS = [
            "xpath=//a[contains(text(), 'Вход в систему')]",
            "xpath=//a[contains(@href, '/login')]",
            "[e2e-id*='login']",
        ]

    def _first_visible_any_context(self, selectors, timeout_ms=None):
        timeout_ms = timeout_ms or config.EXPLICIT_WAIT * 1000
        import time
        deadline = time.time() + (timeout_ms / 1000)

        while time.time() < deadline:
            # default content
            for selector in selectors:
                locator = self.page.locator(selector)
                count = locator.count()
                for i in range(count):
                    candidate = locator.nth(i)
                    try:
                        if candidate.is_visible():
                            return candidate
                    except Exception:
                        continue

            # frames
            for frame in self.page.frames:
                for selector in selectors:
                    locator = frame.locator(selector)
                    try:
                        count = locator.count()
                        for i in range(count):
                            candidate = locator.nth(i)
                            try:
                                if candidate.is_visible():
                                    return candidate
                            except Exception:
                                continue
                    except Exception:
                        continue

            self.page.wait_for_timeout(250)

        raise TimeoutError(f"Не удалось найти элемент по селекторам: {selectors}")

    def _debug_dump(self, suffix="new_password_debug"):
        try:
            self.page.screenshot(path=f"{suffix}.png", full_page=True)
        except Exception:
            pass
        try:
            with open(f"{suffix}.html", "w", encoding="utf-8") as file:
                file.write(self.page.content())
        except Exception:
            pass

    def _find_visible_password_inputs_any_context(self, timeout_ms=None):
        timeout_ms = timeout_ms or config.EXPLICIT_WAIT * 1000
        import time
        deadline = time.time() + (timeout_ms / 1000)

        while time.time() < deadline:
            # default content
            page_passwords = self.page.locator("input[type='password']")
            visible_page_passwords = [
                page_passwords.nth(i)
                for i in range(page_passwords.count())
                if page_passwords.nth(i).is_visible()
            ]
            if len(visible_page_passwords) >= 2:
                return visible_page_passwords[0], visible_page_passwords[1]

            # frames
            for frame in self.page.frames:
                try:
                    frame_passwords = frame.locator("input[type='password']")
                    visible_frame_passwords = [
                        frame_passwords.nth(i)
                        for i in range(frame_passwords.count())
                        if frame_passwords.nth(i).is_visible()
                    ]
                    if len(visible_frame_passwords) >= 2:
                        return visible_frame_passwords[0], visible_frame_passwords[1]
                except Exception:
                    continue

            self.page.wait_for_timeout(250)

        return None, None

    def set_new_password(self, new_password):
        self.page.wait_for_url("**/login/new-password**", timeout=config.EXPLICIT_WAIT * 2000)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1200)

        new_password_input = None
        confirm_password_input = None
        try:
            new_password_input = self._first_visible_any_context(
                self.NEW_PASSWORD_INPUTS,
                timeout_ms=config.EXPLICIT_WAIT * 2000,
            )
            confirm_password_input = self._first_visible_any_context(
                self.CONFIRM_PASSWORD_INPUTS,
                timeout_ms=config.EXPLICIT_WAIT * 2000,
            )
        except Exception:
            pass

        if not new_password_input or not confirm_password_input:
            new_password_input, confirm_password_input = self._find_visible_password_inputs_any_context(
                timeout_ms=config.EXPLICIT_WAIT * 2000,
            )
        if not new_password_input or not confirm_password_input:
            raise TimeoutError("Не удалось найти два видимых password-поля на странице восстановления")

        new_password_input.fill(new_password)
        confirm_password_input.fill(new_password)

        save_button = None
        try:
            save_button = self._first_visible_any_context(self.SAVE_BUTTONS)
        except Exception:
            # fallback: берем первую видимую кнопку с текстом про изменение/сохранение пароля
            buttons = self.page.locator("button")
            for i in range(buttons.count()):
                candidate = buttons.nth(i)
                try:
                    if not candidate.is_visible():
                        continue
                    text = (candidate.inner_text() or "").strip().lower()
                    if any(token in text for token in ("изменить", "сохранить", "save", "парол")):
                        save_button = candidate
                        break
                except Exception:
                    continue
        if save_button is None:
            self._debug_dump("new_password_save_button_not_found")
            # финальный fallback: Enter в поле подтверждения
            try:
                confirm_password_input.press("Enter")
                return
            except Exception:
                raise
        try:
            save_button.click(timeout=5000)
        except Exception:
            try:
                save_button.click(force=True)
            except Exception:
                try:
                    save_button.press("Enter")
                except Exception:
                    self.page.evaluate("el => el.click()", save_button.element_handle())

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