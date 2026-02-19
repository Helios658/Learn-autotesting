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
                if locator.count() > 0:
                    return locator.first

            for frame in self.page.frames:
                for selector in selectors:
                    locator = frame.locator(selector)
                    if locator.count() > 0:
                        return locator.first
            self.page.wait_for_timeout(250)

        raise PlaywrightTimeoutError(f"Не удалось найти элемент по локаторам: {selectors}")

    def open(self):
        self._ensure_response_tracking()
        self._response_statuses.clear()
        self.page.goto(self.URL, wait_until="domcontentloaded")
        self.page.locator(self.USERNAME_INPUT).first.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
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

    def click_show_all(self):
        try:
            self._find_first_visible(self.SHOW_ALL_INPUT_LOCATORS, timeout=3000).click()
        except Exception:
            pass
        return self

    def adfs_link_open(self):
        self.click_show_all()
        # Иногда модальный overlay перекрывает провайдеры авторизации и перехватывает клики.
        # Убираем перехват pointer-событий у известных overlay-контейнеров.
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
        adfs_element = self._find_first_visible(self.ADFS_LINK_LOCATORS, timeout=config.EXPLICIT_WAIT * 1000)
        try:
            adfs_element.click(timeout=5000)
        except Exception:
            adfs_element.click(force=True)
        self.page.wait_for_url(re.compile(r"adfs|microsoftonline", re.IGNORECASE), timeout=config.EXPLICIT_WAIT * 1000)

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
