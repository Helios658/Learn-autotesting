import re
from config import config
from pages.chat_page import ChatPage

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class ChatFlow:
    def __init__(self, driver):
        self.driver = driver
        self.chat_page = ChatPage(driver)

    def pick_group_participants(self, required_count: int = 2) -> list[str]:
        candidate_users = [
            config.TEST_USER2_EMAIL,
            config.TEST_LDAP_USER_EMAIL,
            config.TEST_ADFS_USER_EMAIL,
            config.USER_EMAIL,
        ]

        participants: list[str] = []
        for user in candidate_users:
            if user and user != config.ADMIN_EMAIL and user not in participants:
                participants.append(user)
            if len(participants) == required_count:
                break

        if len(participants) != required_count:
            raise AssertionError(
                "Нужно минимум 2 тестовых пользователя для группового чата "
                "(например TEST_USER2_EMAIL и TEST_LDAP_USER_EMAIL)."
            )
        return participants

    def create_group_chat(self, participants: list[str]) -> str:
        self.chat_page.open()
        self.chat_page.click_create_chat()
        self.chat_page.enable_group_chat_mode()

        for user in participants:
            self.chat_page.search_user_for_new_chat(user)
            self.chat_page.select_user_checkbox_from_new_chat_results(user)

        with self.driver.expect_response(
            lambda r: "/api/rest/chats/create-group-chat" in r.url and r.request.method == "POST"
        ) as response_info:
            self.chat_page.click_create_chat_submit()

        response = response_info.value
        assert response.ok, f"Запрос create-group-chat завершился неуспешно: {response.status}"

        payload = response.json()
        chat_id = payload.get("id")
        assert chat_id, f"В ответе create-group-chat отсутствует id: {payload}"
        assert UUID_RE.match(chat_id), f"id группового чата не похож на UUID: {chat_id}"
        return chat_id