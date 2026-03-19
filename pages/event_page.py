from config import config
from pages.base_page import BasePage


class EventPage(BasePage):
    CONFERENCES_TAB = "[e2e-id='shared-core.navigation-menu.conferences']"
    ADD_BUTTON = "[e2e-id='ADD']"

    TEMPLATE_GROUPS_CARD = (
        "xpath=//div[contains(@class, 'conference-card')]"
        "[.//h4[contains(@class, 'conference-name') and normalize-space()='Деление участников на группы']]"
    )

    SETTINGS_MODAL_BUTTON = "xpath=//span[text()=' Войти ']/parent::button"
    CLOSE_MODAL_BUTTON = "button.close-button.iva-icon-button"

    EVENT_LIST_SCROLLER = "virtual-scroller.selfScroll"
    HAMBURGER_BUTTON = "button.hamburger.iva-icon-button"
    CONFERENCES_TAB_SETTINGS_LOCATORS = [
        "[e2e-id='conference-tab__settings']",
        "button[e2e-id='conference-tab__settings']",
        "[e2e-id='conference-tab__setting']",
        "button[e2e-id='conference-tab__setting']",
        "xpath=//button[@e2e-id='conference-tab__settings' or @e2e-id='conference-tab__setting']",
    ]
    CONFERENCE_SESSION_SETTINGS_GUEST_LINK_COPY = "[e2e-id='conference-session--settings--guest-link--copy-btn']"
    CONFERENCE_SESSION_LINK_LIST = [
        "a.layout.layout-top-margin_8.pseudo-link",
        'a.pseudo-link:has-text("расширенные настройки ссылок")',
    ]
    CONFERENCE_SESSION_SPEAKER_LINK_COPY = "[e2e-id='share-link-copy-speaker-link-btn']"
    SPEAKER_LINK_INPUT_LOCATORS = [
        "input[e2e-id*='speaker']",
        "input[value*='#join:']",
        "input[value*='join:']",
        "input[readonly]",
    ]
    SPEAKER_LINK_ANCHOR_LOCATORS = [
        "a[href*='#join:']",
        "a[href*='join:']",
    ]
    CONFERENCE_SESSION_MODERATOR_LINK_COPY = "[e2e-id='share-link-copy-moderator-link-btn']"
    MODERATOR_LINK_INPUT_LOCATORS = [
        "input[e2e-id*='moderator']",
        "input[value*='#join:']",
        "input[value*='join:']",
        "input[readonly]",
    ]
    MODERATOR_LINK_ANCHOR_LOCATORS = [
        "a[href*='#join:']",
        "a[href*='join:']",
    ]
    GUEST_LINK_INPUT_LOCATORS = [
        "input[e2e-id*='guest-link']",
        "input[value*='#join:']",
        "input[value*='join:']",
        "input[readonly]",
    ]
    GUEST_LINK_ANCHOR_LOCATORS = [
        "a[href*='#join:']",
        "a[href*='join:']",
    ]

    PARTICIPANTS_LIST_LOCATOR = "[e2e-id='toggle-participants-list-btn']"
    PARTICIPANTS_PLUS_BOTTOM_LOCATOR = "[e2e-id='participants-list-additional-actions-btn']"
    ADD_PARTICIPANTS_LOCATORS = [
        "div.option__main-content:has-text('Добавить участников')",
        "div.option:has(span.action-title:has-text('Добавить участников'))",
        "span.action-title:has-text('Добавить участников')",
    ]
    INVITE_EMAIL_INPUT_LOCATORS = [
        "input.search-input.iva-input",
        "input[type='email']",
        "input[placeholder*='email' i]",
        "input[placeholder*='почт' i]",
    ]

    RESULT_ROW_LOCATORS = [
        "shared-invite-interlocutors-list shared-interlocutors-item",
        "shared-interlocutors-item",
    ]

    PARTICIPANT_ROW_CHECKBOX_LOCATORS = [
        "iva-checkbox div.iva-checkbox_frame",
        "div.iva-checkbox_frame",
        "iva-checkbox input[type='checkbox']",
        "input[type='checkbox']",
    ]
    SEND_INVITE_BUTTON_LOCATORS = [
        "button:has-text('Добавить')",
        "button:has(span:has-text('Добавить'))",
    ]
    SIMPLE_EVENT_TEMPLATE_CARD = (
        "xpath=//div[contains(@class, 'conference-card')]"
        "[.//h4[contains(@class, 'conference-name') and normalize-space()='Мероприятие']]"
    )

    JOIN_SETTINGS_SECTION = [
        "[e2e-id='join-settings']",
        "shared-settings-section[e2e-id='join-settings']",
    ]

    REGISTRATION_FORM_CHECKBOX = [
        "input[name='registrationForm']",
        "input[id*='_input'][name='registrationForm']",
    ]

    DRAFT_PLAN_CONFERENCE_BUTTON = "[e2e-id='draft-plan-conference-btn']"

    REGISTRATION_LINK_COPY_BUTTON = "[e2e-id='registration-link-copy-button']"

    EVENT_START_MODAL_LOCATORS = [
        "app-conference-calling-modal",
        "iva-dynamic app-conference-calling-modal",
    ]

    EVENT_START_MODAL_CLOSE_LOCATORS = [
        "app-conference-calling-modal header button.iva-icon-button",
        "app-conference-calling-modal button.iva-icon-button",
        "app-conference-calling-modal svg-icon[src*='close.svg']",
        "app-conference-calling-modal button:has(svg-icon[src*='close.svg'])",
    ]

    def open(self):
        self.page.goto(f"{config.BASE_URL}/v2/iva/home/conferences", wait_until="domcontentloaded")
        self.page.locator(self.ADD_BUTTON).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )

    def click_add(self):
        self.safe_click(self.ADD_BUTTON)

    def select_groups_template(self):
        self.page.locator(self.TEMPLATE_GROUPS_CARD).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.TEMPLATE_GROUPS_CARD)

    def open_settings_and_close(self):
        self.page.locator(self.SETTINGS_MODAL_BUTTON).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.SETTINGS_MODAL_BUTTON)

        self.page.locator(self.CLOSE_MODAL_BUTTON).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CLOSE_MODAL_BUTTON)

    def back_to_list(self):
        try:
            self.page.locator(self.HAMBURGER_BUTTON).first.click(timeout=5000)
        except Exception:
            self.page.locator(self.HAMBURGER_BUTTON).first.click(force=True)

        self.page.goto(f"{config.BASE_URL}/v2/iva/home/conferences", wait_until="domcontentloaded")
        self._disable_overlay_pointer_events()

        self.page.locator(self.EVENT_LIST_SCROLLER).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        return self

    def _disable_overlay_pointer_events(self):
        self.page.evaluate(
            """
            () => {
              const selectors = [
                '.conference-session.conference-session-wide-mode',
                '[ivamover="conference-session-pip"]',
                '.conference-session video'
              ];
              selectors.forEach((selector) => {
                document.querySelectorAll(selector).forEach((el) => {
                  el.style.pointerEvents = 'none';
                  el.style.zIndex = '0';
                });
              });
            }
            """
        )

    def _reveal_conference_controls(self):
        viewport = self.page.viewport_size or {"width": 1920, "height": 1080}
        top_y = max(int(viewport["height"] * 0.07), 1)

        points = [
            (int(viewport["width"] * 0.50), top_y),
            (int(viewport["width"] * 0.75), top_y),
            (int(viewport["width"] * 0.90), top_y),
            (int(viewport["width"] * 0.96), top_y + 8),
        ]
        for x, y in points:
            self.page.mouse.move(max(x, 1), max(y, 1), steps=10)
            self.page.wait_for_timeout(120)

    def open_event_settings(self):
        for _ in range(4):
            self._reveal_conference_controls()
            try:
                settings_button = self._find_first_visible(self.CONFERENCES_TAB_SETTINGS_LOCATORS, timeout=2500)
                self.safe_click(settings_button)
                return
            except Exception:
                continue

        raise AssertionError(
            "Не удалось открыть вкладку настроек мероприятия: кнопка settings не появилась после reveal controls"
        )

    def open_link_list(self):
        link_list = self._find_first_visible(self.CONFERENCE_SESSION_LINK_LIST, timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(link_list)

    def click_copy_speaker_link(self):
        self.page.locator(self.CONFERENCE_SESSION_SPEAKER_LINK_COPY).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CONFERENCE_SESSION_SPEAKER_LINK_COPY)

    def click_copy_moderator_link(self):
        self.page.locator(self.CONFERENCE_SESSION_MODERATOR_LINK_COPY).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CONFERENCE_SESSION_MODERATOR_LINK_COPY)

    def click_copy_guest_link(self):
        self.page.locator(self.CONFERENCE_SESSION_SETTINGS_GUEST_LINK_COPY).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CONFERENCE_SESSION_SETTINGS_GUEST_LINK_COPY)

    def get_speaker_link_url(self) -> str:
        for selector in self.SPEAKER_LINK_INPUT_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            value = (locator.input_value() or "").strip()
            if "join:" in value:
                return value

        for selector in self.SPEAKER_LINK_ANCHOR_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            href = (locator.get_attribute("href") or "").strip()
            if "join:" in href:
                return href

        full_text = self.page.content() or ""
        import re
        match = re.search(r'https?://[^\s"\'<>]+#?join:[^\s"\'<>]+', full_text)
        if match:
            return match.group(0)

        raise AssertionError("Не удалось получить speaker-link из настроек мероприятия")

    def get_moderator_link_url(self) -> str:
        for selector in self.MODERATOR_LINK_INPUT_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            value = (locator.input_value() or "").strip()
            if "join:" in value:
                return value

        for selector in self.MODERATOR_LINK_ANCHOR_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            href = (locator.get_attribute("href") or "").strip()
            if "join:" in href:
                return href

        full_text = self.page.content() or ""
        import re
        match = re.search(r'https?://[^\s"\'<>]+#?join:[^\s"\'<>]+', full_text)
        if match:
            return match.group(0)

        raise AssertionError("Не удалось получить moderator-link из настроек мероприятия")

    def get_guest_link_url(self) -> str:
        for selector in self.GUEST_LINK_INPUT_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            value = (locator.input_value() or "").strip()
            if "join:" in value:
                return value

        for selector in self.GUEST_LINK_ANCHOR_LOCATORS:
            locator = self.page.locator(selector).first
            if locator.count() == 0:
                continue
            href = (locator.get_attribute("href") or "").strip()
            if "join:" in href:
                return href

        raise AssertionError("Не удалось получить guest-link из настроек мероприятия")

    def open_participants_list(self):
        self.page.locator(self.PARTICIPANTS_LIST_LOCATOR).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.PARTICIPANTS_LIST_LOCATOR)

    def plus_bottom_participants_list(self):
        self.page.locator(self.PARTICIPANTS_PLUS_BOTTOM_LOCATOR).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.PARTICIPANTS_PLUS_BOTTOM_LOCATOR)

    def add_participants_bottom(self):
        selectors = (
            [self.ADD_PARTICIPANTS_LOCATORS]
            if isinstance(self.ADD_PARTICIPANTS_LOCATORS, str)
            else self.ADD_PARTICIPANTS_LOCATORS
        )
        add_participants_button = self._find_first_visible(
            selectors, timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(add_participants_button)

    def _wait_invite_loader_disappear(self, timeout_ms: int = 7000):
        loader = self.page.locator("shared-invite-interlocutors-list div.loader").first
        try:
            if loader.count() > 0:
                loader.wait_for(state="hidden", timeout=timeout_ms)
        except Exception:
            pass

    def _escape_xpath_text(self, value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join([f"'{part}'" for part in parts]) + ")"

    def fill_invited_participant_email(self, email: str):
        input_locator = self._find_first_visible(
            self.INVITE_EMAIL_INPUT_LOCATORS,
            timeout=config.EXPLICIT_WAIT * 1000
        )

        input_locator.click()
        input_locator.fill("")
        input_locator.fill(email)

        self.page.wait_for_timeout(400)

        try:
            input_locator.press("Enter")
        except Exception:
            pass

        self._wait_invite_loader_disappear(timeout_ms=7000)
        self.page.wait_for_timeout(500)

    def _find_participant_row(self, value: str, timeout_ms: int = 10000):
        escaped_value = self._escape_xpath_text(value)

        xpath_variants = [
            f"xpath=//shared-interlocutors-item[contains(., {escaped_value})]",
            f"xpath=//shared-invite-interlocutors-list//shared-interlocutors-item[contains(., {escaped_value})]",
        ]

        for _ in range(max(1, timeout_ms // 250)):
            self._wait_invite_loader_disappear(timeout_ms=1500)

            for xpath in xpath_variants:
                row = self.page.locator(xpath).first
                try:
                    if row.count() > 0 and row.is_visible():
                        return row
                except Exception:
                    continue

            self.page.wait_for_timeout(250)

        for selector in self.RESULT_ROW_LOCATORS:
            rows = self.page.locator(selector)
            count = rows.count()
            for idx in range(min(count, 20)):
                row = rows.nth(idx)
                try:
                    if row.is_visible():
                        return row
                except Exception:
                    continue

        raise AssertionError(f"Не удалось найти строку участника: {value}")

    def _participant_row_is_selected(self, participant_row) -> bool:
        checkbox_input = participant_row.locator("iva-checkbox input[type='checkbox']").first
        try:
            if checkbox_input.count() > 0:
                try:
                    if checkbox_input.is_checked():
                        return True
                except Exception:
                    pass

                checked_attr = checkbox_input.get_attribute("checked")
                if checked_attr is not None:
                    return True
        except Exception:
            pass

        try:
            aria_checked = (participant_row.locator("iva-checkbox").first.get_attribute("aria-checked") or "").lower()
            if aria_checked == "true":
                return True
        except Exception:
            pass

        try:
            classes = (participant_row.get_attribute("class") or "").lower()
            if "selected" in classes or "checked" in classes or "active" in classes:
                return True
        except Exception:
            pass

        return False

    def _wait_add_button_enabled(self, timeout_ms: int = 7000) -> bool:
        for _ in range(max(1, timeout_ms // 250)):
            self._wait_invite_loader_disappear(timeout_ms=1000)

            for selector in self.SEND_INVITE_BUTTON_LOCATORS:
                buttons = self.page.locator(selector)
                count = buttons.count()
                for idx in range(count):
                    button = buttons.nth(idx)
                    try:
                        if button.is_visible() and button.is_enabled():
                            return True
                    except Exception:
                        continue

            self.page.wait_for_timeout(250)

        return False

    def select_invited_participant_checkbox(self, value: str):
        participant_row = self._find_participant_row(value, timeout_ms=config.EXPLICIT_WAIT * 1000)
        participant_row.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

        checkbox_frame = participant_row.locator("iva-checkbox div.iva-checkbox_frame").first
        checkbox_input = participant_row.locator("iva-checkbox input[type='checkbox']").first

        last_error = None

        for _ in range(5):
            try:
                self._wait_invite_loader_disappear(timeout_ms=2000)

                if checkbox_frame.count() > 0 and checkbox_frame.is_visible():
                    self.safe_click(checkbox_frame)
                elif checkbox_input.count() > 0:
                    try:
                        checkbox_input.check(force=True)
                    except Exception:
                        handle = checkbox_input.element_handle()
                        if handle is not None:
                            self.page.evaluate(
                                """
                                (el) => {
                                    el.checked = true;
                                    el.dispatchEvent(new Event('input', { bubbles: true }));
                                    el.dispatchEvent(new Event('change', { bubbles: true }));
                                }
                                """,
                                handle,
                            )
                else:
                    self.safe_click(participant_row)

                self.page.wait_for_timeout(300)
                self._wait_invite_loader_disappear(timeout_ms=2000)

                if self._participant_row_is_selected(participant_row):
                    if self._wait_add_button_enabled(timeout_ms=3000):
                        return

                try:
                    label = participant_row.locator("iva-checkbox label").first
                    if label.count() > 0 and label.is_visible():
                        self.safe_click(label)
                        self.page.wait_for_timeout(300)
                        self._wait_invite_loader_disappear(timeout_ms=2000)
                        if self._wait_add_button_enabled(timeout_ms=3000):
                            return
                except Exception:
                    pass

                try:
                    self.safe_click(participant_row)
                    self.page.wait_for_timeout(300)
                    self._wait_invite_loader_disappear(timeout_ms=2000)
                    if self._wait_add_button_enabled(timeout_ms=3000):
                        return
                except Exception:
                    pass

            except Exception as e:
                last_error = e

        debug_text = ""
        try:
            debug_text = participant_row.inner_text()
        except Exception:
            pass

        raise AssertionError(
            f"Не удалось выбрать участника: {value}. "
            f"Текст строки: {debug_text}. "
            f"Последняя ошибка: {last_error}"
        )

    def _is_button_actionable(self, button):
        try:
            if not button.is_visible():
                return False
        except Exception:
            return False

        try:
            return button.is_enabled()
        except Exception:
            return False

    def submit_invite_participant(self):
        if not self._wait_add_button_enabled(timeout_ms=8000):
            debug_lines = []

            for selector in self.SEND_INVITE_BUTTON_LOCATORS:
                buttons = self.page.locator(selector)
                count = buttons.count()
                debug_lines.append(f"selector={selector}, count={count}")

                for idx in range(count):
                    button = buttons.nth(idx)
                    try:
                        debug_lines.append(
                            f"idx={idx}, visible={button.is_visible()}, enabled={button.is_enabled()}, "
                            f"disabled={button.get_attribute('disabled')}, "
                            f"aria-disabled={button.get_attribute('aria-disabled')}, "
                            f"text={(button.inner_text() or '').strip()}"
                        )
                    except Exception as e:
                        debug_lines.append(f"idx={idx}, read_error={e}")

            try:
                self.page.screenshot(path="invite_participant_debug.png", full_page=True)
            except Exception:
                pass

            raise AssertionError(
                "Кнопка добавления участника осталась неактивной после выбора участника.\n"
                + "\n".join(debug_lines)
            )

        for selector in self.SEND_INVITE_BUTTON_LOCATORS:
            buttons = self.page.locator(selector)
            count = buttons.count()

            for idx in range(count):
                button = buttons.nth(idx)
                try:
                    if button.is_visible() and button.is_enabled():
                        self.safe_click(button)
                        return
                except Exception:
                    continue

        raise AssertionError("Не удалось нажать кнопку 'Добавить', хотя она стала активной")

    def select_simple_event_template(self):
        self.page.locator(self.SIMPLE_EVENT_TEMPLATE_CARD).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.SIMPLE_EVENT_TEMPLATE_CARD)

    def open_join_settings(self):
        section = self._find_first_visible(self.JOIN_SETTINGS_SECTION, timeout=config.EXPLICIT_WAIT * 1000)
        self.safe_click(section)

    def enable_registration_form(self):
        self.open_join_settings()

        checkbox = self.page.locator("input[name='registrationForm']").first
        checkbox.wait_for(state="attached", timeout=config.EXPLICIT_WAIT * 1000)

        try:
            if checkbox.is_checked():
                return
        except Exception:
            pass

        # Сначала пробуем кликнуть по видимой кастомной обертке рядом с checkbox
        click_candidates = [
            "xpath=//input[@name='registrationForm']/following-sibling::*[1]",
            "xpath=//input[@name='registrationForm']/parent::*",
            "xpath=//input[@name='registrationForm']/ancestor::*[self::label or self::div][1]",
        ]

        for selector in click_candidates:
            try:
                candidate = self.page.locator(selector).first
                if candidate.count() > 0 and candidate.is_visible():
                    candidate.click(force=True)
                    self.page.wait_for_timeout(300)

                    try:
                        if checkbox.is_checked():
                            return
                    except Exception:
                        pass
            except Exception:
                continue

        # Если визуальный клик не помог — включаем напрямую через JS
        handle = checkbox.element_handle()
        if handle is None:
            raise AssertionError("Не удалось получить element_handle для registrationForm checkbox")

        self.page.evaluate(
            """
            (el) => {
                el.checked = true;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
            }
            """,
            handle,
        )

        self.page.wait_for_timeout(500)

        assert checkbox.is_checked(), "Чекбокс registrationForm не включился"

    def click_plan_draft(self):
        self.page.locator(self.DRAFT_PLAN_CONFERENCE_BUTTON).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.DRAFT_PLAN_CONFERENCE_BUTTON)

    def click_copy_registration_link(self):
        button = self.page.locator("[e2e-id='registration-link-copy-button']").first

        try:
            button.wait_for(state="visible", timeout=3000)
            button.click(force=True)
            self.page.wait_for_timeout(500)
            return
        except Exception:
            pass

        self.close_event_start_popup_if_present()

        button.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        button.click(force=True)
        self.page.wait_for_timeout(700)

    def close_event_start_popup_if_present(self) -> bool:
        for modal_selector in self.EVENT_START_MODAL_LOCATORS:
            try:
                modal = self.page.locator(modal_selector).first
                if modal.count() > 0 and modal.is_visible():
                    for close_selector in self.EVENT_START_MODAL_CLOSE_LOCATORS:
                        try:
                            close_btn = self.page.locator(close_selector).first
                            if close_btn.count() > 0 and close_btn.is_visible():
                                close_btn.click(force=True)
                                self.page.wait_for_timeout(700)
                                return True
                        except Exception:
                            continue
            except Exception:
                continue
        return False