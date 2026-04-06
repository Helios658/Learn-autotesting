from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from config import config


class NavigatorFlow:

    PARTICIPANT_MENU = ".participant"
    SETTINGS_TAB = "[e2e-id='shared-core.navigation-menu.settings']"
    PROFILE_ITEM = "[e2e-id='settings-page.list.profile']"
    LOGOUT_BUTTON_MENU = "[e2e-id='profile-action__logout']"
    ADMIN_SELECTOR = "[e2e-id='profile-action__navigate-to-administration']"

    def __init__(self, driver: Page):
        self.driver = driver

    def _click_first_visible(self, selectors: tuple[str, ...], *, timeout_ms: int | None = None):
        timeout_ms = timeout_ms or config.EXPLICIT_WAIT * 1000

        for selector in selectors:
            locator = self.driver.locator(selector).first
            try:
                locator.wait_for(state="visible", timeout=timeout_ms)
                locator.click()
                return selector
            except PlaywrightTimeoutError:
                continue

        raise AssertionError(f"Не нашли видимый элемент ни по одному селектору: {selectors}")

    def open_profile_actions_menu(self):
        self.driver.locator(self.PARTICIPANT_MENU).first.click()
        return self

    def open_settings(self):
        self.driver.locator(self.SETTINGS_TAB).first.click()
        return self

    def open_profile_settings(self):
        self.open_settings()
        self.driver.locator(self.PROFILE_ITEM).first.click()
        return self

    def click_logout_in_profile_menu(self):
        self.open_profile_actions_menu()
        self.driver.locator(self.LOGOUT_BUTTON_MENU).first.click()
        return self

    def click_administration_menu(self):
        self.open_profile_actions_menu()
        self.driver.locator(self.ADMIN_SELECTOR).first.click()
        return self