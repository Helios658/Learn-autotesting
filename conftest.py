import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright
from pathlib import Path
from datetime import datetime

from utils.artifacts import save_artifacts
from config import config
import socket

load_dotenv()


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    1) Сохраняем rep_* на item, чтобы фикстуры могли понять failed/success
    2) Если упал — сохраняем screenshot+html (у тебя уже было)
    """
    outcome = yield
    report = outcome.get_result()

    # ✅ важно для tracing: сохраняем репорт в item
    setattr(item, "rep_" + report.when, report)

    if report.when != "call":
        return

    if report.failed:
        page = item.funcargs.get("driver")
        if page is None:
            return

        test_name = item.nodeid.replace("::", "__")
        paths = save_artifacts(page, test_name=test_name, out_dir="artifacts")

        report.sections.append(("artifacts", f"{paths}"))

@pytest.fixture(scope="session", autouse=True)
def validate_test_base_url():
    """Проверяет, что TEST_BASE_URL резолвится до запуска e2e-тестов."""
    from urllib.parse import urlparse

    parsed = urlparse(config.BASE_URL)
    host = parsed.hostname

    if not host:
        pytest.skip("TEST_BASE_URL не задан или некорректен (не удалось извлечь host)")

    try:
        socket.gethostbyname(host)
    except socket.gaierror:
        pytest.skip(
            f"Хост TEST_BASE_URL не резолвится: {host}. "
            "Проверьте переменную окружения TEST_BASE_URL и DNS/VPN."
        )

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

    # ✅ START tracing всегда, сохраняем только при падении
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = context.new_page()

    if use_headless:
        print("🚀 Запуск Playwright в headless-режиме")
    else:
        print("🚀 Запуск Playwright в обычном режиме")

    yield page

    # ✅ определяем, упал ли тест
    rep_call = getattr(request.node, "rep_call", None)
    failed = bool(rep_call and rep_call.failed)

    if failed:
        out_dir = Path("artifacts")
        out_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_path = out_dir / f"{request.node.name}_{ts}_trace.zip"

        try:
            context.tracing.stop(path=str(trace_path))
        except Exception:
            pass

        # ✅ опционально: attach trace в Allure, если установлен
        try:
            import allure  # type: ignore

            if trace_path.exists():
                allure.attach.file(
                    str(trace_path),
                    name="trace.zip",
                    attachment_type=allure.attachment_type.ZIP,
                )
        except Exception:
            pass
    else:
        # success: остановить без сохранения
        try:
            context.tracing.stop()
        except Exception:
            pass

    context.close()
    browser.close()


@pytest.fixture
def admin_user():
    return {"email": config.ADMIN_EMAIL, "password": config.ADMIN_PASSWORD}


@pytest.fixture
def test_user():
    return {"email": config.USER_EMAIL, "password": config.USER_PASSWORD}


@pytest.fixture
def login_page(driver):
    from pages.login_page import LoginPage
    return LoginPage(driver)