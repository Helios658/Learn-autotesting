# Создайте файл: pages/main_page.py

from selenium.webdriver.common.by import By
from .base_page import BasePage


class MainPage(BasePage):
    """Page Object для главной страницы после логина"""

    CALL_BUTTON = (By.CSS_SELECTOR, "[e2e-id*='call'], [data-testid*='call']")
    PHONE_INPUT = (By.CSS_SELECTOR, "input[type='tel'], [placeholder*='номер']")
    START_CALL_BUTTON = (By.CSS_SELECTOR, "button[type='submit'], [class*='start-call']")

    def start_call(self, phone_number):
        """Начать звонок на номер"""
        # Нажать кнопку звонка
        self.wait_for_clickable(self.CALL_BUTTON).click()

        # Ввести номер
        phone_field = self.wait_for_clickable(self.PHONE_INPUT)
        phone_field.clear()
        phone_field.send_keys(phone_number)

        # Начать звонок
        self.wait_for_clickable(self.START_CALL_BUTTON).click()
        from .call_page import CallPage

        return CallPage(self.driver)
