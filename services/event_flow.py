import time
import re
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import Page

from config import config
from pages.event_page import EventPage

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class EventFlow:
    EVENT_LIST_SCROLLER = "virtual-scroller.selfScroll"
    EVENT_CARDS = "app-conferences-list-item"
    HAMBURGER_BUTTON = "button.hamburger.iva-icon-button"

    def __init__(self, driver: Page):
        self.driver = driver
        self.event_page = EventPage(driver)

    def create_event(self) -> str:
        with self.driver.expect_response(
            lambda r: (
                "/api/rest/conferences/start-now" in r.url
                or "/api/rest/public/conference-sessions/" in r.url
            ),
            timeout=60_000,
        ) as response_info:
            self.event_page.open()
            self.event_page.click_add()
            self.event_page.select_groups_template()
            self.event_page.open_settings_and_close()

        body = response_info.value.json()
        event_id = body.get("conferenceSessionId") or body.get("id")
        if not event_id:
            raise AssertionError(f"Не нашли conferenceSessionId/id в response: url={response_info.value.url}")
        return event_id

    def return_to_events_list(self):
        # Поведение как в твоём тесте: пробуем меню, потом жестко go to list
        try:
            self.driver.locator(self.HAMBURGER_BUTTON).first.click(timeout=5000)
        except Exception:
            self.driver.locator(self.HAMBURGER_BUTTON).first.click(force=True)

        self.driver.goto(f"{config.BASE_URL}/v2/iva/home/conferences", wait_until="domcontentloaded")
        self._disable_overlay_pointer_events()
        self.driver.locator(self.EVENT_LIST_SCROLLER).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )

    def open_event_from_list(self, target_event_id: str):
        self._disable_overlay_pointer_events()

        scroller = self.driver.locator(self.EVENT_LIST_SCROLLER).first
        scroller.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        max_scroll_attempts = 40
        for _ in range(max_scroll_attempts):
            cards = self.driver.locator(self.EVENT_CARDS)
            count = cards.count()

            for idx in range(count):
                card = cards.nth(idx)
                card.scroll_into_view_if_needed()

                try:
                    card.click(timeout=1500)
                except Exception:
                    try:
                        card.click(force=True, timeout=1000)
                    except Exception:
                        self.driver.evaluate("el => el.click()", card.element_handle())

                selected_id = self._extract_selected_item_id(self.driver.url)
                if selected_id == target_event_id:
                    return card

            old_scroll = self.driver.evaluate("el => el.scrollTop", scroller.element_handle())
            self.driver.evaluate("el => { el.scrollTop = el.scrollTop + el.clientHeight; }", scroller.element_handle())
            time.sleep(0.4)
            new_scroll = self.driver.evaluate("el => el.scrollTop", scroller.element_handle())
            if new_scroll == old_scroll:
                break

        raise AssertionError(f"Не нашли мероприятие с id={target_event_id} в virtual-scroller")

    # ---------- helpers ----------

    def _extract_selected_item_id(self, current_url: str) -> str | None:
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)
        for key in ("conferenceItemId", "conferenceItem_conferenceSessionId", "conferenceSessionId"):
            values = query_params.get(key)
            if values and UUID_RE.match(values[0]):
                return values[0]
        return None

    def _disable_overlay_pointer_events(self):
        self.driver.evaluate(
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