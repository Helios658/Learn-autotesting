import pytest
from config import config
from services.login_flow import LoginFlow
from pages.chat_page import ChatPage


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30")
def test_30_create_or_open_p2p_chat_with_test_user2(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.create_or_open_p2p_chat(config.TEST_USER2_EMAIL)

    assert chat_page.is_p2p_chat_opened(config.TEST_USER2_EMAIL), \
        "P2P чат с TEST_USER2 не открылся"