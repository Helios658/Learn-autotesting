import pytest
from config import config
import re
from urllib.parse import urlparse, parse_qs

CONFERENCES_TAB = "[e2e-id='shared-core.navigation-menu.conferences']"
ADD_BUTTON = "[e2e-id='ADD']"
SETTINGS_MODAL_BUTTON = "xpath=//span[text()=' Войти ']/parent::button"
CLOSE_MODAL_BUTTON = "button.close-button.iva-icon-button"
HAMBURGER_BUTTON = "button.hamburger.iva-icon-button"
EVENTS_TAB = "[e2e-id='shared-core.navigation-menu.conferences']"
EVENT_LIST_SCROLLER = "virtual-scroller.selfScroll"
EVENT_CARDS = "app-conferences-list-item"
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)


def _extract_event_id(current_url: str) -> str:
    parsed_url = urlparse(current_url)
    query_params = parse_qs(parsed_url.query)

    for key in (
        "conferenceSessionId",
        "conferenceItemId",
        "conferenceItem_conferenceSessionId",
        "conferenceId",
        "conference_id",
        "eventId",
        "id",
    ):
        values = query_params.get(key)
        if values and UUID_RE.match(values[0]):
            return values[0]

    path_match = re.search(r"/conferences/([0-9a-f-]{36})", parsed_url.path, flags=re.IGNORECASE)
    if path_match and UUID_RE.match(path_match.group(1)):
        return path_match.group(1)

    raise AssertionError(f"Не удалось достать UUID мероприятия из URL: {current_url}")


def _extract_selected_item_id(current_url: str) -> str | None:
    parsed_url = urlparse(current_url)
    query_params = parse_qs(parsed_url.query)
    for key in ("conferenceItemId", "conferenceItem_conferenceSessionId", "conferenceSessionId"):
        values = query_params.get(key)
        if values and UUID_RE.match(values[0]):
            return values[0]
    return None


def _find_event_in_virtual_list_by_id(page, target_event_id: str):
    _disable_overlay_pointer_events(page)
    scroller = page.locator(EVENT_LIST_SCROLLER).first
    scroller.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

    max_scroll_attempts = 40
    for _ in range(max_scroll_attempts):
        cards = page.locator(EVENT_CARDS)
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
                    page.evaluate("el => el.click()", card.element_handle())
            selected_id = _extract_selected_item_id(page.url)
            if selected_id == target_event_id:
                return card

        old_scroll = page.evaluate("el => el.scrollTop", scroller.element_handle())
        page.evaluate("el => { el.scrollTop = el.scrollTop + el.clientHeight; }", scroller.element_handle())
        time.sleep(0.4)
        new_scroll = page.evaluate("el => el.scrollTop", scroller.element_handle())
        if new_scroll == old_scroll:
            break

    raise AssertionError(f"Не нашли мероприятие с id={target_event_id} в virtual-scroller")


def _disable_overlay_pointer_events(page):
    """Отключает перехват pointer-событий у PiP/видео-оверлея, который мешает кликам по списку."""
    page.evaluate(
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


@pytest.mark.buildtest
@pytest.mark.testcase("30887")
def test_30887_events_one_time_login_only(login_page, driver):
    error_code = login_page.login_with_network_check(
        username=config.ADMIN_EMAIL,
        password=config.ADMIN_PASSWORD,
        expect_success=True,
    )

    assert error_code == 0, f"Ошибка сети при логине: {error_code}"
    assert login_page.wait_for_successful_login(), f"Логин неуспешен, текущий URL: {driver.url}"

    driver.locator(CONFERENCES_TAB).first.click()
    driver.locator(ADD_BUTTON).first.click()
    driver.locator(
        "xpath=//div[contains(@class, 'conference-card')][.//h4[contains(@class, 'conference-name') and normalize-space()='Деление участников на группы']]"
    ).first.click()

    driver.locator(SETTINGS_MODAL_BUTTON).first.click()
    driver.locator(CLOSE_MODAL_BUTTON).first.click()

    created_event_id = _extract_event_id(driver.url)

    # На части окружений поверх хедера находится активный video/PiP-слой,
    # поэтому hover нестабилен и часто перехватывается overlay.
    try:
        driver.locator(HAMBURGER_BUTTON).first.click(timeout=5000)
    except Exception:
        driver.locator(HAMBURGER_BUTTON).first.click(force=True)

    # На части окружений переход назад в список из wide-mode через кнопку меню
    # не срабатывает из-за перекрытий, поэтому делаем детерминированную навигацию.
    driver.goto(f"{config.BASE_URL}/v2/iva/home/conferences", wait_until="domcontentloaded")
    _disable_overlay_pointer_events(driver)
    driver.locator(EVENT_LIST_SCROLLER).first.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

    event_card = _find_event_in_virtual_list_by_id(driver, created_event_id)
    assert event_card.is_visible(), f"Мероприятие c id={created_event_id} найдено, но не отображается в списке"