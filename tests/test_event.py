import time
import pytest
from config import config
import re
from urllib.parse import parse_qs, urlparse
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CONFERENCES_TAB = (By.CSS_SELECTOR, "[e2e-id='shared-core.navigation-menu.conferences']")
ADD_BUTTON = (By.CSS_SELECTOR, "[e2e-id='ADD']")
SETTINGS_MODAL_BUTTON = (By.XPATH, "//span[text()=' Войти ']/parent::button")
CLOSE_MODAL_BUTTON = (By.CSS_SELECTOR, "button.close-button.iva-icon-button")
HAMBURGER_BUTTON = (By.CSS_SELECTOR, "button.hamburger.iva-icon-button")
EVENTS_TAB = (By.CSS_SELECTOR, "[e2e-id='shared-core.navigation-menu.conferences']")
EVENT_LIST_SCROLLER = (By.CSS_SELECTOR, "virtual-scroller.selfScroll")
EVENT_CARDS = (By.CSS_SELECTOR, "app-conferences-list-item")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)


def _click_when_ready(wait: WebDriverWait, locator: tuple[str, str]):
    element = wait.until(EC.element_to_be_clickable(locator))
    element.click()


def _select_conference_template(wait: WebDriverWait, template_name: str):
    template_locator = (
        By.XPATH,
        "//div[contains(@class, 'conference-card')]"
        f"[.//h4[contains(@class, 'conference-name') and normalize-space()='{template_name}']]",
    )
    _click_when_ready(wait, template_locator)


def _wait_for_event_in_list(wait: WebDriverWait, event_id: str):
    """Проверяет, что карточка мероприятия с event_id появилась в списке."""
    possible_locators = [
        (By.CSS_SELECTOR, f"a[href*='/conferences/{event_id}']"),
        (By.CSS_SELECTOR, f"[href*='conferenceId={event_id}']"),
        (By.CSS_SELECTOR, f"[data-conference-id='{event_id}']"),
        (By.CSS_SELECTOR, f"[data-id='{event_id}']"),
    ]

    for locator in possible_locators:
        try:
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            continue

    raise AssertionError(f"Мероприятие с id={event_id} не найдено в списке мероприятий")

def _extract_event_id(current_url: str) -> str:
    """Достаёт UUID мероприятия из URL создания/открытия."""
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

    # fallback на случай path-варианта
    path_match = re.search(r"/conferences/([0-9a-f-]{36})", parsed_url.path, flags=re.IGNORECASE)
    if path_match and UUID_RE.match(path_match.group(1)):
        return path_match.group(1)

    raise AssertionError(f"Не удалось достать UUID мероприятия из URL: {current_url}")


def _extract_selected_item_id(current_url: str) -> str | None:
    """ID выбранного в списке мероприятия (появляется после клика по карточке)."""
    parsed_url = urlparse(current_url)
    query_params = parse_qs(parsed_url.query)
    for key in ("conferenceItemId", "conferenceItem_conferenceSessionId", "conferenceSessionId"):
        values = query_params.get(key)
        if values and UUID_RE.match(values[0]):
            return values[0]
    return None


def _find_event_in_virtual_list_by_id(wait: WebDriverWait, driver, target_event_id: str):
    """
    В списке URL не меняется сам по себе.
    Поэтому кликаем карточки и проверяем, что после клика в URL появился conferenceItemId=<target_event_id>.
    """
    scroller = wait.until(EC.presence_of_element_located(EVENT_LIST_SCROLLER))
    seen_signatures: set[str] = set()

    max_scroll_attempts = 40
    for _ in range(max_scroll_attempts):
        cards = driver.find_elements(*EVENT_CARDS)
        for card in cards:
            try:
                signature = card.text.strip()
                if signature in seen_signatures:
                    continue
                seen_signatures.add(signature)

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                driver.execute_script("arguments[0].click();", card)

                selected_id = _extract_selected_item_id(driver.current_url)
                if selected_id == target_event_id:
                    return card
            except StaleElementReferenceException:
                continue
        old_scroll_top = driver.execute_script("return arguments[0].scrollTop;", scroller)
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight;", scroller)
        time.sleep(0.4)
        new_scroll_top = driver.execute_script("return arguments[0].scrollTop;", scroller)

        if new_scroll_top == old_scroll_top:
            break

    raise AssertionError(
        f"Не нашли мероприятие с id={target_event_id} в virtual-scroller (перебрали карточки и прокрутили список)"
    )

@pytest.mark.buildtest
@pytest.mark.testcase("30887")
def test_30887_events_one_time_login_only(login_page, driver):
    wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

    error_code = login_page.login_with_network_check(
        username=config.ADMIN_EMAIL,
        password=config.ADMIN_PASSWORD,
        expect_success=True,
    )

    assert error_code == 0, f"Ошибка сети при логине: {error_code}"
    assert login_page.wait_for_successful_login(), (
        f"Логин неуспешен, текущий URL: {login_page.driver.current_url}"
    )

    # 1. Переход на вкладку Конференции и создание по шаблону
    _click_when_ready(wait, CONFERENCES_TAB)
    _click_when_ready(wait, ADD_BUTTON)
    _select_conference_template(wait, "Деление участников на группы")

    # 2. Нажимаем на кнопку "Войти" в модальном окне
    _click_when_ready(wait, SETTINGS_MODAL_BUTTON)
    print("✅ Нажали кнопку 'Войти' в модальном окне")
    # 3. Закрываем модальное окно
    _click_when_ready(wait, CLOSE_MODAL_BUTTON)
    print("✅ Закрыли модальное окно")

    created_event_id = _extract_event_id(driver.current_url)
    print(f"✅ Получили id созданного мероприятия: {created_event_id}")

    # 4. Двигаем мышку, чтобы появился гамбургер
    conference_header = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".conference-header, .conference-title, h1"))
    )

    action_chains = ActionChains(driver)
    action_chains.move_to_element(conference_header).perform()
    print("✅ Навели мышь на заголовок конференции")

    # 5. Нажимаем на гамбургер
    _click_when_ready(wait, HAMBURGER_BUTTON)
    print("✅ Нажали на кнопку-гамбургер")

    # 6. Возвращаемся на страницу списка мероприятий
    events_tab = wait.until(
        EC.presence_of_element_located(EVENTS_TAB)
    )
    driver.execute_script("arguments[0].click();", events_tab)
    print("✅ Вернулись на страницу списка мероприятий")

    event_card = _find_event_in_virtual_list_by_id(wait, driver, created_event_id)
    assert event_card.is_displayed(), (
        f"Мероприятие c id={created_event_id} найдено, но не отображается в списке"
    )
    print(f"✅ Мероприятие c id={created_event_id} найдено в списке")
