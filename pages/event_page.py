from config import config
from pages.base_page import BasePage


class EventPage(BasePage):
    CONFERENCES_TAB = "[e2e-id='shared-core.navigation-menu.conferences']"
    ADD_BUTTON = "[e2e-id='ADD']"

    TEMPLATE_GROUPS_CARD = (
        "xpath=//div[contains(@class, 'conference-card')]"
        "[.//h4[contains(@class, 'conference-name') and normalize-space()='Деление участников на группы']]"
    )

    SETTINGS_MODAL_BUTTON = "xpath=//span[text()=' Войти ']/parent::button"
    CLOSE_MODAL_BUTTON = "button.close-button.iva-icon-button"

    EVENT_LIST_SCROLLER = "virtual-scroller.selfScroll"
    HAMBURGER_BUTTON = "button.hamburger.iva-icon-button"

    def open(self):
        self.page.goto(f"{config.BASE_URL}/v2/iva/home/conferences", wait_until="domcontentloaded")
        self.page.locator(self.ADD_BUTTON).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )

    def click_add(self):
        self.safe_click(self.ADD_BUTTON)

    def select_groups_template(self):
        self.page.locator(self.TEMPLATE_GROUPS_CARD).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.TEMPLATE_GROUPS_CARD)

    def open_settings_and_close(self):
        self.page.locator(self.SETTINGS_MODAL_BUTTON).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.SETTINGS_MODAL_BUTTON)

        self.page.locator(self.CLOSE_MODAL_BUTTON).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CLOSE_MODAL_BUTTON)

    def back_to_list(self):
        try:
            self.page.locator(self.HAMBURGER_BUTTON).first.click(timeout=5000)
        except Exception:
            self.page.locator(self.HAMBURGER_BUTTON).first.click(force=True)

        self.page.goto(f"{config.BASE_URL}/v2/iva/home/conferences", wait_until="domcontentloaded")
        self._disable_overlay_pointer_events()

        self.page.locator(self.EVENT_LIST_SCROLLER).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        return self

    def _disable_overlay_pointer_events(self):
        self.page.evaluate(
            """
            () => {
              const selectors = [
                '.conference-session.conference-session-wide-mode',
                '[ivamover="conference-session-pip"]',
                '.conference-session video'
              ];
              selectors.forEach((selector) => {
                document.querySelectorAll(selector).forEach((el) => {
                  el.style.pointerEvents = 'none';
                  el.style.zIndex = '0';
                });
              });
            }
            """
        )