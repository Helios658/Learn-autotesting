from config import config
from pages.base_page import BasePage


class ChatPage(BasePage):
    OPEN_CHATS_TAB = "[e2e-id='shared-core.navigation-menu.chats']"
    CLICK_CREATE_CHAT = "button.iva-round-button[iva-size='s'][iva-color='primary']"
    SEARCH_USER = "input.search-input"

    CREATE_CHAT_CONTAINER_LOCATORS = [
        "app-chat-creation",
        "[class*='chat-creation']",
    ]

    CONTACT_ROW = "app-chat-creation-contact"
    CHAT_HEADER = "app-chat-header"

    def open(self):
        self.page.goto(f"{config.BASE_URL}/v2/iva/home/chats", wait_until="domcontentloaded")
        self.page.locator(self.OPEN_CHATS_TAB).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )

    def click_create_chat(self):
        self.safe_click(self.CLICK_CREATE_CHAT)
        self.get_create_chat_container()

    def get_create_chat_container(self):
        for selector in self.CREATE_CHAT_CONTAINER_LOCATORS:
            locator = self.page.locator(selector).first
            try:
                locator.wait_for(state="visible", timeout=3000)
                return locator
            except Exception:
                continue
        raise AssertionError("Не найден контейнер экрана создания чата")

    def search_user(self, value: str):
        container = self.get_create_chat_container()
        search_input = container.locator(self.SEARCH_USER).first
        search_input.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        search_input.fill("")
        search_input.fill(value)
        self.page.wait_for_timeout(700)

    def select_user_from_results(self, user_text: str):
        container = self.get_create_chat_container()
        rows = container.locator(self.CONTACT_ROW)

        rows.first.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        count = rows.count()
        normalized_target = user_text.strip().lower()

        for i in range(count):
            row = rows.nth(i)
            try:
                if not row.is_visible():
                    continue

                text = row.inner_text().strip()
                lines = [line.strip().lower() for line in text.splitlines() if line.strip()]

                print(f"[search result {i}] {text!r}")

                if normalized_target in lines:
                    self.safe_click(row)
                    return

            except Exception:
                continue

        raise AssertionError(f"Не найден нужный пользователь в результатах поиска: {user_text}")

    def create_or_open_p2p_chat(self, user_text: str):
        self.click_create_chat()
        self.search_user(user_text)
        self.select_user_from_results(user_text)

    def is_p2p_chat_opened(self, user_text: str) -> bool:
        try:
            header = self.page.locator(self.CHAT_HEADER).first
            header.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

            user_locator = header.locator(f"text={user_text}").first
            user_locator.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False