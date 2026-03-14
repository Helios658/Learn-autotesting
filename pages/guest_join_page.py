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
    HAVE_ACCOUNT_LOCATORS = [
        "[e2e-id='landing-page.already-have-account']",
        "a[e2e-id='landing-page.already-have-account']",
        "xpath=//a[contains(@e2e-id, 'already-have-account')]",
        "xpath=//*[self::a or self::button][contains(normalize-space(.), 'У меня есть аккаунт') or contains(normalize-space(.), 'Уже есть аккаунт') or contains(normalize-space(.), 'I have an account')]",
    ]

    AUTH_MODAL_USERNAME_LOCATORS = [
        "[e2e-id='login-page.login-form.login-input']",
        "input[e2e-id='login-page.login-form.login-input']",
        "input[type='email']",
    ]
    POST_MAIL_JOIN_BUTTON_LOCATORS = [
        "[e2e-id='auth-info__join-button']",
        "button[e2e-id='auth-info__join-button']",
        "button:has-text('Войти')",
        "button:has-text('Продолжить')",
        "button:has-text('Присоединиться')",
        "button:has-text('Подключиться')",
        "button:has-text('Join')",
        "button:has-text('Continue')",
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
        join_btn = self.page.locator("[e2e-id='auth-info__join-button']").first
        join_btn.wait_for(state="visible", timeout=12000)
        join_btn.click(force=True)

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

    def click_already_have_account(self) -> bool:
        try:
            self._find_visible(self.AUTH_MODAL_USERNAME_LOCATORS, timeout_ms=2000)
            return False
        except AssertionError:
            pass

        self._find_visible(self.HAVE_ACCOUNT_LOCATORS, timeout_ms=15_000).click()
        return True

    def click_join_after_mail_link(self) -> None:
        try:
            self._find_visible(self.POST_MAIL_JOIN_BUTTON_LOCATORS, timeout_ms=12_000).click()
            return
        except AssertionError:
            pass

        btn = self.page.get_by_role(
            "button",
            name=re.compile(r"Войти|Продолжить|Присоединиться|Подключиться|Join|Continue", re.IGNORECASE),
        ).first
        btn.click(timeout=8000)

    def finalize_join_from_mail_link(self, timeout_ms: int = 20_000) -> bool:
        deadline = time.time() + timeout_ms / 1000

        while time.time() < deadline:
            current_url = self.page.url or ""
            if "/v2/iva/home/conferences" in current_url and "conferenceSessionId=" in current_url:
                return True

            try:
                join_btn = self.page.locator("[e2e-id='auth-info__join-button']").first
                if join_btn.count() > 0 and join_btn.is_visible():
                    join_btn.click(force=True)
                    self.page.wait_for_timeout(2500)
            except Exception:
                pass

            current_url = self.page.url or ""
            if "/v2/iva/home/conferences" in current_url and "conferenceSessionId=" in current_url:
                return True

            self.page.wait_for_timeout(1500)

        return False