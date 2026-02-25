import re
from playwright.sync_api import Page
from pages.event_page import EventPage

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class EventFlow:
    EVENT_LIST_SCROLLER = "virtual-scroller.selfScroll"
    EVENT_CARDS = "app-conferences-list-item"

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

            # если у тебя это уже было добавлено раньше — оставь
            self.event_page.back_to_list()

        body = response_info.value.json()
        event_id = body.get("conferenceSessionId") or body.get("id")

        if not event_id or not UUID_RE.match(event_id):
            raise AssertionError(f"Не нашли conferenceSessionId/id в response: {body}")

        return event_id

    def open_event_from_list(self, target_event_id: str):
        scroller = self.driver.locator(self.EVENT_LIST_SCROLLER).first
        scroller.wait_for(state="visible", timeout=15000)

        cards = self.driver.locator(self.EVENT_CARDS)
        count = cards.count()

        for idx in range(count):
            card = cards.nth(idx)
            card.scroll_into_view_if_needed()
            try:
                card.click(timeout=2000)
            except Exception:
                card.click(force=True)

            if target_event_id in self.driver.url:
                return card

        raise AssertionError(f"Не нашли мероприятие {target_event_id}")