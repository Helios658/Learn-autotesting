# conftest.py - ДОБАВЬ ИМПОРТ В НАЧАЛО
import pytest
from selenium import webdriver
from pages.login_page import LoginPage


def pytest_addoption(parser):
    """Добавляем опцию --headless"""
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")


@pytest.fixture
def driver(request):
    """Фикстура драйвера с выбором режима"""
    options = webdriver.ChromeOptions()

    # В CI всегда headless, иначе по флагу
    use_headless = IS_CI or request.config.getoption("--headless")

    if use_headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        print("🚀 Запуск в CI/headless режиме")
    else:
        options.add_argument("--start-maximized")
        print("🚀 Запуск в обычном режиме")

    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    if not use_headless:
        driver.maximize_window()

    yield driver
    driver.quit()


@pytest.fixture
def login_page(driver):
    return LoginPage(driver)