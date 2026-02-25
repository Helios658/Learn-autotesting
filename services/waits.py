from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def wait_visible(page, selector: str, timeout_ms: int):
    return page.locator(selector).first.wait_for(state="visible", timeout=timeout_ms)


def wait_url(page, pattern, timeout_ms: int):
    page.wait_for_url(pattern, timeout=timeout_ms)


def wait_dom_ready(page, timeout_ms: int):
    page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)


def wait_not_login(page, timeout_ms: int) -> bool:
    try:
        page.wait_for_function(
            "() => !window.location.href.toLowerCase().includes('/login')",
            timeout=timeout_ms,
        )
        return True
    except PlaywrightTimeoutError:
        return False