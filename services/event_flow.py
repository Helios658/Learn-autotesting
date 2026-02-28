import re
from playwright.sync_api import Page
from pages.event_page import EventPage
from pages.guest_join_page import GuestJoinPage
from pages.guest_auth_modal_page import GuestAuthModalPage

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

    def create_event(self, return_to_list: bool = True) -> str:
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

            if return_to_list:
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

    def get_guest_link_for_event(self, target_event_id: str) -> str:
        if target_event_id not in (self.driver.url or ""):
            self.open_event_from_list(target_event_id)

        self.event_page.open_event_settings()
        return self.event_page.get_guest_link_url()

    def open_guest_link_in_incognito(self, guest_url: str):
        browser = self.driver.context.browser
        if browser is None:
            raise AssertionError("Не удалось получить browser из текущего driver context")

        guest_context = browser.new_context(ignore_https_errors=True)
        guest_page = guest_context.new_page()
        guest_page.goto(guest_url, wait_until="domcontentloaded")
        return guest_context, guest_page


    def join_guest_via_link(self, guest_url: str, guest_name: str = "Auto Guest"):
        guest_context, guest_page = self.open_guest_link_in_incognito(guest_url)
        try:
            GuestJoinPage(guest_page).join(guest_name)
            guest_page.wait_for_load_state("domcontentloaded")
            return guest_page.url
        finally:
            guest_context.close()

    def join_via_guest_link_as_registered_user(self, guest_url: str, username: str, password: str):
        guest_context, guest_page = self.open_guest_link_in_incognito(guest_url)
        try:
            guest_join_page = GuestJoinPage(guest_page)
            guest_join_page.click_already_have_account()

            auth_modal = GuestAuthModalPage(guest_page)
            auth_modal.wait_opened().login(username=username, password=password)

            guest_page.wait_for_load_state("domcontentloaded")
            joined = guest_join_page.is_in_conference(timeout_ms=20_000)
            return guest_page.url, joined
        finally:
            guest_context.close()