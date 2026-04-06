import pytest
import re
from config import config
from services.login_flow import LoginFlow
from pages.chat_page import ChatPage
from utils.generate_random_message import generate_unique_message
import time


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

    candidate_users = [
        config.TEST_USER2_EMAIL,
        config.TEST_LDAP_USER_EMAIL,
        config.TEST_ADFS_USER_EMAIL,
        config.USER_EMAIL,
    ]
    participants = []
    for user in candidate_users:
        if user and user != config.ADMIN_EMAIL and user not in participants:
            participants.append(user)
        if len(participants) == 2:
            break

    assert len(participants) == 2, (
        "Нужно минимум 2 тестовых пользователя для группового чата "
        "(например TEST_USER2_EMAIL и TEST_LDAP_USER_EMAIL)."
    )

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.click_create_chat()
    chat_page.enable_group_chat_mode()

    for user in participants:
        chat_page.search_user_for_new_chat(user)
        chat_page.select_user_checkbox_from_new_chat_results(user)

    with driver.expect_response(
        lambda r: "/api/rest/chats/create-group-chat" in r.url and r.request.method == "POST"
    ) as response_info:
        chat_page.click_create_chat_submit()

    response = response_info.value
    assert response.ok, f"Запрос create-group-chat завершился неуспешно: {response.status}"

    payload = response.json()
    chat_id = payload.get("id")
    assert chat_id, f"В ответе create-group-chat отсутствует id: {payload}"
    assert re.match(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", chat_id, re.IGNORECASE
    ), f"id группового чата не похож на UUID: {chat_id}"

    unique_group_name = f"autotest-group-{chat_id[:8]}"
    chat_page.rename_opened_chat(unique_group_name)