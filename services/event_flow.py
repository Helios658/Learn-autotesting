import re
from time import (sleep)
from playwright.sync_api import Page
from pages.event_page import EventPage
from pages.guest_join_page import GuestJoinPage
from pages.guest_auth_modal_page import GuestAuthModalPage
from pages.login_page import LoginPage
from config import config

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

        max_scroll_steps = 120
        no_progress_steps = 0

        for _ in range(max_scroll_steps):
            cards = self.driver.locator(self.EVENT_CARDS)
            visible_count = cards.count()

            for idx in range(visible_count):
                card = cards.nth(idx)
                try:
                    card.scroll_into_view_if_needed(timeout=2000)
                except Exception:
                    pass

                try:
                    card.click(timeout=2000)
                except Exception:
                    card.click(force=True)

                if target_event_id in (self.driver.url or ""):
                    return card

            prev_top = scroller.evaluate("el => el.scrollTop")
            scroller.evaluate(
                "el => el.scrollBy(0, Math.max(Math.floor(el.clientHeight * 0.85), 700))"
            )
            self.driver.wait_for_timeout(350)
            new_top = scroller.evaluate("el => el.scrollTop")

            if new_top <= prev_top + 1:
                no_progress_steps += 1
            else:
                no_progress_steps = 0

            if no_progress_steps >= 3:
                break

        raise AssertionError(
            f"Не нашли мероприятие {target_event_id} после прокрутки списка конференций"
        )

    def get_guest_link_for_event(self, target_event_id: str) -> str:
        if target_event_id not in (self.driver.url or ""):
            self.open_event_from_list(target_event_id)

        self.event_page.open_event_settings()
        return self.event_page.get_guest_link_url()

    def _read_link_from_clipboard(self) -> str:
        self.driver.context.grant_permissions(["clipboard-read", "clipboard-write"])
        link = self.driver.evaluate("""
            async () => {
                try {
                    return (await navigator.clipboard.readText()) || "";
                } catch (e) {
                    return "";
                }
            }
        """)
        return (link or "").strip()

    def get_speaker_link_for_event(self, target_event_id: str) -> str:
        if target_event_id not in (self.driver.url or ""):
            self.open_event_from_list(target_event_id)

        self.event_page.open_event_settings()
        self.event_page.open_link_list()
        self.event_page.click_copy_speaker_link()

        speaker_url = self._read_link_from_clipboard()
        if "join:" in speaker_url:
            return speaker_url

        fallback_url = self.event_page.get_speaker_link_url()
        if "join:" in fallback_url:
            return fallback_url

        raise AssertionError(
            f"Не удалось получить ссылку докладчика ни из буфера, ни из DOM. clipboard={speaker_url}, dom={fallback_url}"
        )

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

    def join_via_guest_link_as_adfs_user(self, guest_url: str, username: str, password: str):
        """Вход по гостевой ссылке с авторизацией через ADFS."""
        guest_context, guest_page = self.open_guest_link_in_incognito(guest_url)
        try:
            guest_join_page = GuestJoinPage(guest_page)
            guest_join_page.click_already_have_account()

            login_page = LoginPage(guest_page)
            login_page.click_show_all()
            login_page.adfs_link_open()
            login_page.enter_username_adfs(username)
            login_page.enter_password_adfs(password)
            login_page.click_login_button_adfs()

            active_page = login_page.page
            active_page.wait_for_load_state("domcontentloaded")


            active_guest_join_page = GuestJoinPage(active_page)
            active_guest_join_page.click_join()
            active_page.wait_for_load_state("domcontentloaded")

            joined = active_guest_join_page.is_in_conference(timeout_ms=20_000)
            return active_page.url, joined
        finally:
            guest_context.close()

    def join_via_guest_link_as_registered_user_login_before_open_guest_link(self, guest_url: str, username: str, password: str):
        guest_context, guest_page = self.open_guest_link_in_incognito(guest_url)
        try:
            login_page = LoginPage(guest_page)
            login_page.open()
            login_page.enter_username(username)
            login_page.enter_password(password)
            login_page.click_login_button()
            if not login_page.wait_for_successful_login(timeout=20):
                raise AssertionError(f"Не удалось залогиниться зарегистрированным пользователем: {guest_page.url}")

            guest_page.goto(guest_url, wait_until="domcontentloaded")
            guest_join_page = GuestJoinPage(guest_page)
            guest_join_page.click_join()

            guest_page.wait_for_load_state("domcontentloaded")
            joined = guest_join_page.is_in_conference(timeout_ms=20_000)
            return guest_page.url, joined
        finally:
            guest_context.close()

    def join_via_guest_link_as_registered_user_login_before_open_quest_link(self, guest_url: str, username: str, password: str):
        return self.join_via_guest_link_as_registered_user_login_before_open_guest_link(
            guest_url=guest_url,
            username=username,
            password=password,
        )