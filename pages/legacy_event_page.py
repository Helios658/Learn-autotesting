import re

from pages.base_page import BasePage
from config import config


class LegacyEventPage(BasePage):
    """PageObject для старого интерфейса создания мероприятия с ticket-ссылкой."""

    OPEN_MAIN_MENU = "[e2e-id='shared-core.navigation-menu.self-actions-popover']"
    SWITCH_TO_LEGACY_BTN = "[e2e-id='profile-action__navigate-to-old-interface']"
    CREATE_EVENT_BTN = "[imarker='planConferenceButton']"

    CREATE_TICKETS_LINK = "[imarker='ticketsLink']"
    TICKET_GENERATE = "[imarker='generateButton']"
    CHECK_BOX_TICKET_LINK = "[imarker='checkBox']"
    COPY_TICKET_LINK_BTN = "[imarker='copyButton']"
    CLOSE_TICKETS_MODAL_LOCATORS = [
        "xpath=//div[@imarker='saveButton'][.//*[contains(normalize-space(.), 'Сохранить') or contains(normalize-space(.), 'Save')]]",
        "[imarker='saveButton']",
    ]
    CLICK_OK_FOR_LEGACY_EVENT_LOCATORS = [
        "xpath=//div[contains(@class,'ivcs-button') and @imarker='mainContainerPanel'][.//div[contains(@class,'ivcs-button-text') and normalize-space(.)='OK']]",
        "xpath=//*[contains(@class,'ivcs-button-text') and normalize-space(.)='OK']/ancestor::*[contains(@class,'ivcs-button')][1]",
    ]

    CREATE_LEGACY_EVENT_LOCATORS = [
        "xpath=//div[contains(@class,'ivcs-dialog-buttons-panel')]//div[@imarker='planConferenceButton'][.//*[contains(normalize-space(.), 'Запланировать') or contains(normalize-space(.), 'Plan')]]",
        "xpath=//div[@imarker='planConferenceButton' and contains(@class,'ivcs-button')][.//div[contains(@class,'ivcs-button-text') and (contains(normalize-space(.), 'Запланировать') or contains(normalize-space(.), 'Plan'))]]",
        "xpath=//div[@imarker='planConferenceButton'][.//*[contains(normalize-space(.), 'Запланировать') or contains(normalize-space(.), 'Plan')]]",
        "[imarker='planConferenceButton']",
    ]

    LEGACY_SWITCH_OK_BUTTON = (
        "xpath=//div[contains(@class,'ivcs-button') and @imarker='mainContainerPanel']"
        "[.//div[contains(@class,'ivcs-button-text') and normalize-space(.)='OK']]"
    )
    LEGACY_SWITCH_CLOSE_BUTTON = (
        "xpath=//div[contains(@class,'ivcs-button') and @imarker='mainContainerPanel']"
        "[.//div[contains(@class,'ivcs-button-text') and normalize-space(.)='Закрыть']]"
    )
    TICKET_URL_VALUE_LOCATORS = [
        "xpath=//*[@imarker='mainContainerPanel']//input[contains(@value,'http')]",
        "xpath=//*[@imarker='mainContainerPanel']//textarea[contains(.,'http')]",
        "xpath=//input[contains(@value,'join:') or contains(@value,'/join') or contains(@value,'ticket')]",
        "xpath=//a[contains(@href,'join:') or contains(@href,'/join') or contains(@href,'ticket')]",
    ]


    def _close_switch_popup_if_visible(self, selector: str, timeout_ms: int = 7000):
        try:
            btn = self.page.locator(selector).first
            btn.wait_for(state="visible", timeout=timeout_ms)
        except Exception:
            return False

        self.safe_click(btn)
        self.page.wait_for_timeout(300)
        return True

    def close_post_switch_popups(self):
        # По согласованному сценарию сначала закрываем окно "Используйте новый интерфейс" (OK),
        # затем окно "Видео инструкция" (Закрыть).
        self._close_switch_popup_if_visible(self.LEGACY_SWITCH_OK_BUTTON, timeout_ms=10_000)
        self._close_switch_popup_if_visible(self.LEGACY_SWITCH_CLOSE_BUTTON, timeout_ms=10_000)
        return self

    def open(self):
        self.page.goto(f"{config.BASE_URL}/v2/iva/home/conferences", wait_until="domcontentloaded")
        self.page.locator(self.OPEN_MAIN_MENU).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        return self

    def open_main_menu(self):
        self.page.locator(self.OPEN_MAIN_MENU).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.OPEN_MAIN_MENU)
        return self

    def switch_to_legacy(self):
        self.open_main_menu()
        self.page.locator(self.SWITCH_TO_LEGACY_BTN).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.SWITCH_TO_LEGACY_BTN)
        self.page.wait_for_url("**/videoconference.html?forcedV1=true**", timeout=config.EXPLICIT_WAIT * 1000)
        self.page.wait_for_load_state("domcontentloaded")
        self.close_post_switch_popups()
        return self

    def open_create_event(self):
        self.page.locator(self.CREATE_EVENT_BTN).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CREATE_EVENT_BTN)
        return self

    def _click_first_visible(self, selectors, timeout_ms: int = 5000, required: bool = True):
        try:
            el = self._find_first_visible(selectors, timeout=timeout_ms)
        except Exception:
            if required:
                raise AssertionError(f"Не найден элемент для клика по локаторам: {selectors}")
            return False
        self.safe_click(el)
        return True

    def open_tickets_modal(self):
        self.page.locator(self.CREATE_TICKETS_LINK).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CREATE_TICKETS_LINK)
        return self

    def generate_ticket_link(self):
        self.page.locator(self.TICKET_GENERATE).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.TICKET_GENERATE)
        return self

    def check_box_ticket_link(self):
        self.page.locator(self.CHECK_BOX_TICKET_LINK).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CHECK_BOX_TICKET_LINK)
        return self

    def copy_ticket_link(self) -> str:
        self.page.context.grant_permissions(["clipboard-read", "clipboard-write"])
        self.safe_click(self.COPY_TICKET_LINK_BTN)
        self.page.wait_for_timeout(250)

        dom_url = self._extract_ticket_url_from_dom()
        if self._looks_like_ticket_url(dom_url):
            return dom_url

        clipboard_text = (
            self.page.evaluate(
                """
                async () => {
                    try {
                        return (await navigator.clipboard.readText()) || "";
                    } catch (e) {
                        return "";
                    }
                }
                """
            )
            or ""
        ).strip()

        selected_text = (
            self.page.evaluate(
                """
                () => {
                    try {
                        return (window.getSelection && window.getSelection().toString()) || "";
                    } catch (e) {
                        return "";
                    }
                }
                """
            )
            or ""
        ).strip()

        page_html_url = self._extract_ticket_url_from_page_html()

        for raw in (clipboard_text, selected_text, page_html_url):
            normalized = self._extract_first_url(raw)
            if self._looks_like_ticket_url(normalized):
                return normalized

        if self._looks_like_url(clipboard_text):
            return clipboard_text

        if self._looks_like_url(dom_url):
            return dom_url

        # По запросу сценария: возвращаем то, что удалось скопировать (или fallback из DOM),
        # без дополнительной блокирующей валидации на этом шаге.
        return clipboard_text

    def _looks_like_url(self, text: str) -> bool:
        if not text:
            return False
        return re.match(r"^https?://", text) is not None

    def _extract_ticket_url_from_dom(self) -> str:
        for selector in self.TICKET_URL_VALUE_LOCATORS:
            try:
                locator = self.page.locator(selector)
                count = locator.count()
                for i in range(count):
                    node = locator.nth(i)
                    if not node.is_visible():
                        continue
                    href = (node.get_attribute("href") or "").strip()
                    value = (node.input_value() if node.evaluate("el => 'value' in el") else "").strip()
                    text = (node.text_content() or "").strip()
                    for candidate in (href, value, text):
                        if self._looks_like_url(candidate):
                            return candidate
            except Exception:
                continue
        return ""

    def _extract_ticket_url_from_page_html(self) -> str:
        try:
            html = (self.page.content() or "").replace("\\n", " ")
        except Exception:
            return ""

        # Приоритетно ищем ссылки join/ticket/token, чтобы не взять случайный URL страницы.
        specific = re.search(r"https?://[^\s\"'<>]*(join|ticket|token)[^\s\"'<>]*", html)
        if specific:
            return specific.group(0)

        any_http = re.search(r"https?://[^\s\"'<>]+", html)
        return any_http.group(0) if any_http else ""

    def _extract_first_url(self, text: str) -> str:
        if not text:
            return ""
        m = re.search(r"https?://[^\s\"'<>]+", text)
        return m.group(0) if m else ""

    def _looks_like_ticket_url(self, text: str) -> bool:
        if not self._looks_like_url(text):
            return False
        lowered = text.lower()
        return any(tag in lowered for tag in ("join", "ticket", "token", "#join:"))

    def close_tickets_modal(self):
        self._click_first_visible(self.CLOSE_TICKETS_MODAL_LOCATORS, timeout_ms=config.EXPLICIT_WAIT * 1000)
        return self

    def click_ok(self):
        # После сохранения тикетов дополнительное окно OK может не появляться.
        self._click_first_visible(
            self.CLICK_OK_FOR_LEGACY_EVENT_LOCATORS,
            timeout_ms=3000,
            required=False,
        )
        return self

    def submit_create_event(self):
        # В legacy есть несколько planConferenceButton (верхняя вкладка и нижняя кнопка отправки).
        # Прокручиваем вниз и кликаем по кнопке в панели действий формы.
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(250)
        self._click_first_visible(self.CREATE_LEGACY_EVENT_LOCATORS, timeout_ms=config.EXPLICIT_WAIT * 1000)
        self.page.wait_for_load_state("domcontentloaded")
        return self

    def create_event_with_single_ticket(self):
        """Полный сценарий в старом вебе: открыть создание, сгенерировать ticket, скопировать и создать."""
        self.open_create_event()
        self.open_tickets_modal()
        self.generate_ticket_link()
        self.check_box_ticket_link()
        ticket_url = self.copy_ticket_link()
        self.close_tickets_modal()
        self.click_ok()
        self.submit_create_event()
        return ticket_url