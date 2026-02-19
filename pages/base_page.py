import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class BasePage:
    def __init__(self, page):
        self.page = page

    def _find_first_visible(self, selectors, timeout=3000):
        deadline = time.time() + timeout / 1000
        while time.time() < deadline:
            for selector in selectors:
                locator = self.page.locator(selector)
                if locator.count() > 0 and locator.first.is_visible():
                    return locator.first
            self.page.wait_for_timeout(200)
        raise PlaywrightTimeoutError(f"Не удалось найти видимый элемент по локаторам: {selectors}")

    def _safe_click(self, selector_or_locator):
        locator = selector_or_locator if hasattr(selector_or_locator, "click") else self.page.locator(selector_or_locator)
        try:
            locator.first.scroll_into_view_if_needed()
            locator.first.click()
        except Exception:
            self.page.evaluate("(el) => el.click()", locator.first.element_handle())