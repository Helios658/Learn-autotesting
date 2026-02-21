import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class BasePage:
    def __init__(self, page):
        self.page = page

    def _find_first_visible(self, selectors, timeout=3000):
        deadline = time.time() + timeout / 1000
        while time.time() < deadline:
            for selector in selectors:
                try:
                    locator = self.page.locator(selector)
                    for i in range(locator.count()):
                        candidate = locator.nth(i)
                        if candidate.is_visible():
                            return candidate
                except Exception:
                    pass

                for frame in self.page.frames:
                    try:
                        frame_locator = frame.locator(selector)
                        for i in range(frame_locator.count()):
                            candidate = frame_locator.nth(i)
                            if candidate.is_visible():
                                return candidate
                    except Exception:
                        continue
            self.page.wait_for_timeout(200)
        raise PlaywrightTimeoutError(f"Не удалось найти видимый элемент по локаторам: {selectors}")

    def _safe_click(self, selector_or_locator):
        locator = selector_or_locator if hasattr(selector_or_locator, "click") else self.page.locator(selector_or_locator)
        try:
            locator.first.scroll_into_view_if_needed()
            locator.first.click()
        except Exception:
            self.page.evaluate("(el) => el.click()", locator.first.element_handle())