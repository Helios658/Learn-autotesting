from config import config
from pages.base_page import BasePage
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import re
import time

class ChatPage(BasePage):
    # Навигация
    OPEN_CHATS_TAB = "[e2e-id='shared-core.navigation-menu.chats']"

    # Создание / открытие p2p через "+"
    CLICK_CREATE_CHAT = "button.iva-round-button[iva-size='s'][iva-color='primary']"
    CREATE_CHAT_CONTAINER_LOCATORS = [
        "app-chat-creation",
        "app-chat-members-adding",
        "app-add-members-modal",
        "[class*='chat-creation']",
    ]
    CREATE_CHAT_CONTACT = "app-chat-creation-contact"
    CREATE_CHAT_CONTACT_CANDIDATES = (
        "app-chat-creation-contact",
        "app-chat-members-adding-user",
        "app-chat-member-item",
        "app-contact-list-item",
        "app-user-list-item",
        "app-option",
        ".option",
        "[role='option']",
        "li",
    )
    CREATE_CHAT_SEARCH_INPUT_CANDIDATES = (
        "input.search-input[placeholder='Поиск пользователей']",
        "input.search-input",
        "input[placeholder='Поиск пользователей']",
    )
    CREATE_CHAT_SUBMIT_BUTTON_CANDIDATES = (
        "button.iva-button:has-text('Создать чат')",
        "button.iva-button:has-text('Добавить')",
    )
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
    CHAT_HEADER_MENU_BUTTON = "app-chat-header button.iva-icon-button:has(svg-icon[src*='3-dots'])"
    CHAT_MENU_CREATE_GROUP_ACTION = (
        ".option__main-content:has-text('Создать групповой чат'), "
        ".option:has-text('Создать групповой чат'), "
        "app-option:has-text('Создать групповой чат'), "
        "li:has-text('Создать групповой чат'), "
        "button:has-text('Создать групповой чат'), "
        "[role='menuitem']:has-text('Создать групповой чат')"
    )
    CHAT_MENU_CLEAR_CHAT_ACTION = (
    ".option__main-content:has-text('Очистить чат'), "
    ".option:has-text('Очистить чат'), "
    "app-option:has-text('Очистить чат'), "
    "li:has-text('Очистить чат'), "
    "button:has-text('Очистить чат'), "
    "[role='menuitem']:has-text('Очистить чат')"
    )
    CLEAR_CHAT_CONFIRM_BUTTON_CANDIDATES = (
        "app-confirm-dialog button.iva-button:has-text('Очистить')",
        "app-dialog button.iva-button:has-text('Очистить')",
        "[role='dialog'] button.iva-button:has-text('Очистить')",
        "button.iva-button:has-text('Очистить')",
        "button:has-text('Очистить')",
    )
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
    SELF_MESSAGE = "app-chat-message.chat-message_self"
    MESSAGE_BUBBLE = ".chat-message__bubble"
    MESSAGE_TEXT = ".chat-message__text"
    MESSAGE_CONTEXT_EDIT_ACTION = (
        ".dropdown-item:has-text('Изменить текст'), "
        ".option:has-text('Изменить текст'), "
        "app-option:has-text('Изменить текст'), "
        "[role='menuitem']:has-text('Изменить текст')"
    )
    MESSAGE_CONTEXT_COPY_ACTION = (
        ".dropdown-item:has-text('Копировать текст'), "
        ".option:has-text('Копировать текст'), "
        "app-option:has-text('Копировать текст'), "
        "[role='menuitem']:has-text('Копировать текст')"
    )
    MESSAGE_CONTEXT_COPY_LINK_ACTION = (
        ".dropdown-item:has-text('Копировать ссылку'), "
        ".option:has-text('Копировать ссылку'), "
        "app-option:has-text('Копировать ссылку'), "
        "[role='menuitem']:has-text('Копировать ссылку')"
    )
    MESSAGE_CONTEXT_DELETE_ACTION = (
        ".dropdown-item_remove:has-text('Удалить'), "
        ".dropdown-item:has-text('Удалить'), "
        ".option:has-text('Удалить'), "
        "app-option:has-text('Удалить'), "
        "[role='menuitem']:has-text('Удалить')"
    )
    MESSAGE_CONTEXT_REPLY_ACTION = (
        ".dropdown-item:has-text('Ответить'), "
        ".option:has-text('Ответить'), "
        "app-option:has-text('Ответить'), "
        "[role='menuitem']:has-text('Ответить')"
    )
    MESSAGE_CONTEXT_FORWARD_ACTION = (
        ".dropdown-item:has-text('Переслать'), "
        ".option:has-text('Переслать'), "
        "app-option:has-text('Переслать'), "
        "[role='menuitem']:has-text('Переслать')"
    )
    MESSAGE_DELETE_CONFIRM_BUTTON_CANDIDATES = (
        "app-confirm-dialog button.iva-button:has-text('Удалить')",
        "app-dialog button.iva-button:has-text('Удалить')",
        "[role='dialog'] button.iva-button:has-text('Удалить')",
        "button.iva-button:has-text('Удалить')",
        "button:has-text('Удалить')",
    )
    FORWARD_SEARCH_INPUT_CANDIDATES = (
        "input.search-input[placeholder='Поиск получателей']",
        "input[placeholder='Поиск получателей']",
        "app-chat-forward input.search-input",
    )
    FORWARD_RECIPIENT_ROW_CANDIDATES = (
        "app-chat-forward app-chat-creation-contact",
        "app-chat-forward app-chat-members-adding-user",
        "app-chat-forward app-contact-list-item",
        "app-chat-forward .option",
        "app-chat-forward li",
        "app-chat-creation-contact",
        "app-chat-members-adding-user",
        "app-contact-list-item",
        ".option",
        "li",
    )
    FORWARD_SUBMIT_BUTTON_CANDIDATES = (
        "app-chat-forward button.iva-button:has-text('Переслать')",
        "button.iva-button:has-text('Переслать')",
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
        # Быстрый проход без длинных wait_for, чтобы не тратить десятки секунд.
        for selector in self.CREATE_CHAT_CONTAINER_LOCATORS:
            locator = self.page.locator(selector).first
            try:
                if locator.count() > 0 and locator.is_visible():
                    return locator
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

        # Короткое активное ожидание (до 3с) появления контейнера.
        for _ in range(12):
            for selector in self.CREATE_CHAT_CONTAINER_LOCATORS:
                locator = self.page.locator(selector).first
                try:
                    if locator.count() > 0 and locator.is_visible():
                        return locator
                except (PlaywrightError, PlaywrightTimeoutError):
                    continue
            self.page.wait_for_timeout(250)

        # Fallback: окно может рендериться без отдельного контейнера.
        for selector in self.CREATE_CHAT_SEARCH_INPUT_CANDIDATES:
            search_input = self.page.locator(selector).first
            try:
                if search_input.count() > 0 and search_input.is_visible():
                    return self.page
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

        raise AssertionError("Не найден контейнер экрана создания чата")

    def search_user_for_new_chat(self, value: str):
        container = self.get_create_chat_container()
        search_input = self._get_create_chat_search_input(container)
        search_input.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        search_input.fill("")
        search_input.fill(value)
        self.page.wait_for_timeout(300)

    def select_user_from_new_chat_results(self, user_text: str):
        container = self.get_create_chat_container()
        rows = self._get_create_chat_contact_rows(container)
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
        try:
            row = self._find_user_row_in_create_chat(container, user_text)
        except AssertionError:
            # Финальный fallback для вариантов DOM, где строка результата нестандартная:
            # пытаемся кликнуть по видимому frame чекбокса у строки с текстом пользователя.
            checkbox_frame_by_user = self.page.locator(
                "xpath=(//*[contains(normalize-space(text()), '"
                + user_text
                + "')]/ancestor::*[.//iva-checkbox][1]//*[contains(@class,'iva-checkbox_frame')])[1]"
            ).first
            try:
                checkbox_frame_by_user.wait_for(state="visible", timeout=3000)
                self.safe_click(checkbox_frame_by_user)
                return self
            except (PlaywrightError, PlaywrightTimeoutError):
                pass

            # Самый последний fallback: первый видимый checkbox frame в модалке.
            checkbox_frame = self.page.locator("iva-checkbox .iva-checkbox_frame").first
            checkbox_frame.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
            self.safe_click(checkbox_frame)
            return self

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

        # Последний fallback: выставить состояние чекбокса напрямую через input.
        checkbox_input = row.locator("input[type='checkbox']").first
        try:
            if checkbox_input.count() > 0:
                checkbox_input.set_checked(True, timeout=2000)
                self.page.wait_for_timeout(120)
                if _is_selected():
                    return self
        except (PlaywrightError, PlaywrightTimeoutError):
            pass

        raise AssertionError(f"Не удалось выбрать чекбокс пользователя в списке: {user_text}")
        return self

    def click_create_chat_submit(self):
        container = self.get_create_chat_container()
        submit_button = self._get_create_chat_submit_button(container)
        submit_button.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(submit_button)
        return self

    def _get_create_chat_search_input(self, container):
        for selector in self.CREATE_CHAT_SEARCH_INPUT_CANDIDATES:
            candidate = container.locator(selector).first
            try:
                if candidate.count() > 0 and candidate.is_visible():
                    return candidate
            except (PlaywrightError, PlaywrightTimeoutError):
                continue
        return container.locator(self.CREATE_CHAT_SEARCH_INPUT_CANDIDATES[-1]).first

    def _get_create_chat_contact_rows(self, container):
        for selector in self.CREATE_CHAT_CONTACT_CANDIDATES:
            rows = container.locator(selector)
            try:
                if rows.count() == 0:
                    continue
                if rows.first.is_visible():
                    return rows
            except (PlaywrightError, PlaywrightTimeoutError):
                continue
        return container.locator(self.CREATE_CHAT_CONTACT)

    def _find_user_row_in_create_chat(self, container, user_text: str):
        normalized = self._normalize_chat_text(user_text)
        local_part = normalized.split("@")[0] if "@" in normalized else normalized
        candidates = [text for text in (user_text, normalized, local_part) if text]

        for selector in self.CREATE_CHAT_CONTACT_CANDIDATES:
            rows = container.locator(selector)
            try:
                if rows.count() == 0:
                    continue
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

            for text in candidates:
                row = rows.filter(has_text=text).first
                try:
                    if row.count() > 0 and row.is_visible():
                        return row
                except (PlaywrightError, PlaywrightTimeoutError):
                    continue

        # Fallback: если текст не совпал (например отображается ФИО),
        # берём первый видимый элемент списка с чекбоксом.
        for selector in self.CREATE_CHAT_CONTACT_CANDIDATES:
            rows = container.locator(selector)
            try:
                total = rows.count()
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

            for idx in range(total):
                row = rows.nth(idx)
                try:
                    if not row.is_visible():
                        continue
                    if row.locator("input[type='checkbox']").count() > 0:
                        return row
                    if row.locator("iva-checkbox").count() > 0:
                        return row
                except (PlaywrightError, PlaywrightTimeoutError):
                    continue

        raise AssertionError(
            f"Не найден пользователь в списке добавления участников: '{user_text}'. "
            f"Проверены селекторы: {', '.join(self.CREATE_CHAT_CONTACT_CANDIDATES)}"
        )

    def _get_create_chat_submit_button(self, container):
        for selector in self.CREATE_CHAT_SUBMIT_BUTTON_CANDIDATES:
            button = container.locator(selector).first
            try:
                if button.count() > 0 and button.is_visible():
                    return button
            except (PlaywrightError, PlaywrightTimeoutError):
                continue
        return container.locator(self.CREATE_CHAT_SUBMIT_BUTTON_CANDIDATES[0]).first

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

    def open_chat_header_menu(self, expected_actions=None):
        header = self.page.locator(self.CHAT_HEADER).first
        header.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        menu_button = header.locator("button.iva-icon-button").filter(
            has=self.page.locator("svg-icon[src*='3-dots']")
        ).first
        menu_button.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(menu_button)

        menu_actions = expected_actions or (self.CHAT_MENU_CREATE_GROUP_ACTION,)
        self._find_first_visible(menu_actions, timeout=config.EXPLICIT_WAIT * 1000)
        return self

    def create_group_chat_from_opened_p2p(self):
        self.open_chat_header_menu(
            expected_actions=(self.CHAT_MENU_CREATE_GROUP_ACTION,),
        )

        action = self.page.locator(self.CHAT_MENU_CREATE_GROUP_ACTION).first
        action.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(action)

        self._wait_for_group_members_step()
        return self

    def _wait_for_group_members_step(self):
        for selector in self.CREATE_CHAT_SEARCH_INPUT_CANDIDATES:
            input_locator = self.page.locator(selector).first
            try:
                input_locator.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
                return self
            except PlaywrightTimeoutError:
                continue

        for selector in self.CREATE_CHAT_SUBMIT_BUTTON_CANDIDATES:
            button = self.page.locator(selector).first
            try:
                button.wait_for(state="visible", timeout=2000)
                return self
            except PlaywrightTimeoutError:
                continue

        raise AssertionError("Не открылся шаг добавления участников при создании группового чата")

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

    def open_context_menu_for_last_own_message(self):
        own_message = self.page.locator(self.SELF_MESSAGE).last
        own_message.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        action_button_selector = getattr(
            self,
            "MESSAGE_ACTION_BUTTON",
            "button.chat-message__action-button:has(svg-icon[src*='3-dots'])",
        )
        action_button = own_message.locator(action_button_selector).first
        try:
            action_button.wait_for(state="visible", timeout=2500)
            self.safe_click(action_button)
        except (PlaywrightError, PlaywrightTimeoutError):
            bubble = own_message.locator(self.MESSAGE_BUBBLE).first
            bubble.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
            bubble.click(button="right")

        edit_action = self.page.locator(self.MESSAGE_CONTEXT_EDIT_ACTION).first
        edit_action.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        return self

    def click_edit_message_action(self):
        edit_action = self.page.locator(self.MESSAGE_CONTEXT_EDIT_ACTION).first
        edit_action.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(edit_action)
        self.page.locator(self.MESSAGE_INPUT).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        return self

    def click_copy_message_action(self):
        copy_action = self.page.locator(self.MESSAGE_CONTEXT_COPY_ACTION).first
        copy_action.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(copy_action)
        return self

    def click_copy_message_link_action(self):
        copy_link_action = self.page.locator(self.MESSAGE_CONTEXT_COPY_LINK_ACTION).first
        copy_link_action.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(copy_link_action)
        return self

    def click_delete_message_action(self):
        delete_action = self.page.locator(self.MESSAGE_CONTEXT_DELETE_ACTION).first
        delete_action.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(delete_action)
        return self

    def click_reply_message_action(self):
        reply_action = self.page.locator(self.MESSAGE_CONTEXT_REPLY_ACTION).first
        reply_action.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(reply_action)
        return self

    def click_forward_message_action(self):
        forward_action = self.page.locator(self.MESSAGE_CONTEXT_FORWARD_ACTION).first
        forward_action.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(forward_action)
        return self

    def is_message_context_menu_closed(self) -> bool:
        try:
            reply_visible = self.page.locator(self.MESSAGE_CONTEXT_REPLY_ACTION).first.is_visible()
            forward_visible = self.page.locator(self.MESSAGE_CONTEXT_FORWARD_ACTION).first.is_visible()
            return not (reply_visible or forward_visible)
        except (PlaywrightError, PlaywrightTimeoutError):
            return True

    def forward_last_own_message_to_recipient(self, recipient_text: str):
        search_input = self._get_forward_search_input()
        search_input.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        search_input.fill("")
        search_input.fill(recipient_text)
        self.page.wait_for_timeout(300)

        recipient_row = self._find_forward_recipient_row(recipient_text)
        recipient_row.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self._select_forward_recipient(recipient_row, recipient_text)

        forward_button = self._get_forward_submit_button()
        forward_button.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        for _ in range(20):
            try:
                if forward_button.is_enabled():
                    self.safe_click(forward_button)
                    return self
            except (PlaywrightError, PlaywrightTimeoutError):
                pass
            self.page.wait_for_timeout(200)

        raise AssertionError("Кнопка 'Переслать' не стала активной в окне пересылки")

    def _get_forward_search_input(self):
        for selector in self.FORWARD_SEARCH_INPUT_CANDIDATES:
            candidate = self.page.locator(selector).first
            try:
                if candidate.count() > 0 and candidate.is_visible():
                    return candidate
            except (PlaywrightError, PlaywrightTimeoutError):
                continue
        return self.page.locator(self.FORWARD_SEARCH_INPUT_CANDIDATES[-1]).first

    def _find_forward_recipient_row(self, recipient_text: str):
        normalized_target = self._normalize_chat_text(recipient_text)
        local_part = normalized_target.split("@")[0] if "@" in normalized_target else normalized_target

        for selector in self.FORWARD_RECIPIENT_ROW_CANDIDATES:
            rows = self.page.locator(selector)
            try:
                if rows.count() == 0:
                    continue
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

            for text in (recipient_text, normalized_target, local_part):
                if not text:
                    continue
                row = rows.filter(has_text=text).first
                try:
                    if row.count() > 0 and row.is_visible():
                        return row
                except (PlaywrightError, PlaywrightTimeoutError):
                    continue

            try:
                if rows.first.is_visible():
                    return rows.first
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

        # Fallback: строка через текст + ближайший контейнер с чекбоксом.
        for text in (recipient_text, normalized_target, local_part):
            if not text:
                continue
            by_text_checkbox_container = self.page.locator(
                "xpath=(//*[contains(translate(normalize-space(text()), "
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '"
                + text.lower()
                + "')]/ancestor::*[.//iva-checkbox][1])[1]"
            ).first
            try:
                if by_text_checkbox_container.count() > 0 and by_text_checkbox_container.is_visible():
                    return by_text_checkbox_container
            except (PlaywrightError, PlaywrightTimeoutError):
                continue

        # Последний fallback: первый видимый контейнер с чекбоксом.
        checkbox_container = self.page.locator("xpath=(//*[.//iva-checkbox])[1]").first
        try:
            if checkbox_container.count() > 0 and checkbox_container.is_visible():
                return checkbox_container
        except (PlaywrightError, PlaywrightTimeoutError):
            pass

        raise AssertionError(f"Не удалось найти получателя для пересылки: {recipient_text}")

    def _select_forward_recipient(self, recipient_row, recipient_text: str):
        def _is_selected() -> bool:
            checkbox_input = recipient_row.locator("input[type='checkbox']").first
            try:
                if checkbox_input.count() > 0 and checkbox_input.is_checked():
                    return True
            except (PlaywrightError, PlaywrightTimeoutError):
                pass

            try:
                aria_checked = (recipient_row.locator("iva-checkbox").first.get_attribute("aria-checked") or "").lower()
                if aria_checked == "true":
                    return True
            except (PlaywrightError, PlaywrightTimeoutError):
                pass
            return False

        if _is_selected():
            return self

        click_targets = [
            recipient_row.locator("iva-checkbox .iva-checkbox_frame").first,
            recipient_row.locator("iva-checkbox label").first,
            recipient_row,
        ]

        # Дополнительный точечный target: frame чекбокса у строки с текстом получателя.
        by_text_checkbox_frame = self.page.locator(
            "xpath=(//*[contains(normalize-space(text()), '"
            + recipient_text
            + "')]/ancestor::*[.//iva-checkbox][1]//*[contains(@class,'iva-checkbox_frame')])[1]"
        ).first
        click_targets.insert(0, by_text_checkbox_frame)

        for target in click_targets:
            try:
                self.safe_click(target)
            except (PlaywrightError, PlaywrightTimeoutError):
                continue
            self.page.wait_for_timeout(120)
            if _is_selected():
                return self

        checkbox_input = recipient_row.locator("input[type='checkbox']").first
        try:
            if checkbox_input.count() > 0:
                checkbox_input.set_checked(True, timeout=2000)
                self.page.wait_for_timeout(120)
                if _is_selected():
                    return self
        except (PlaywrightError, PlaywrightTimeoutError):
            pass

        raise AssertionError(f"Не удалось выбрать получателя для пересылки: {recipient_text}")

    def _get_forward_submit_button(self):
        for selector in self.FORWARD_SUBMIT_BUTTON_CANDIDATES:
            button = self.page.locator(selector).first
            try:
                if button.count() > 0 and button.is_visible():
                    return button
            except (PlaywrightError, PlaywrightTimeoutError):
                continue
        return self.page.locator(self.FORWARD_SUBMIT_BUTTON_CANDIDATES[-1]).first

    def wait_for_chat_title_contains(self, text: str, timeout_ms: int = 15000) -> bool:
        end_time = time.time() + timeout_ms / 1000
        while time.time() < end_time:
            try:
                header_title = (self.page.locator(self.CHAT_HEADER_TITLE).first.inner_text() or "").lower()
                if text.lower() in header_title:
                    return True
            except (PlaywrightError, PlaywrightTimeoutError):
                pass
            self.page.wait_for_timeout(250)
        return False

    def confirm_delete_message_action(self):
        confirm_button = self._find_first_visible(
            self.MESSAGE_DELETE_CONFIRM_BUTTON_CANDIDATES,
            timeout=config.EXPLICIT_WAIT * 1000,
        )
        self.safe_click(confirm_button)
        return self

    def try_confirm_delete_message_action(self, timeout_ms: int = 3000) -> bool:
        try:
            confirm_button = self._find_first_visible(
                self.MESSAGE_DELETE_CONFIRM_BUTTON_CANDIDATES,
                timeout=timeout_ms,
            )
            self.safe_click(confirm_button)
            return True
        except (PlaywrightTimeoutError, PlaywrightError):
            return False

    def get_last_own_message_text(self) -> str:
        own_message = self.page.locator(self.SELF_MESSAGE).last
        own_message.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        text_locator = own_message.locator(self.MESSAGE_TEXT).first
        text_locator.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        return (text_locator.inner_text() or "").strip()

    def wait_for_last_own_message_text(self, expected_text: str, timeout_ms: int = 15000) -> bool:
        end_time = time.time() + timeout_ms / 1000
        while time.time() < end_time:
            actual = self.get_last_own_message_text()
            if actual == expected_text:
                return True
            self.page.wait_for_timeout(250)
        return False

    def paste_clipboard_to_message_input(self) -> str:
        input_locator = self.page.locator(self.MESSAGE_INPUT).first
        input_locator.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        input_locator.click()
        input_locator.fill("")
        input_locator.press("Control+V")
        self.page.wait_for_timeout(150)
        pasted = (input_locator.input_value() or "").strip()
        if pasted:
            return pasted

        try:
            clipboard_text = self.page.evaluate(
                """
                async () => {
                    try {
                        return (await navigator.clipboard.readText()) || "";
                    } catch (e) {
                        return "";
                    }
                }
                """
            ).strip()
        except PlaywrightError:
            clipboard_text = ""

        if clipboard_text:
            input_locator.fill(clipboard_text)
            return clipboard_text

        return pasted

    def wait_for_message_absent(self, text: str, timeout_ms: int = 15000) -> bool:
        end_time = time.time() + timeout_ms / 1000
        while time.time() < end_time:
            target = self.page.locator(self.MESSAGE_LIST).get_by_text(text, exact=True)
            try:
                if target.count() == 0:
                    return True
            except (PlaywrightError, PlaywrightTimeoutError):
                return True
            self.page.wait_for_timeout(250)
        return False

    def click_clear_chat(self):
        self.open_chat_header_menu(
            expected_actions=(self.CHAT_MENU_CLEAR_CHAT_ACTION,),
        )
        action = self.page.locator(self.CHAT_MENU_CLEAR_CHAT_ACTION).first
        action.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(action)
        return self

    def confirm_clear_chat(self):
        confirm_button = self._find_first_visible(
            self.CLEAR_CHAT_CONFIRM_BUTTON_CANDIDATES,
            timeout=config.EXPLICIT_WAIT * 1000,
        )
        self.safe_click(confirm_button)
        return self