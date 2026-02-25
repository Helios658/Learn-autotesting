from config import config
from pages.base_page import BasePage


class EventPage(BasePage):
    CONFERENCES_TAB = "[e2e-id='shared-core.navigation-menu.conferences']"
    ADD_BUTTON = "[e2e-id='ADD']"

    # Шаблон: "Деление участников на группы" (как в твоём тесте)
    TEMPLATE_GROUPS_CARD = (
        "xpath=//div[contains(@class, 'conference-card')]"
        "[.//h4[contains(@class, 'conference-name') and normalize-space()='Деление участников на группы']]"
    )

    SETTINGS_MODAL_BUTTON = "xpath=//span[text()=' Войти ']/parent::button"
    CLOSE_MODAL_BUTTON = "button.close-button.iva-icon-button"

    def open(self):
        # Важно: абсолютный URL
        self.page.goto(f"{config.BASE_URL}/v2/iva/home/conferences", wait_until="domcontentloaded")
        # Дожидаемся, что кнопка ADD вообще появилась
        self.page.locator(self.ADD_BUTTON).first.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)

    def click_add(self):
        # Используем твой safe_click из BasePage (он есть)
        self.safe_click(self.ADD_BUTTON)

    def select_groups_template(self):
        self.page.locator(self.TEMPLATE_GROUPS_CARD).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.TEMPLATE_GROUPS_CARD)

    def open_settings_and_close(self):
        # Это из твоего теста — оставляем, чтобы поведение совпало
        self.page.locator(self.SETTINGS_MODAL_BUTTON).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.SETTINGS_MODAL_BUTTON)
        self.page.locator(self.CLOSE_MODAL_BUTTON).first.wait_for(
            state="visible", timeout=config.EXPLICIT_WAIT * 1000
        )
        self.safe_click(self.CLOSE_MODAL_BUTTON)