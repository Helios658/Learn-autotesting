# conftest.py
import pytest
from selenium import webdriver
from dotenv import load_dotenv  # ← ДОБАВЬТЕ ЭТОТ ИМПОРТ
import os

# 🔧 ЗАГРУЖАЕМ .env ПЕРЕД ИСПОЛЬЗОВАНИЕМ config
load_dotenv()

# ТОЛЬКО ПОСЛЕ load_dotenv() импортируем config
from config import config  # ← ИМПОРТ ПОСЛЕ load_dotenv()


def pytest_addoption(parser):
    """Добавляем опцию --headless"""
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")


@pytest.fixture
def driver(request):
    """Фикстура драйвера с выбором режима"""
    options = webdriver.ChromeOptions()

    # Используем настройку из конфига или командной строки
    use_headless = request.config.getoption("--headless") or config.HEADLESS_MODE

    if use_headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        print("🚀 Запуск в headless-режиме")
    else:
        options.add_argument("--start-maximized")
        print("🚀 Запуск в обычном режиме")

    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(config.IMPLICIT_WAIT)

    if not use_headless:
        driver.maximize_window()

    yield driver
    driver.quit()


@pytest.fixture
def admin_user():
    """Фикстура с данными администратора"""
    return {
        'email': config.ADMIN_EMAIL,
        'password': config.ADMIN_PASSWORD
    }


@pytest.fixture
def test_user():
    """Фикстура с данными тестового пользователя"""
    return {
        'email': config.USER_EMAIL,
        'password': config.USER_PASSWORD  # ← будет динамический пароль
    }


@pytest.fixture
def login_page(driver):
    from pages.login_page import LoginPage
    return LoginPage(driver)