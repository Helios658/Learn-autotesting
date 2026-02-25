from playwright.sync_api import Page
from config import config


class LogoutFlow:
    PARTICIPANT_MENU = ".participant"
    LOGOUT_BUTTON_MENU = "[e2e-id='profile-action__logout']"

    SETTINGS_TAB = "[e2e-id='shared-core.navigation-menu.settings']"
    PROFILE_ITEM = "[e2e-id='settings-page.list.profile']"
    LOGOUT_LINK_PROFILE = "[e2e-id='settings-page.profile.logout-link']"

    def __init__(self, driver: Page):
        self.driver = driver

    def logout_via_menu(self):
        self.driver.locator(self.PARTICIPANT_MENU).first.click()
        self.driver.locator(self.LOGOUT_BUTTON_MENU).first.click()
        self.driver.wait_for_url("**/login**", timeout=config.EXPLICIT_WAIT * 1000)
        return True

    def logout_via_profile(self):
        self.driver.locator(self.SETTINGS_TAB).first.click()
        self.driver.locator(self.PROFILE_ITEM).first.click()
        self.driver.locator(self.LOGOUT_LINK_PROFILE).first.click()
        self.driver.wait_for_url("**/login**", timeout=config.EXPLICIT_WAIT * 1000)
        return True