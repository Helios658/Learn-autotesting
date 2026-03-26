import pytest
from config import config
from services.login_flow import LoginFlow
from pages.chat_page import ChatPage
from utils.generate_random_message import generate_unique_message


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