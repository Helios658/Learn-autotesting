import json
import re
import time
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import config


class LoginPage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.EXPLICIT_WAIT)
        self.URL = config.LOGIN_URL
        self.USERNAME_INPUT = (By.CSS_SELECTOR, "[e2e-id='login-page.login-form.login-input']")
        self.PASSWORD_INPUT = (By.CSS_SELECTOR, "[e2e-id='login-page.login-form.password-input']")
        self.LOGIN_BUTTON = (By.CSS_SELECTOR, "[e2e-id='login-form__login-button']")
        self.SHOW_ALL_INPUT_LOCATORS = [
            (By.CSS_SELECTOR, "[e2e-id='login-page.login-form.show-more-providers-link']"),
            (By.XPATH, "//a[contains(normalize-space(.), 'Показать все') or contains(normalize-space(.), 'Show all')]"),
            (By.XPATH, "//*[self::a or self::button][contains(@e2e-id, 'show') and contains(@e2e-id, 'provider')]"),
            (By.CSS_SELECTOR, "[e2e-id*='show-all'], [data-testid*='show-all']"),
        ]
        self.ADFS_LINK_LOCATORS = [
            (By.CSS_SELECTOR, "[e2e-id*='adfs']"),
            (By.XPATH, "//*[self::a or self::button][contains(translate(normalize-space(.), 'adfs', 'ADFS'), 'ADFS') and (contains(., 'login+password') or contains(., 'Login+password'))]"),
            (By.XPATH, "//*[self::a or self::button][contains(translate(normalize-space(.), 'adfs', 'ADFS'), 'ADFS')]")
        ]
        self.USERNAME_INPUT_ADFS = (By.CSS_SELECTOR, "#userNameInput")
        self.PASSWORD_INPUT_ADFS = (By.CSS_SELECTOR, "#passwordInput")
        self.LOGIN_BUTTON_ADFS = (By.CSS_SELECTOR, "#submitButton")

    def _resolve_text_input(self, locator):
        """Возвращает реальное поле ввода, даже если locator указывает на контейнер."""
        for _ in range(3):
            try:
                element = self.wait.until(EC.element_to_be_clickable(locator))
                tag_name = element.tag_name.lower()

                if tag_name in {"input", "textarea"}:
                    return element

                nested_input = element.find_elements(By.CSS_SELECTOR, "input, textarea")
                if nested_input:
                    return nested_input[0]

                return element
            except StaleElementReferenceException:
                continue
        return self.wait.until(EC.presence_of_element_located(locator))

    def open(self):
        self.driver.get(self.URL)
        return self

    def enter_username(self, username):
        element = self._resolve_text_input(self.USERNAME_INPUT)
        element.click()
        element.send_keys(username)
        return self

    def enter_username_adfs(self, username):
        element = self._resolve_text_input(self.USERNAME_INPUT_ADFS)
        element.click()
        element.send_keys(username)
        return self

    def enter_password(self, password):
        element = self._resolve_text_input(self.PASSWORD_INPUT)
        element.click()
        element.clear()
        element.send_keys(password)
        return self

    def enter_password_adfs(self, password):
        element = self._resolve_text_input(self.PASSWORD_INPUT_ADFS)
        element.click()
        element.clear()
        element.send_keys(password)
        return self

    def get_entered_username(self):
        element = self.wait.until(EC.presence_of_element_located(self.USERNAME_INPUT))
        return element.get_attribute("value")

    def get_entered_username_adfs(self):
        element = self.wait.until(EC.presence_of_element_located(self.USERNAME_INPUT_ADFS))
        return element.get_attribute("value")

    def get_entered_password(self):
        element = self._resolve_text_input(self.PASSWORD_INPUT)
        return element.get_attribute("value")

    def get_entered_password_adfs(self):
        element = self._resolve_text_input(self.PASSWORD_INPUT_ADFS)
        return element.get_attribute("value")

    def is_login_button_enabled(self):
        element = self._resolve_text_input(self.PASSWORD_INPUT)
        return element.is_enabled()

    def click_show_all(self):
        element = self._find_first_clickable(self.SHOW_ALL_INPUT_LOCATORS)
        if not element:
            return self
        self._safe_click(element)
        return self

    def adfs_link_open(self):
        self.click_show_all()
        element = self._find_first_clickable(self.ADFS_LINK_LOCATORS)
        if not element:
            raise TimeoutException(
                f"Не удалось найти кликабельный ADFS-элемент по локаторам: {self.ADFS_LINK_LOCATORS}")
        self._safe_click(element)

    def _find_first_clickable(self, locators):
        for locator in locators:
            try:
                return WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(locator))
            except TimeoutException:
                continue
        return None

    def _safe_click(self, element):
        for _ in range(2):
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                element.click()
                return
            except StaleElementReferenceException:
                continue
            except Exception:
                self.driver.execute_script("arguments[0].click();", element)
                return

    def wait_for_successful_login(self, timeout=None):
        """
        Ожидает успешный вход: исчезновение кнопки логина
        или уход со страницы /login.
        Возвращает True при успехе, иначе False.
        """
        timeout = timeout or config.EXPLICIT_WAIT
        waiter = WebDriverWait(self.driver, timeout)

        try:
            waiter.until(
                lambda d: ('/login' not in d.current_url.lower())
                or EC.invisibility_of_element_located(self.LOGIN_BUTTON)(d)
            )
            return True
        except TimeoutException:
            return False

    def click_login_button(self):
        element = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
        element.click()
        return self

    def click_login_button_adfs(self):
        element = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON_ADFS))
        element.click()
        return self

    def get_network_error(self):
        """
        Проверяет HTTP ошибку в network
        Возвращает: код ошибки или 0
        """
        try:
            logs = self.driver.get_log('performance')
        except WebDriverException:
            return 0

        for entry in logs[-50:]:
            message = entry.get('message', '')
            if 'responseReceived' not in message:
                continue

            try:
                data = json.loads(message)
                status = data['message']['params']['response']['status']
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

            if 400 <= status < 600:
                return status

        return 0

    def login_with_network_check(self, username=None, password=None, expect_success=True):
        """
        Основной метод: логин + проверка network
        Возвращает код ошибки (0 если нет ошибки)
        """
        username = username or config.ADMIN_EMAIL
        password = password or config.ADMIN_PASSWORD

        self.open()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

        if expect_success:
            try:
                self.wait.until(EC.invisibility_of_element_located(self.LOGIN_BUTTON))
                print("✅ Успешный вход, ожидание завершено.")
            except TimeoutException as e:
                print(f"⚠️ Не дождались успешного входа: {e}")
                return self.get_network_error()

            return self.get_network_error()

        try:
            WebDriverWait(self.driver, 3).until(
                lambda d: self.get_network_error() != 0 or '/login' not in d.current_url.lower()
            )
        except TimeoutException:
            pass

        return self.get_network_error()

    def check_400_error(self, timeout=5):
        """
        Ищет ошибку 400 в network логах.
        Возвращает True если найдена ошибка 400.
        """
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                logs = self.driver.get_log('performance')
            except WebDriverException:
                return False

            for entry in logs[-100:]:
                message = entry.get('message', '')

                if re.search(r'"status"\s*:\s*400\b', message) or '400 Bad Request' in message:
                    print("✅ Найдена ошибка 400 в network логах")
                    return True

                try:
                    data = json.loads(message)
                    params = data.get('message', {}).get('params', {})
                    response = params.get('response', {})
                    status = response.get('status')
                except (json.JSONDecodeError, TypeError):
                    continue

                if status == 400:
                    print("✅ Найдена ошибка 400 (JSON парсинг)")
                    return True

            try:
                WebDriverWait(self.driver, 0.5).until(lambda _: False)
            except TimeoutException:
                pass

        print("⚠️ Ошибка 400 не найдена в логах")
        return False