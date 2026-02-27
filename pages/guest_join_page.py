import re
import time
from playwright.sync_api import Error as PlaywrightError


class GuestJoinPage:
    NAME_FIELD_LOCATORS = [
        "[e2e-id='auth-info__name-input']",
        "input[e2e-id='auth-info__name-input']",
        "input[e2e-id*='guest-name']",
        "input[placeholder*='Введите своё имя']",
        "input[placeholder*='Имя']",
        "input[placeholder*='Name']",
        "input[type='text']",
    ]

    JOIN_BUTTON_LOCATORS = [
        "[e2e-id='auth-info__join-button']",
        "button[e2e-id='auth-info__join-button']",
    ]

    def __init__(self, page):
        self.page = page

    def _find_visible(self, selectors, timeout_ms: int = 10_000):
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            for selector in selectors:
                try:
                    locator = self.page.locator(selector)
                    if locator.count() > 0 and locator.first.is_visible():
                        return locator.first
                except PlaywrightError:
                    pass

                for frame in self.page.frames:
                    try:
                        frame_locator = frame.locator(selector)
                        if frame_locator.count() > 0 and frame_locator.first.is_visible():
                            return frame_locator.first
                    except PlaywrightError:
                        continue
            self.page.wait_for_timeout(200)

        raise AssertionError(f"Не найден видимый элемент по локаторам: {selectors}")

    def enter_guest_name(self, name: str) -> None:
        field = self._find_visible(self.NAME_FIELD_LOCATORS, timeout_ms=12_000)
        field.fill(name)

    def click_join(self) -> None:
        try:
            self._find_visible(self.JOIN_BUTTON_LOCATORS, timeout_ms=8_000).click()
            return
        except AssertionError:
            pass

        login_btn = self.page.get_by_role(
            "button",
            name=re.compile(r"Войти|Join|Продолжить", re.IGNORECASE),
        ).first
        login_btn.click(timeout=8000)

    def join(self, name: str) -> None:
        self.enter_guest_name(name)
        self.click_join()

    def is_in_conference(self, timeout_ms: int = 15_000) -> bool:
        conference_locators = [
            ".conference-session",
            "[ivamover='conference-session-pip']",
            "video",
            "[e2e-id*='conference']",
        ]

        try:
            self._find_visible(conference_locators, timeout_ms=timeout_ms)
            return True
        except AssertionError:
            return False