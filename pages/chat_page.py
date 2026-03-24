from config import config
from pages.base_page import BasePage


class ChatPage(BasePage):
    # Навигация
    OPEN_CHATS_TAB = "[e2e-id='shared-core.navigation-menu.chats']"

    # Создание / открытие p2p через "+"
    CLICK_CREATE_CHAT = "button.iva-round-button[iva-size='s'][iva-color='primary']"
    CREATE_CHAT_CONTAINER_LOCATORS = [
        "app-chat-creation",
        "[class*='chat-creation']",
    ]
    CREATE_CHAT_CONTACT = "app-chat-creation-contact"
    CREATE_CHAT_SEARCH_INPUT = "input.search-input"

    # Поиск по списку чатов слева
    CHAT_SEARCH_BUTTON = "[e2e-id='contacts-header__search-btn']"
    CHAT_SEARCH_INPUT = "input.search-input[placeholder='Поиск чатов']"

    # Список чатов
    CHAT_LIST_ITEM = "app-chats-list-item"
    CHAT_CARD = "div.chat-card"
    CHAT_CARD_TITLE = "h3.chat-card__title"

    # Открытый чат справа
    CHAT_HEADER = "app-chat-header"
    MESSAGE_LIST = "app-chat-message-list"

    # Поле ввода и отправка
    MESSAGE_INPUT = "textarea.chat-message-list__textarea"
    SEND_BUTTON = "button.chat-message-list__send-button"

    def open(self):
        self.page.goto(f"{config.BASE_URL}/v2/iva/home/chats", wait_until="domcontentloaded")
        self.page.locator(self.OPEN_CHATS_TAB).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )

    # =========================
    # Создание / открытие p2p через "+"
    # =========================
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

    def search_user_for_new_chat(self, value: str):
        container = self.get_create_chat_container()
        search_input = container.locator(self.CREATE_CHAT_SEARCH_INPUT).first
        search_input.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        search_input.fill("")
        search_input.fill(value)
        self.page.wait_for_timeout(700)

    def select_user_from_new_chat_results(self, user_text: str):
        container = self.get_create_chat_container()
        rows = container.locator(self.CREATE_CHAT_CONTACT)

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

                print(f"[new chat result {i}] {text!r}")

                if normalized_target in lines or normalized_target in text.lower():
                    self.safe_click(row)
                    return

            except Exception:
                continue

        raise AssertionError(f"Не найден пользователь в результатах создания чата: {user_text}")

    def create_or_open_p2p_chat(self, user_text: str):
        self.click_create_chat()
        self.search_user_for_new_chat(user_text)
        self.select_user_from_new_chat_results(user_text)

        header = self.page.locator(self.CHAT_HEADER).first
        header.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

    # =========================
    # Открытие существующего чата через поиск по списку
    # =========================
    def open_existing_p2p_chat_via_search(self, user_text: str):
        self.safe_click(self.CHAT_SEARCH_BUTTON)

        search_input = self.page.locator(self.CHAT_SEARCH_INPUT).first
        search_input.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        search_input.fill("")
        search_input.fill(user_text)
        self.page.wait_for_timeout(700)

        row = self.page.locator(self.CHAT_LIST_ITEM).filter(
            has=self.page.locator(f"mark.highlighted:has-text('{user_text}')")
        ).first

        try:
            row.wait_for(state="visible", timeout=3000)
        except Exception:
            row = self.page.locator(self.CHAT_LIST_ITEM).filter(
                has=self.page.locator(f"{self.CHAT_CARD_TITLE}:has-text('{user_text}')")
            ).first
            row.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        card = row.locator(self.CHAT_CARD).first
        card.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(card)

        header = self.page.locator(self.CHAT_HEADER).first
        header.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

    # =========================
    # Проверка открытого p2p чата
    # =========================
    def is_p2p_chat_opened(self, user_text: str) -> bool:
        try:
            header = self.page.locator(self.CHAT_HEADER).first
            header.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
            header.get_by_text(user_text, exact=True).first.wait_for(
                state="visible", timeout=5000
            )
            return True
        except Exception:
            return False

    # =========================
    # Сообщения
    # =========================
    def focus_message_input(self):
        input_locator = self.page.locator(self.MESSAGE_INPUT).first
        input_locator.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        input_locator.click()

    def type_message(self, text: str):
        input_locator = self.page.locator(self.MESSAGE_INPUT).first
        input_locator.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        input_locator.fill("")
        input_locator.fill(text)

    def click_send(self):
        send_button = self.page.locator(self.SEND_BUTTON).first
        send_button.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        for _ in range(20):
            try:
                if send_button.is_enabled():
                    self.safe_click(send_button)
                    return
            except Exception:
                pass

            self.page.wait_for_timeout(200)

        raise AssertionError("Кнопка отправки сообщения не стала активной")

    def send_message(self, text: str):
        self.focus_message_input()
        self.type_message(text)
        self.click_send()

    def wait_for_message(self, text: str, timeout_ms: int = 15000) -> bool:
        try:
            message_list = self.page.locator(self.MESSAGE_LIST).first
            message_list.wait_for(state="visible", timeout=timeout_ms)
            message_list.get_by_text(text, exact=True).last.wait_for(
                state="visible",
                timeout=timeout_ms,
            )
            return True
        except Exception:
            return False