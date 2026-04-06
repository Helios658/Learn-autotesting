from playwright.sync_api import Page
from config import config
from services.navigator_flow import NavigatorFlow


class LogoutFlow:
    PARTICIPANT_MENU = ".participant"
    LOGOUT_BUTTON_MENU = "[e2e-id='profile-action__logout']"

    SETTINGS_TAB = "[e2e-id='shared-core.navigation-menu.settings']"
    PROFILE_ITEM = "[e2e-id='settings-page.list.profile']"
    LOGOUT_LINK_PROFILE = "[e2e-id='settings-page.profile.logout-link']"

    def __init__(self, driver: Page):
        self.driver = driver
        self.navigator = NavigatorFlow(driver)

    def logout_via_menu(self):
        self.navigator.click_logout_in_profile_menu()
        self.driver.wait_for_url("**/login**", timeout=config.EXPLICIT_WAIT * 1000)
        return True

    def logout_via_profile(self):
        self.navigator.open_profile_settings()
        self.driver.locator(self.LOGOUT_LINK_PROFILE).first.click()
        self.driver.wait_for_url("**/login**", timeout=config.EXPLICIT_WAIT * 1000)
        return True