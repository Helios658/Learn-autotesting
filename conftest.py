import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright
from pathlib import Path
from datetime import datetime
from utils.artifacts import save_artifacts
from config import config
import socket
from playwright.sync_api import Error as PlaywrightError
from pages.mail_page import MailPage, InvitationLinkNotFoundError
load_dotenv()


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", help="Run tests in headless mode")

def _resolve_browser_launcher(playwright_instance: Playwright):
    browser_name = (config.BROWSER or "chromium").strip().lower()
    aliases = {
        "chrome": "chromium",
        "chromium": "chromium",
        "firefox": "firefox",
        "webkit": "webkit",
        "safari": "webkit",
    }

    resolved = aliases.get(browser_name)
    if not resolved:
        print(f"⚠️ Неизвестный BROWSER='{config.BROWSER}', используем chromium")
        resolved = "chromium"

    return resolved, getattr(playwright_instance, resolved)

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
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

@pytest.fixture(autouse=True)
def validate_test_base_url(request):
    if "driver" not in request.fixturenames and "login_page" not in request.fixturenames:
        return
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

    resolved_browser, browser_launcher = _resolve_browser_launcher(playwright_instance)

    launch_kwargs = {"headless": use_headless}
    if resolved_browser == "chromium":
        launch_kwargs["args"] = ["--ignore-certificate-errors", "--allow-insecure-localhost"]

    browser = browser_launcher.launch(**launch_kwargs)
    context_kwargs = {
        "viewport": {"width": 1600, "height": 900},
        "ignore_https_errors": True,
        "record_video_dir": "artifacts/videos",
    }

    if config.TEST_2FA_USER_EMAIL:
        context_kwargs["http_credentials"] = {
            "username": config.TEST_2FA_USER_EMAIL,
            "password": config.TEST_2FA_USER_PASSWORD,
        }

    context = browser.new_context(**context_kwargs)

    # ✅ START tracing всегда, сохраняем только при падении
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = context.new_page()

    if use_headless:
        print(f"🚀 Запуск Playwright ({resolved_browser}) в headless-режиме")
    else:
        print(f"🚀 Запуск Playwright ({resolved_browser}) в обычном режиме")

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
        except PlaywrightError as exc:
            print(f"⚠️ Не удалось сохранить trace: {exc}")

        # ✅ опционально: attach trace в Allure, если установлен
        try:
            import allure  # type: ignore

            if trace_path.exists():
                allure.attach.file(
                    str(trace_path),
                    name="trace.zip",
                    attachment_type=allure.attachment_type.ZIP,
                )
        except (ImportError, AttributeError, OSError) as exc:
            print(f"⚠️ Не удалось сохранить trace: {exc}")
    else:
        # success: остановить без сохранения
        try:
            context.tracing.stop()
        except PlaywrightError as exc:
            print(f"⚠️ Не удалось сохранить trace: {exc}")
        mail_logout_urls = [
            f"{config.MAIL_URL.rstrip('/')}/owa/logoff.owa",
            f"{config.MAIL_URL.rstrip('/')}/owa/auth/logoff.aspx",
        ]
        for logout_url in mail_logout_urls:
            try:
                page.goto(logout_url, wait_until="domcontentloaded", timeout=8000)
                page.wait_for_timeout(400)
            except PlaywrightError:
                continue

        try:
            context.clear_cookies()
        except PlaywrightError:
            pass

        context.close()
        browser.close()

@pytest.fixture
def mail_page_session(driver):
    """
    Fallback-фикстура на случай, если session-scoped mail fixture отсутствует в conftest.py.
    Используем текущий driver-контекст и логинимся в почту в рамках теста.
    """
    mail_page = MailPage(driver)
    mail_page.login()
    return mail_page

@pytest.fixture(scope="session")
def mail_page_session(playwright_instance: Playwright):
    """
    Отдельная session-scoped страница почты:
    - логинимся 1 раз на всю сессию тестов,
    - избегаем частых новых OWA-сессий и блокировок по лимиту.
    """
    from pages.mail_page import MailPage

    resolved_browser, browser_launcher = _resolve_browser_launcher(playwright_instance)
    launch_kwargs = {"headless": config.HEADLESS_MODE}
    if resolved_browser == "chromium":
        launch_kwargs["args"] = ["--ignore-certificate-errors", "--allow-insecure-localhost"]

    browser = browser_launcher.launch(**launch_kwargs)
    context = browser.new_context(ignore_https_errors=True, viewport={"width": 1600, "height": 900})
    page = context.new_page()

    mail_page = MailPage(page)
    mail_page.login()

    yield mail_page

    mail_logout_urls = [
        f"{config.MAIL_URL.rstrip('/')}/owa/logoff.owa",
        f"{config.MAIL_URL.rstrip('/')}/owa/auth/logoff.aspx",
    ]
    for logout_url in mail_logout_urls:
        try:
            page.goto(logout_url, wait_until="domcontentloaded", timeout=8000)
            page.wait_for_timeout(400)
        except PlaywrightError:
            continue

    try:
        context.clear_cookies()
    except PlaywrightError:
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

@pytest.fixture
def two_users(request, playwright_instance: Playwright):
    use_headless = request.config.getoption("--headless") or config.HEADLESS_MODE
    resolved_browser, browser_launcher = _resolve_browser_launcher(playwright_instance)

    launch_kwargs = {"headless": use_headless}
    if resolved_browser == "chromium":
        launch_kwargs["args"] = ["--ignore-certificate-errors", "--allow-insecure-localhost"]

    browser = browser_launcher.launch(**launch_kwargs)

    context_a = browser.new_context(
        viewport={"width": 1600, "height": 900},
        ignore_https_errors=True,
        record_video_dir="artifacts/videos",
    )

    context_a1 = browser.new_context(
        viewport={"width": 1600, "height": 900},
        ignore_https_errors=True,
        record_video_dir="artifacts/videos",
    )

    page_a = context_a.new_page()
    page_a1 = context_a1.new_page()

    yield {
        "a": page_a,
        "a1": page_a1,
        "context_a": context_a,
        "context_a1": context_a1,
        "browser": browser,
    }

    context_a.close()
    context_a1.close()
    browser.close()