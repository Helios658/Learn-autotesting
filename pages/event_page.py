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
    CONFERENCES_TAB_SETTINGS_LOCATORS = [
        "[e2e-id='conference-tab__settings']",
        "button[e2e-id='conference-tab__settings']",
        "[e2e-id='conference-tab__setting']",
        "button[e2e-id='conference-tab__setting']",
        "xpath=//button[@e2e-id='conference-tab__settings' or @e2e-id='conference-tab__setting']",
    ]
    CONFERENCE_SESSION_SETTINGS_GUEST_LINK_COPY = "[e2e-id='conference-session--settings--guest-link--copy-btn']"
    CONFERENCE_SESSION_LINK_LIST = [
        "a.layout.layout-top-margin_8.pseudo-link",
        'a.pseudo-link:has-text("расширенные настройки ссылок")',
    ]
    CONFERENCE_SESSION_SPEAKER_LINK_COPY = "[e2e-id='share-link-copy-speaker-link-btn']"
    SPEAKER_LINK_INPUT_LOCATORS = [
        "input[e2e-id*='speaker']",
        "input[value*='#join:']",
        "input[value*='join:']",
        "input[readonly]",
    ]
    SPEAKER_LINK_ANCHOR_LOCATORS = [
        "a[href*='#join:']",
        "a[href*='join:']",
    ]
    CONFERENCE_SESSION_MODERATOR_LINK_COPY = "[e2e-id='share-link-copy-moderator-link-btn']"
    MODERATOR_LINK_INPUT_LOCATORS = [
        "input[e2e-id*='moderator']",
        "input[value*='#join:']",
        "input[value*='join:']",
        "input[readonly]",
    ]
    MODERATOR_LINK_ANCHOR_LOCATORS = [
        "a[href*='#join:']",
        "a[href*='join:']",
    ]
    GUEST_LINK_INPUT_LOCATORS = [
        "input[e2e-id*='guest-link']",
        "input[value*='#join:']",
        "input[value*='join:']",
        "input[readonly]",
    ]
    GUEST_LINK_ANCHOR_LOCATORS = [
        "a[href*='#join:']",
        "a[href*='join:']",
    ]
    PARTICIPANTS_LIST_LOCATOR = "[e2e-id='toggle-participants-list-btn']"
    PARTICIPANTS_PLUS_BOTTOM_LOCATOR = "[e2e-id='participants-list-additional-actions-btn']"
    ADD_PARTICIPANTS_LOCATOR = "div.option_main-content:has(span.action-title:has-text('Добавить участников'))"

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

    def _reveal_conference_controls(self):
        viewport = self.page.viewport_size or {"width": 1920, "height": 1080}
        top_y = max(int(viewport["height"] * 0.07), 1)

        points = [
            (int(viewport["width"] * 0.50), top_y),
            (int(viewport["width"] * 0.75), top_y),
            (int(viewport["width"] * 0.90), top_y),
            (int(viewport["width"] * 0.96), top_y + 8),
        ]
        for x, y in points:
            self.page.mouse.move(max(x, 1), max(y, 1), steps=10)
            self.page.wait_for_timeout(120)

    def open_event_settings(self):
        for _ in range(4):
            self._reveal_conference_controls()
            try:
                settings_button = self._find_first_visible(self.CONFERENCES_TAB_SETTINGS_LOCATORS, timeout=2500)
                self.safe_click(settings_button)
                return
            except Exception:
                continue

        raise AssertionError(
            "Не удалось открыть вкладку настроек мероприятия: кнопка settings не появилась после reveal controls"
        )

    def open_link_list(self):
        link_list = self._find_first_visible(self.CONFERENCE_SESSION_LINK_LIST, timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(link_list)

    def click_copy_speaker_link(self):
        self.page.locator(self.CONFERENCE_SESSION_SPEAKER_LINK_COPY).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CONFERENCE_SESSION_SPEAKER_LINK_COPY)

    def click_copy_moderator_link(self):
        self.page.locator(self.CONFERENCE_SESSION_MODERATOR_LINK_COPY).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CONFERENCE_SESSION_MODERATOR_LINK_COPY)

    def click_copy_guest_link(self):
        self.page.locator(self.CONFERENCE_SESSION_SETTINGS_GUEST_LINK_COPY).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CONFERENCE_SESSION_SETTINGS_GUEST_LINK_COPY)

    def get_speaker_link_url(self) -> str:
        for selector in self.SPEAKER_LINK_INPUT_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            value = (locator.input_value() or "").strip()
            if "join:" in value:
                return value

        for selector in self.SPEAKER_LINK_ANCHOR_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            href = (locator.get_attribute("href") or "").strip()
            if "join:" in href:
                return href

        full_text = (self.page.content() or "")
        import re
        match = re.search(r'https?://[^\s"\'<>]+#?join:[^\s"\'<>]+', full_text)
        if match:
            return match.group(0)

        raise AssertionError("Не удалось получить speaker-link из настроек мероприятия")

    def get_moderator_link_url(self) -> str:
        for selector in self.MODERATOR_LINK_INPUT_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            value = (locator.input_value() or "").strip()
            if "join:" in value:
                return value

        for selector in self.MODERATOR_LINK_ANCHOR_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            href = (locator.get_attribute("href") or "").strip()
            if "join:" in href:
                return href

        full_text = (self.page.content() or "")
        import re
        match = re.search(r'https?://[^\s"\'<>]+#?join:[^\s"\'<>]+', full_text)
        if match:
            return match.group(0)

        raise AssertionError("Не удалось получить moderator-link из настроек мероприятия")

    def get_guest_link_url(self) -> str:
        for selector in self.GUEST_LINK_INPUT_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            value = (locator.input_value() or "").strip()
            if "join:" in value:
                return value

        for selector in self.GUEST_LINK_ANCHOR_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            href = (locator.get_attribute("href") or "").strip()
            if "join:" in href:
                return href

        raise AssertionError("Не удалось получить guest-link из настроек мероприятия")

    def open_participants_list(self):
        self.page.locator(self.PARTICIPANTS_LIST_LOCATOR).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.PARTICIPANTS_LIST_LOCATOR)

    def plus_bottom_participants_list(self):
        self.page.locator(self.PARTICIPANTS_PLUS_BOTTOM_LOCATOR).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.PARTICIPANTS_PLUS_BOTTOM_LOCATOR)

    def add_participants_bottom(self):
        self.page.locator(self.ADD_PARTICIPANTS_LOCATOR).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.ADD_PARTICIPANTS_LOCATOR)

