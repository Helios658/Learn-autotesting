import re
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from config import config
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.URL = config.LOGIN_URL
        self.USERNAME_INPUT = "[e2e-id='login-page.login-form.login-input']"
        self.PASSWORD_INPUT = "[e2e-id='login-page.login-form.password-input']"
        self.LOGIN_BUTTON = "[e2e-id='login-form__login-button']"
        self.SHOW_ALL_INPUT_LOCATORS = [
            "[e2e-id='login-page.login-form.show-more-providers-link']",
            "xpath=//a[contains(normalize-space(.), 'Показать все') or contains(normalize-space(.), 'Show all')]",
            "xpath=//*[self::a or self::button][contains(@e2e-id, 'show') and contains(@e2e-id, 'provider')]",
            "[e2e-id*='show-all'], [data-testid*='show-all']",
        ]
        self.ADFS_LINK_LOCATORS = [
            "app-auth-providers-list-modal a.pseudo-link:has-text('ADFS(login+password)')",
            "app-auth-providers-list-modal a.pseudo-link:has-text('Войти через ADFS')",
            "app-auth-provider a.pseudo-link:has-text('ADFS')",
            "[e2e-id*='adfs']",
            "xpath=//*[self::a or self::button][contains(translate(normalize-space(.), 'adfs', 'ADFS'), 'ADFS')]",
        ]
        self.USERNAME_INPUT_ADFS_LOCATORS = [
            "#userNameInput",
            "input[name='UserName']",
            "input[type='email']",
            "input[name='loginfmt']",
            "#i0116",
        ]
        self.PASSWORD_INPUT_ADFS_LOCATORS = [
            "#passwordInput",
            "input[name='Password']",
            "input[type='password']",
            "#i0118",
        ]
        self.LOGIN_BUTTON_ADFS_LOCATORS = [
            "#submitButton",
            "button[type='submit']",
            "input[type='submit']",
            "#idSIButton9",
        ]
        self._response_statuses = []
        self._response_listener_registered = False

    @property
    def driver(self):
        return self.page

    def _ensure_response_tracking(self):
        if not self._response_listener_registered:
            self.page.on("response", self._track_response)
            self._response_listener_registered = True

    def _track_response(self, response):
        try:
            self._response_statuses.append(response.status)
        except Exception:
            pass

    def _find_any_context(self, selectors, timeout=None):
        timeout = timeout or config.EXPLICIT_WAIT
        deadline = time.time() + timeout
        while time.time() < deadline:
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

        raise PlaywrightTimeoutError(f"Не удалось найти элемент по локаторам: {selectors}")

    def open(self):
        self._ensure_response_tracking()
        self._response_statuses.clear()
        self.page.goto(self.URL, wait_until="domcontentloaded")
        self.page.locator(self.USERNAME_INPUT).first.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 2000)
        return self

    def enter_username(self, username):
        self.page.locator(self.USERNAME_INPUT).first.fill(username)
        return self

    def enter_username_adfs(self, username):
        self._find_any_context(self.USERNAME_INPUT_ADFS_LOCATORS).fill(username)
        return self

    def enter_password(self, password):
        self.page.locator(self.PASSWORD_INPUT).first.fill(password)
        return self

    def enter_password_adfs(self, password):
        self._find_any_context(self.PASSWORD_INPUT_ADFS_LOCATORS).fill(password)
        return self

    def get_entered_username(self):
        return self.page.locator(self.USERNAME_INPUT).first.input_value()

    def get_entered_username_adfs(self):
        return self._find_any_context(self.USERNAME_INPUT_ADFS_LOCATORS).input_value()

    def get_entered_password(self):
        return self.page.locator(self.PASSWORD_INPUT).first.input_value()

    def get_entered_password_adfs(self):
        return self._find_any_context(self.PASSWORD_INPUT_ADFS_LOCATORS).input_value()

    def is_login_button_enabled(self):
        return self.page.locator(self.LOGIN_BUTTON).first.is_enabled()

    def _click_with_fallback(self, locator):
        try:
            locator.click(timeout=4000)
            return True
        except Exception:
            pass

        try:
            locator.click(force=True, timeout=2000)
            return True
        except Exception:
            pass

        # Важно: не используем element_handle() — он может зависать 30s на отвалившемся locator.
        try:
            locator.dispatch_event("click", timeout=1000)
            return True
        except Exception:
            return False

    def click_show_all(self):
        try:
            show_all = self._find_first_visible(self.SHOW_ALL_INPUT_LOCATORS, timeout=3000)
            self._click_with_fallback(show_all)
            return True
        except Exception as exc:
            print(f"⚠️ Не удалось открыть список SSO-провайдеров: {exc}")
            return False

    def adfs_link_open(self):
        self.click_show_all()
        # Иногда модальный overlay перекрывает провайдеры авторизации и перехватывает клики.
        self.page.evaluate(
            """
            () => {
              document.querySelectorAll('.cdk-overlay-pane.modal, .iva-core-modal-overlay, .cdk-overlay-backdrop')
                .forEach((el) => {
                  el.style.pointerEvents = 'none';
                });
            }
            """
        )

        # Критично: сначала пробуем именно ADFS(login+password), потом любой ADFS.
        candidate_groups = [
            self.page.locator("app-auth-providers-list-modal a.pseudo-link").filter(
                has_text=re.compile(r"adfs\s*\(\s*login\+password\s*\)|login\+password", re.IGNORECASE)
            ),
            self.page.locator("app-auth-providers-list-modal a.pseudo-link").filter(
                has_text=re.compile(r"adfs", re.IGNORECASE)
            ),
        ]

        candidates = []
        for group in candidate_groups:
            try:
                for idx in range(group.count()):
                    candidate = group.nth(idx)
                    if candidate.is_visible():
                        candidates.append(candidate)
            except Exception:
                continue

        if not candidates:
            candidates.append(self._find_first_visible(self.ADFS_LINK_LOCATORS, timeout=config.EXPLICIT_WAIT * 1000))

        pattern = re.compile(r"adfs|microsoftonline", re.IGNORECASE)
        last_error = None
        for adfs_element in candidates:
            # Если на предыдущем шаге уже ушли на ADFS — не продолжаем кликать по устаревшим locator.
            if pattern.search(self.page.url or ""):
                print(f"✅ Уже на странице ADFS: {self.page.url}")
                return

            popup_page = None
            try:
                link_text = adfs_element.inner_text(timeout=1000)
            except Exception:
                link_text = "<unknown>"
            print(f"ℹ️ Кликаем ADFS провайдер: {link_text.strip()} | URL до клика: {self.page.url}")

            try:
                with self.page.context.expect_page(timeout=2500) as page_info:
                    clicked = self._click_with_fallback(adfs_element)
                    if not clicked:
                        raise PlaywrightTimeoutError("Не удалось кликнуть по ADFS-провайдеру")
                popup_page = page_info.value
            except Exception:
                if not self._click_with_fallback(adfs_element):
                    last_error = PlaywrightTimeoutError("Не удалось кликнуть по ADFS-провайдеру")
                    continue

            # Быстрый путь: URL уже сменился после клика.
            if pattern.search(self.page.url or ""):
                print(f"✅ ADFS открыт (same tab), URL: {self.page.url}")
                return
            if popup_page is not None:
                try:
                    if pattern.search(popup_page.url or ""):
                        self.page = popup_page
                        print(f"✅ ADFS открыт (popup), URL: {self.page.url}")
                        return
                except Exception:
                    pass

            try:
                self._wait_for_adfs_ready(primary_page=self.page, popup_page=popup_page, timeout_seconds=6)
                print(f"✅ ADFS открыт, текущий URL: {self.page.url}")
                return
            except Exception as exc:
                last_error = exc
                print(f"⚠️ После клика не открылся ADFS, пробуем следующий провайдер. Ошибка: {exc}")

        raise PlaywrightTimeoutError(f"Не удалось открыть/распознать страницу ADFS. Последняя ошибка: {last_error}")

    def _wait_for_adfs_ready(self, primary_page, popup_page=None, timeout_seconds=None):
        pattern = re.compile(r"adfs|microsoftonline", re.IGNORECASE)
        timeout_seconds = timeout_seconds or config.EXPLICIT_WAIT
        timeout_ms = int(timeout_seconds * 1000)

        # 0) URL уже на ADFS/Microsoft — считаем готовым сразу.
        try:
            if pattern.search(primary_page.url or ""):
                return
        except Exception:
            pass
        if popup_page is not None:
            try:
                if pattern.search(popup_page.url or ""):
                    self.page = popup_page
                    return
            except Exception:
                pass

        # 1) Навигация в текущей вкладке.
        try:
            primary_page.wait_for_url(pattern, timeout=timeout_ms, wait_until="domcontentloaded")
            return
        except Exception:
            pass

        # 2) Навигация в popup-вкладке (если появилась).
        if popup_page is not None:
            try:
                popup_page.wait_for_url(pattern, timeout=timeout_ms, wait_until="domcontentloaded")
                self.page = popup_page
                return
            except Exception:
                pass

        # 3) fallback: могли не сменить URL, но ADFS форма уже в DOM.
        # Используем только строгие ADFS/Microsoft id/name селекторы (без input[type=email]).
        strict_adfs_selectors = [
            "#userNameInput",
            "input[name='UserName']",
            "#i0116",
            "#passwordInput",
            "input[name='Password']",
            "#i0118",
        ]
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            for target_page in [primary_page] + ([popup_page] if popup_page is not None else []):
                for selector in strict_adfs_selectors:
                    try:
                        locator = target_page.locator(selector)
                        if locator.count() > 0 and locator.first.is_visible():
                            self.page = target_page
                            return
                    except Exception:
                        continue
            primary_page.wait_for_timeout(250)

        raise PlaywrightTimeoutError("Не удалось открыть/распознать страницу ADFS")

    def wait_for_successful_login(self, timeout=None):
        timeout = timeout or config.EXPLICIT_WAIT
        try:
            self.page.wait_for_function(
                "() => !window.location.href.toLowerCase().includes('/login')",
                timeout=timeout * 1000,
            )
            return True
        except PlaywrightTimeoutError:
            return False

    def click_login_button(self):
        self.page.locator(self.LOGIN_BUTTON).first.click()
        return self

    def click_login_button_adfs(self):
        self._find_any_context(self.LOGIN_BUTTON_ADFS_LOCATORS).click()
        return self

    def get_network_error(self):
        for status in reversed(self._response_statuses[-100:]):
            if 400 <= status < 600:
                return status
        return 0

    def login_with_network_check(self, username=None, password=None, expect_success=True):
        username = username or config.ADMIN_EMAIL
        password = password or config.ADMIN_PASSWORD

        self.open()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

        if expect_success:
            if self.wait_for_successful_login(timeout=config.EXPLICIT_WAIT * 2):
                return 0
            return self.get_network_error()

        self.page.wait_for_timeout(2000)
        return self.get_network_error()

    def check_400_error(self, timeout=5):
        error_text_locators = [
            "text=Неверный логин или пароль",
            "text=Неверный пароль",
            "text=Invalid password",
            "text=Invalid credentials",
            "[e2e-id*='error']",
            ".error, .alert, .notification-error",
        ]

        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.get_network_error() == 400:
                return True

            for locator in error_text_locators:
                element = self.page.locator(locator).first
                if element.count() > 0 and element.is_visible():
                    return True

            self.page.wait_for_timeout(250)
        return False