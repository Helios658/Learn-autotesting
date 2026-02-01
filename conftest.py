import pytest
from selenium import webdriver


@pytest.fixture()
def driver():
    """
    Базовая фикстура для драйвера
    """
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture()
def login_page(driver):
    """
    Фикстура для страницы логина
    """
    from pages.login_page import LoginPage
    return LoginPage(driver)


@pytest.fixture()
def authorized_driver(driver, login_page):
    """
    Фикстура которая возвращает уже авторизованный driver
    Используется в тестах которые требуют авторизации
    """
    login_page.login()  # Авторизуемся
    return driver