
import time

import pytest
from playwright.sync_api import Error as PlaywrightError

from config import config
from services.login_flow import LoginFlow
from pages.event_page import EventPage


ROOMS_TAB = "[e2e-id='shared-core.navigation-menu.rooms']"
ROOMS_PLUS_BUTTONS = [
    "button[e2e-id='item.e2e']:has(svg path[d*='M8.5 3.5v4h4v1h-4v4h-1v-4h-4v-1h4v-4z'])",
    "button.iva-round-button:has(svg path[d*='M8.5 3.5v4h4v1h-4v4h-1v-4h-4v-1h4v-4z'])",
]
ROOM_NAME_INPUTS = [
    "input[name='name']",
    "input[placeholder='Название']",
    "input[placeholder*='комнат' i]",
    ".editable-text-container input",
    ".editable-text-container textarea",
    "[contenteditable='true']",
]
JOIN_SETTINGS = "text=Подключение к мероприятию"
AUTO_CALL_CHECKBOX = "xpath=//div[contains(normalize-space(), 'Вызывать участников при начале сессии комнаты')]/ancestor::label[1]"
ADD_MEMBER_BUTTON = "button[e2e-id='add-button-tab']"
SEARCH_USER_INPUTS = [
    "input.search-input[placeholder*='Поиск участников' i]",
    "input.search-input[placeholder*='Поиск пользователей' i]",
    "input.search-input.iva-input",
]
CREATE_ROOM_BUTTON = "button:has-text('Создать')"
ENTER_BUTTON = "button.enter-button"
CONNECT_BUTTON = "button:has-text('Подключиться')"


def _first_visible(page, selectors: list[str] | str, timeout_ms: int = 10_000):
    selectors = [selectors] if isinstance(selectors, str) else selectors
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            locator.wait_for(state="visible", timeout=timeout_ms)
            return locator
        except PlaywrightError:
            continue
    raise AssertionError(f"Не нашли видимый элемент: {selectors}")






def _open_rooms(page):
    page.goto(f"{config.BASE_URL}/v2/iva/home/rooms", wait_until="domcontentloaded")
    try:
        _first_visible(page, ROOMS_PLUS_BUTTONS, timeout_ms=8_000)
        return
    except AssertionError:
        pass

    _first_visible(page, ROOMS_TAB, timeout_ms=8_000).click()
    _first_visible(page, ROOMS_PLUS_BUTTONS, timeout_ms=10_000)

def _click_rooms_plus(page):
    for selector in ROOMS_PLUS_BUTTONS:
        try:
            btn = _first_visible(page, selector, timeout_ms=5_000)
            btn.click()
            if page.locator("text=Подключиться по ID").first.is_visible(timeout=1500):
                page.keyboard.press("Escape")
                continue
            return
        except PlaywrightError:
            continue

    # fallback: выбираем последнюю кнопку item.e2e (обычно это '+').
    buttons = page.locator("button[e2e-id='item.e2e']")
    if buttons.count() == 0:
        raise AssertionError("Не нашли кнопку '+' для создания комнаты")

    buttons.nth(buttons.count() - 1).click()
    if page.locator("text=Подключиться по ID").first.is_visible(timeout=1500):
        raise AssertionError("Нажали на кнопку 'Подключиться по ID' вместо '+' создания комнаты")





def _add_user_to_room(page, user_email: str):
    _first_visible(page, ADD_MEMBER_BUTTON).click()

    overlay_input = page.locator(".cdk-overlay-container input.search-input.iva-input").first
    try:
        overlay_input.wait_for(state="visible", timeout=8_000)
        search_input = overlay_input
    except PlaywrightError:
        search_input = _first_visible(page, SEARCH_USER_INPUTS, timeout_ms=10_000)

    search_input.fill("")
    search_input.fill(user_email)
    try:
        search_input.press("Enter")
    except PlaywrightError:
        pass

    page.wait_for_timeout(700)

    room_ui = EventPage(page)
    room_ui.select_invited_participant_checkbox(user_email)
    room_ui.submit_invite_participant()

def _finalize_room_creation_if_needed(page):
    create_btn = page.locator(CREATE_ROOM_BUTTON).first
    try:
        if create_btn.is_visible(timeout=3_000):
            create_btn.click()
    except PlaywrightError:
        pass


def _enter_room_by_name(page, room_name: str):
    room_row = page.locator(f"xpath=//*[contains(normalize-space(), '{room_name}')]/ancestor::*[self::app-conferences-list-item or self::div][1]").first
    try:
        room_row.wait_for(state="visible", timeout=10_000)
        enter_btn = room_row.locator("button.enter-button").first
        if enter_btn.count() > 0 and enter_btn.is_visible():
            enter_btn.click()
            return
    except PlaywrightError:
        pass

    # fallback: ищем кнопку Войти рядом с именем комнаты
    enter_by_name = page.locator(f"xpath=//*[contains(normalize-space(), '{room_name}')]/following::button[contains(@class,'enter-button')][1]").first
    try:
        enter_by_name.wait_for(state="visible", timeout=8_000)
        enter_by_name.click()
        return
    except PlaywrightError:
        pass

    raise AssertionError(f"Не удалось войти в комнату с именем: {room_name}")



def _ensure_auto_call_disabled(page):
    _first_visible(page, JOIN_SETTINGS).click()

    checkbox = page.locator(
        "xpath=//div[contains(normalize-space(), 'Вызывать участников при начале сессии комнаты')]/ancestor::label[1]//input[@type='checkbox']"
    ).first

    try:
        if checkbox.count() > 0 and checkbox.is_checked():
            _first_visible(page, AUTO_CALL_CHECKBOX).click()
    except PlaywrightError:
        # fallback: кликаем по лейблу и продолжаем
        _first_visible(page, AUTO_CALL_CHECKBOX).click()


def _assert_no_connect_prompt(page, timeout_ms: int = 12_000):
    connect_locator = page.locator(CONNECT_BUTTON).first
    page.wait_for_timeout(timeout_ms)
    try:
        if connect_locator.count() > 0 and connect_locator.is_visible():
            raise AssertionError("У пользователя 2 появился вызов 'Подключиться', хотя автовызов должен быть выключен")
    except PlaywrightError:
        pass

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("48")
def test_48_create_room_and_join_second_user(two_users):
    page_a = two_users["a"]
    page_a1 = two_users["a1"]

    assert config.ADMIN_EMAIL and config.ADMIN_PASSWORD, "Не заданы ADMIN_EMAIL/ADMIN_PASSWORD"
    assert config.TEST_USER2_EMAIL and config.TEST_USER2_PASSWORD, "Не заданы TEST_USER2_EMAIL/TEST_USER2_PASSWORD"

    LoginFlow(page_a).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    LoginFlow(page_a1).login(config.TEST_USER2_EMAIL, config.TEST_USER2_PASSWORD, expect_success=True)

    room_ui = EventPage(page_a)

    _open_rooms(page_a)
    _click_rooms_plus(page_a)

    room_name = f"тест 48 {int(time.time())}"

    # Если панель не раскрылась автоматически после '+', открываем первую новую комнату.
    first_room_title = page_a.locator("text=Новая комната").first
    if first_room_title.is_visible(timeout=5_000):
        first_room_title.click()

    room_ui.set_event_name(room_name)

    _first_visible(page_a, JOIN_SETTINGS).click()
    _first_visible(page_a, AUTO_CALL_CHECKBOX).click()

    _add_user_to_room(page_a, config.TEST_USER2_EMAIL)

    _finalize_room_creation_if_needed(page_a)
    room_ui.search_event_in_list(room_name)
    _first_visible(page_a, f"text={room_name}", timeout_ms=20_000)

    _enter_room_by_name(page_a, room_name)
    _first_visible(page_a1, CONNECT_BUTTON, timeout_ms=30_000).click()

    page_a1.wait_for_function(
        """() => {
            const href = window.location.href || '';
            return href.includes('/v2/iva/home/') && href.includes('conferenceSessionId=');
        }""",
        timeout=30_000,
    )

    final_url = page_a1.url or ""
    assert "/v2/iva/home/" in final_url and "conferenceSessionId=" in final_url, (
        f"У пользователя 2 не открылась сессия комнаты после подключения. URL: {final_url}"
    )


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("49")
def test_49_room_without_auto_call_second_user_not_called(two_users):
    page_a = two_users["a"]
    page_a1 = two_users["a1"]

    assert config.ADMIN_EMAIL and config.ADMIN_PASSWORD, "Не заданы ADMIN_EMAIL/ADMIN_PASSWORD"
    assert config.TEST_USER2_EMAIL and config.TEST_USER2_PASSWORD, "Не заданы TEST_USER2_EMAIL/TEST_USER2_PASSWORD"

    LoginFlow(page_a).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    LoginFlow(page_a1).login(config.TEST_USER2_EMAIL, config.TEST_USER2_PASSWORD, expect_success=True)

    room_ui = EventPage(page_a)

    _open_rooms(page_a)
    _click_rooms_plus(page_a)

    room_name = f"тест 49 {int(time.time())}"

    first_room_title = page_a.locator("text=Новая комната").first
    if first_room_title.is_visible(timeout=5_000):
        first_room_title.click()

    room_ui.set_event_name(room_name)

    _ensure_auto_call_disabled(page_a)

    _add_user_to_room(page_a, config.TEST_USER2_EMAIL)

    _finalize_room_creation_if_needed(page_a)
    room_ui.search_event_in_list(room_name)
    _first_visible(page_a, f"text={room_name}", timeout_ms=20_000)

    _enter_room_by_name(page_a, room_name)

    _assert_no_connect_prompt(page_a1, timeout_ms=12_000)

    final_url = page_a1.url or ""
    assert "conferenceSessionId=" not in final_url, (
        f"Пользователь 2 не должен был быть вызван автоматически. URL: {final_url}"
    )