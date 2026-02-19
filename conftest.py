import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright

load_dotenv()

from config import config


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as p:
        yield p


@pytest.fixture
def driver(request, playwright_instance: Playwright):
    use_headless = request.config.getoption("--headless") or config.HEADLESS_MODE
    browser = playwright_instance.chromium.launch(
        headless=use_headless,
        args=["--ignore-certificate-errors", "--allow-insecure-localhost"],
    )
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
    )
    page = context.new_page()

    if use_headless:
        print("🚀 Запуск Playwright в headless-режиме")
    else:
        print("🚀 Запуск Playwright в обычном режиме")

    yield page

    context.close()
    browser.close()


@pytest.fixture
def admin_user():
    return {
        "email": config.ADMIN_EMAIL,
        "password": config.ADMIN_PASSWORD,
    }


@pytest.fixture
def test_user():
    return {
        "email": config.USER_EMAIL,
        "password": config.USER_PASSWORD,
    }


@pytest.fixture
def login_page(driver):
    from pages.login_page import LoginPage

    return LoginPage(driver)