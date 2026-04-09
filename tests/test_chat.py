import pytest
import re
from config import config
from services.login_flow import LoginFlow
from pages.chat_page import ChatPage
from utils.generate_random_message import generate_unique_message
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from services.chat_flow import ChatFlow


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30")
def test_30_create_or_open_p2p_chat_with_test_user2(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.create_or_open_p2p_chat(config.TEST_USER2_EMAIL)

    assert chat_page.is_p2p_chat_opened(config.TEST_USER2_EMAIL), (
        "P2P чат с TEST_USER2 не открылся"
    )


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("31")
def test_31_send_and_receive_text_message_p2p(two_users):
    page_a = two_users["a"]
    page_a1 = two_users["a1"]

    message_text = generate_unique_message("autotest-31")

    LoginFlow(page_a).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    LoginFlow(page_a1).login(config.TEST_USER2_EMAIL, config.TEST_USER2_PASSWORD, expect_success=True)

    chat_a = ChatPage(page_a)
    chat_a1 = ChatPage(page_a1)

    chat_a.open()
    chat_a.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    with page_a.expect_response("**/send-message") as response_info:
        chat_a.send_message(message_text)

    response = response_info.value
    assert response.ok, "Запрос send-message завершился неуспешно"

    payload = response.json()
    assert payload["message"] == message_text, (
        f"В send-message вернулся не тот текст: {payload}"
    )

    chat_a1.open()
    chat_a1.open_existing_p2p_chat_via_search(config.ADMIN_EMAIL)

    assert chat_a1.wait_for_message(message_text), (
        f"A1 не получил сообщение: {message_text}"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("35")
def test_35_create_group_chat_and_capture_chat_id(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    flow = ChatFlow(driver)
    participants = flow.pick_group_participants(required_count=2)
    chat_id = flow.create_group_chat(participants)

    chat_page = flow.chat_page
    unique_group_name = f"autotest-group-{chat_id[:8]}"
    chat_page.rename_opened_chat(unique_group_name)


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("36")
def test_36_convert_existing_p2p_chat_to_group_chat(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    chat_page.create_group_chat_from_opened_p2p()

    participant_to_add = config.TEST_LDAP_USER_EMAIL
    assert participant_to_add, "Для теста 36 должен быть задан TEST_LDAP_USER_EMAIL."
    assert participant_to_add not in {config.ADMIN_EMAIL, config.TEST_USER2_EMAIL}, (
        "TEST_LDAP_USER_EMAIL должен отличаться от ADMIN и TEST_USER2."
    )

    chat_page.search_user_for_new_chat(participant_to_add)
    chat_page.select_user_checkbox_from_new_chat_results(participant_to_add)

    chat_page.click_create_chat_submit()

    driver.locator(chat_page.CHAT_HEADER).first.wait_for(
        state="visible",
        timeout=config.EXPLICIT_WAIT * 1000,
    )

    unique_group_name = f"autotest-converted-{int(time.time())}"
    rename_error = None
    for _ in range(3):
        try:
            chat_page.rename_opened_chat(unique_group_name)
            rename_error = None
            break
        except (PlaywrightTimeoutError, AssertionError) as exc:
            rename_error = exc
            driver.wait_for_timeout(1500)

    assert rename_error is None, (
        f"Не удалось переименовать чат после конвертации p2p->group: {rename_error}"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("37")
def test_37_edit_last_sent_message_p2p(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    original_text = generate_unique_message("autotest-37")
    edited_text = generate_unique_message("autotest-37-edit")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(original_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message завершился неуспешно"
    assert chat_page.wait_for_message(original_text), (
        f"Не удалось дождаться отправленного сообщения: {original_text}"
    )

    chat_page.open_context_menu_for_last_own_message()
    chat_page.click_edit_message_action()

    with driver.expect_response(
        lambda r: "/api/rest/chats/" in r.url and "/messages/" in r.url and r.request.method in ("PUT", "PATCH")
    ) as edit_response_info:
        chat_page.send_message(edited_text)

    edit_response = edit_response_info.value
    assert edit_response.ok, f"Запрос редактирования завершился неуспешно: {edit_response.status}"

    assert chat_page.wait_for_last_own_message_text(edited_text), (
        f"Текст последнего сообщения не обновился до ожидаемого значения: '{edited_text}'"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("38")
def test_38_copy_last_sent_message_and_resend_p2p(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    original_text = generate_unique_message("autotest-38")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(original_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message завершился неуспешно"
    assert chat_page.wait_for_message(original_text), (
        f"Не удалось дождаться отправленного сообщения: {original_text}"
    )

    chat_page.open_context_menu_for_last_own_message()
    chat_page.click_copy_message_action()

    copied_text = chat_page.paste_clipboard_to_message_input()
    assert copied_text == original_text, (
        f"Скопированный текст не совпадает с исходным. "
        f"Ожидалось: '{original_text}', получено: '{copied_text}'"
    )

    with driver.expect_response("**/send-message") as resend_response_info:
        chat_page.click_send()

    resend_response = resend_response_info.value
    assert resend_response.ok, "Запрос повторной отправки сообщения завершился неуспешно"

    payload = resend_response.json()
    assert payload["message"] == original_text, (
        f"В повторном send-message вернулся не тот текст: {payload}"
    )
    assert chat_page.wait_for_last_own_message_text(original_text), (
        "Последнее отправленное сообщение не совпадает со скопированным текстом"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("39")
def test_39_copy_message_link_and_send_p2p(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    original_text = generate_unique_message("gamma.hi-tech.org autotest-39")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(original_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message завершился неуспешно"
    assert chat_page.wait_for_message(original_text), (
        f"Не удалось дождаться отправленного сообщения: {original_text}"
    )

    chat_page.open_context_menu_for_last_own_message()
    chat_page.click_copy_message_link_action()

    copied_link = chat_page.paste_clipboard_to_message_input().strip()
    assert "gamma.hi-tech.org" in copied_link, (
        f"Скопированная ссылка не содержит ожидаемый домен: {copied_link}"
    )

    with driver.expect_response("**/send-message") as resend_response_info:
        chat_page.click_send()

    resend_response = resend_response_info.value
    assert resend_response.ok, "Запрос отправки скопированной ссылки завершился неуспешно"

    payload = resend_response.json()
    assert payload["message"] == copied_link, (
        f"В send-message вернулся не тот текст ссылки: {payload}"
    )
    assert chat_page.wait_for_last_own_message_text(copied_link), (
        "Последнее отправленное сообщение не совпадает со скопированной ссылкой"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("40")
def test_40_delete_last_sent_message_p2p(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    message_text = generate_unique_message("autotest-40")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(message_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message завершился неуспешно"
    assert chat_page.wait_for_message(message_text), (
        f"Не удалось дождаться отправленного сообщения: {message_text}"
    )

    chat_page.open_context_menu_for_last_own_message()

    with driver.expect_response(
        lambda r: (
            "/api/rest/chats/" in r.url
            and (
                ("/messages/" in r.url and r.request.method == "DELETE")
                or ("/messages/remove" in r.url and r.request.method in ("POST", "DELETE"))
            )
        )
    ) as delete_response_info:
        chat_page.click_delete_message_action()
        chat_page.try_confirm_delete_message_action(timeout_ms=3500)

    delete_response = delete_response_info.value
    assert delete_response.ok, f"Запрос удаления сообщения завершился неуспешно: {delete_response.status}"
    assert chat_page.wait_for_message_absent(message_text), (
        f"Сообщение не удалилось из списка сообщений: {message_text}"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("41")
def test_41_clear_p2p_chat(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    chat_page.click_clear_chat()

    with driver.expect_response(
        lambda r: (
            "/api/rest/chats/" in r.url
            and "/clear-history" in r.url
            and r.request.method == "POST"
        )
    ) as clear_response_info:
        chat_page.confirm_clear_chat()

    response = clear_response_info.value

    assert response.ok, f"Очистка чата завершилась неуспешно: status={response.status}, url={response.url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("42")
def test_42_clear_group_chat(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    flow = ChatFlow(driver)
    participants = flow.pick_group_participants(required_count=2)
    chat_id = flow.create_group_chat(participants)
    chat_page = flow.chat_page

    chat_page.click_clear_chat()

    with driver.expect_response(
        lambda r: (
            "/api/rest/chats/" in r.url
            and "/clear-history" in r.url
            and r.request.method == "POST"
        )
    ) as clear_response_info:
        chat_page.confirm_clear_chat()

    response = clear_response_info.value

    assert response.ok, f"Очистка чата завершилась неуспешно: status={response.status}, url={response.url}"

    unique_group_name = f"autotest-group-{chat_id[:8]}"
    chat_page.rename_opened_chat(unique_group_name)