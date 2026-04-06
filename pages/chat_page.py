from config import config
from pages.base_page import BasePage
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import re

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
    CREATE_CHAT_SUBMIT_BUTTON = "button.iva-button:has-text('Создать чат')"
    GROUP_CHAT_TOGGLE_INPUT = "iva-toggle input[type='checkbox'][role='switch']"

    # Поиск по списку чатов слева
    CHAT_SEARCH_BUTTON = "[e2e-id='contacts-header__search-btn']"
    CHAT_SEARCH_INPUT = "input.search-input[placeholder='Поиск чатов']"

    # Список чатов
    CHAT_LIST_ITEM = "app-chats-list-item"
    CHAT_CARD = "div.chat-card"
    CHAT_CARD_TITLE = "h3.chat-card__title"

    # Открытый чат справа
    CHAT_HEADER = "app-chat-header"
    CHAT_HEADER_INFO = ".chat-header__info"
    CHAT_HEADER_TITLE = ".chat-header__description-title"
    MESSAGE_LIST = "app-chat-message-list"
    CHAT_EDITABLE_TITLE_CONTAINER = ".editable-text-container"
    CHAT_EDIT_ICON = ".editable-text-container .edit-icon"
    CHAT_EDITABLE_TEXT = ".editable-text-container .text.word-break"
    CHAT_TITLE_INPUT_CANDIDATES = (
        ".editable-text-container input",
        ".editable-text-container textarea",
        "input[placeholder*='Название']",
        "input[placeholder*='название']",
        "[contenteditable='true']",
    )

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
            except PlaywrightTimeoutError:
                continue
        raise AssertionError("Не найден контейнер экрана создания чата")

    def search_user_for_new_chat(self, value: str):
        container = self.get_create_chat_container()
        search_input = container.locator(self.CREATE_CHAT_SEARCH_INPUT).first
        search_input.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        search_input.fill("")
        search_input.fill(value)
        container.locator(self.CREATE_CHAT_CONTACT).first.wait_for(
            state="visible",
            timeout=config.EXPLICIT_WAIT * 1000,
        )

    def select_user_from_new_chat_results(self, user_text: str):
        container = self.get_create_chat_container()
        rows = container.locator(self.CREATE_CHAT_CONTACT)

        rows.first.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        normalized_target = self._normalize_chat_text(user_text)
        local_part = normalized_target.split("@")[0] if "@" in normalized_target else normalized_target

        exact_email_candidates = []
        contains_email_candidates = []
        local_part_candidates = []

        total = rows.count()
        for idx in range(total):
            row = rows.nth(idx)
            try:
                if not row.is_visible():
                    continue
                row_text = self._normalize_chat_text(row.inner_text(timeout=1000))
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

            if not row_text:
                continue

            if normalized_target and row_text == normalized_target:
                exact_email_candidates.append(row)
                continue

            if normalized_target and re.search(rf"(^|\W){re.escape(normalized_target)}($|\W)", row_text):
                contains_email_candidates.append(row)
                continue

            if local_part and local_part != normalized_target and re.search(
                rf"(^|\W){re.escape(local_part)}($|\W)", row_text
            ):
                local_part_candidates.append(row)

        for candidates in (exact_email_candidates, contains_email_candidates, local_part_candidates):
            if candidates:
                self.safe_click(candidates[0])
                return

        # Fallback: в некоторых сборках inner_text у строк пустой/урезанный,
        # но has_text-фильтрация Playwright всё равно находит корректный контакт.
        for text in (user_text, normalized_target, local_part):
            if not text:
                continue
            candidate = rows.filter(has_text=text).first
            try:
                if candidate.count() > 0 and candidate.is_visible():
                    self.safe_click(candidate)
                    return
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

    def create_or_open_p2p_chat(self, user_text: str):
        self.click_create_chat()
        self.search_user_for_new_chat(user_text)
        self.select_user_from_new_chat_results(user_text)

        header = self.page.locator(self.CHAT_HEADER).first
        header.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

    def enable_group_chat_mode(self):
        container = self.get_create_chat_container()
        toggle_input = container.locator(self.GROUP_CHAT_TOGGLE_INPUT).first
        toggle_input.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        if toggle_input.is_checked():
            return self

        click_targets = [
            toggle_input.locator("xpath=ancestor::label[1]").first,
            container.locator("iva-toggle .layout").first,
            container.locator("iva-toggle .bar-container").first,
            toggle_input,
        ]

        for target in click_targets:
            try:
                self.safe_click(target)
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

            self.page.wait_for_timeout(150)
            try:
                if toggle_input.is_checked():
                    return self
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

        raise AssertionError("Не удалось включить тогл 'Групповой чат'")
        return self

    def select_user_checkbox_from_new_chat_results(self, user_text: str):
        container = self.get_create_chat_container()
        row = container.locator(self.CREATE_CHAT_CONTACT).filter(has_text=user_text).first
        row.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        def _is_selected() -> bool:
            checkbox_input = row.locator("input[type='checkbox']").first
            try:
                if checkbox_input.count() > 0 and checkbox_input.is_checked():
                    return True
            except (PlaywrightError, PlaywrightTimeoutError):
                pass

            try:
                aria_checked = (
                    row.locator("iva-checkbox").first.get_attribute("aria-checked") or ""
                ).lower()
                if aria_checked == "true":
                    return True
            except (PlaywrightError, PlaywrightTimeoutError):
                pass

            return False

        if _is_selected():
            return self

        click_targets = [
            row.locator("iva-checkbox .iva-checkbox_frame").first,
            row.locator("iva-checkbox label").first,
            row,
        ]

        for target in click_targets:
            try:
                self.safe_click(target)
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

            self.page.wait_for_timeout(120)
            if _is_selected():
                return self

        raise AssertionError(f"Не удалось выбрать чекбокс пользователя в списке: {user_text}")
        return self

    def click_create_chat_submit(self):
        container = self.get_create_chat_container()
        submit_button = container.locator(self.CREATE_CHAT_SUBMIT_BUTTON).first
        submit_button.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(submit_button)
        return self

    def rename_opened_chat(self, new_name: str):
        header = self.page.locator(self.CHAT_HEADER).first
        header.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        try:
            self.safe_click(self.CHAT_HEADER_INFO)
        except (PlaywrightError, PlaywrightTimeoutError):
            pass

        editable_container = self.page.locator(self.CHAT_EDITABLE_TITLE_CONTAINER).first
        editable_container.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        edit_icon = self.page.locator(self.CHAT_EDIT_ICON).first
        try:
            if edit_icon.count() > 0 and edit_icon.is_visible():
                self.safe_click(edit_icon)
                self.page.wait_for_timeout(150)
        except (PlaywrightError, PlaywrightTimeoutError):
            pass

        for selector in self.CHAT_TITLE_INPUT_CANDIDATES:
            input_locator = self.page.locator(selector).first
            try:
                if input_locator.count() == 0:
                    continue
                input_locator.wait_for(state="visible", timeout=1200)
                input_locator.fill("")
                input_locator.fill(new_name)
                input_locator.press("Enter")
                break
            except (PlaywrightError, PlaywrightTimeoutError):
                continue
        else:
            try:
                text_node = self.page.locator(self.CHAT_EDITABLE_TEXT).first
                text_node.wait_for(state="visible", timeout=1500)
                self.safe_click(text_node)
                try:
                    text_node.dblclick(timeout=1200)
                except (PlaywrightError, PlaywrightTimeoutError):
                    pass

                self.page.keyboard.press("Control+A")
                self.page.keyboard.type(new_name)
                self.page.keyboard.press("Enter")
            except (PlaywrightError, PlaywrightTimeoutError):
                raise AssertionError("Не удалось найти поле ввода названия группового чата")

        self.page.locator(self.CHAT_HEADER_TITLE).filter(has_text=new_name).first.wait_for(
            state="visible",
            timeout=config.EXPLICIT_WAIT * 1000,
        )
        return self

    @staticmethod
    def _normalize_chat_text(value: str) -> str:
        return (value or "").strip().strip('"').strip("'").lower()

    # =========================
    # Открытие существующего чата через поиск по списку
    # =========================
    def open_existing_p2p_chat_via_search(self, user_text: str):
        self.safe_click(self.CHAT_SEARCH_BUTTON)

        search_input = self.page.locator(self.CHAT_SEARCH_INPUT).first
        search_input.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        search_input.fill("")
        search_input.fill(user_text)
        self.page.locator(self.CHAT_LIST_ITEM).first.wait_for(
            state="visible",
            timeout=config.EXPLICIT_WAIT * 1000,
        )

        row = self.page.locator(self.CHAT_LIST_ITEM).filter(
            has=self.page.locator(f"mark.highlighted:has-text('{user_text}')")
        ).first

        try:
            row.wait_for(state="visible", timeout=3000)
        except PlaywrightTimeoutError:
            row = self.page.locator(self.CHAT_LIST_ITEM).filter(
                has=self.page.locator(f"{self.CHAT_CARD_TITLE}:has-text('{user_text}')")
            ).first
            row.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        card = row.locator(self.CHAT_CARD).first
        card.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(card)

        header = self.page.locator(self.CHAT_HEADER).first
        header.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

    def open_most_recent_chat_from_list(self):
        first_chat = self.page.locator(self.CHAT_LIST_ITEM).first
        first_chat.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        card = first_chat.locator(self.CHAT_CARD).first
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
        except (PlaywrightError, PlaywrightTimeoutError):
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
            except PlaywrightError:
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
        except (PlaywrightError, PlaywrightTimeoutError):
            return False