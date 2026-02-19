#test_logout.py
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import config

def test_logout_menu(login_page, driver):
    wait = WebDriverWait(driver, config.EXPLICIT_WAIT)
    # Передаем логин и пароль
    error_code = login_page.login_with_network_check(
        username=config.ADMIN_EMAIL,
        password=config.ADMIN_PASSWORD,
        expect_success=True
    )
    assert error_code == 0
    print("✅ Залогинились")

    avatar = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".participant"))
    )
    avatar.click()

    exit_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='profile-action__logout']"))
    )
    exit_button.click()

    wait.until(
        EC.url_contains("login")
    )
    print("✅ Успешный выход с выпадающего меню")

def test_logout_profile(login_page, driver):
    wait = WebDriverWait(driver, config.EXPLICIT_WAIT)
    # Передаем логин и пароль
    error_code = login_page.login_with_network_check(
        username=config.ADMIN_EMAIL,
        password=config.ADMIN_PASSWORD,
        expect_success=True
    )
    assert error_code == 0
    print("✅ Залогинились")

    settings_bottom = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='shared-core.navigation-menu.settings']"))
    )
    settings_bottom.click()
    profile_bottom = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='settings-page.list.profile']"))
    )
    profile_bottom.click()
    logout_bottom = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='settings-page.profile.logout-link']"))
    )
    logout_bottom.click()

    wait.until(
        EC.url_contains("login")
    )
    print("✅ Успешный выход из профиля")
