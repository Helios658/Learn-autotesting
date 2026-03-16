import time
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from utils.ui_interruptions import close_meeting_start_popup_if_present


class BasePage:
    def __init__(self, page):
        self.page = page

    def _find_first_visible(self, selectors, timeout=3000):
        deadline = time.time() + timeout / 1000
        while time.time() < deadline:
            try:
                close_meeting_start_popup_if_present(self.page)
            except Exception:
                pass
            for selector in selectors:
                try:
                    locator = self.page.locator(selector)
                    for i in range(locator.count()):
                        candidate = locator.nth(i)
                        if candidate.is_visible():
                            return candidate
                except PlaywrightError:
                    continue

                for frame in self.page.frames:
                    try:
                        frame_locator = frame.locator(selector)
                        for i in range(frame_locator.count()):
                            candidate = frame_locator.nth(i)
                            if candidate.is_visible():
                                return candidate
                    except PlaywrightError:
                        continue
            self.page.wait_for_timeout(200)
        raise PlaywrightTimeoutError(f"Не удалось найти видимый элемент по локаторам: {selectors}")

    def safe_click(self, selector, timeout=5000):
        """
        Универсальный клик: закрыть случайные pop-up -> scroll -> click -> force -> js click
        """
        try:
            close_meeting_start_popup_if_present(self.page)
        except Exception:
            pass

        locator = selector if hasattr(selector, "click") else self.page.locator(selector)

        try:
            locator.first.scroll_into_view_if_needed(timeout=timeout)
        except PlaywrightTimeoutError:
            pass

        try:
            locator.first.click(timeout=timeout)
            return
        except (PlaywrightTimeoutError, PlaywrightError):
            try:
                close_meeting_start_popup_if_present(self.page)
            except Exception:
                pass

        try:
            locator.first.click(force=True, timeout=2000)
            return
        except (PlaywrightTimeoutError, PlaywrightError):
            pass

        try:
            handle = locator.first.element_handle(timeout=1000)
            if handle is None:
                raise PlaywrightTimeoutError("element_handle вернул None")
            self.page.evaluate("(el) => el.click()", handle)
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise PlaywrightTimeoutError(f"safe_click failed for selector={selector}: {e}")