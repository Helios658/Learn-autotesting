import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_logout_menu(login_page, driver):
    error_code = login_page.login_with_network_check(expect_success=True)
    assert error_code == 0
    print("✅ Залогинились")

    avatar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".participant"))
    )
    avatar.click()

    exit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='profile-action__logout']"))
    )
    exit_button.click()
    time.sleep(3)

    assert "login" in driver.current_url
    print("✅ Успешный выход с выпадающего меню")

def test_logout_profile(login_page, driver):
    error_code = login_page.login_with_network_check(expect_success=True)
    assert error_code == 0
    print("✅ Залогинились")

    settings_bottom = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR,"[e2e-id='shared-core.navigation-menu.settings']"))
    )
    settings_bottom.click()
    time.sleep(2)
    profile_bottom = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='settings-page.list.profile']"))
    )
    profile_bottom.click()
    time.sleep(2)
    logout_bottom = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR,"[e2e-id='settings-page.profile.logout-link']"))
    )
    logout_bottom.click()
    time.sleep(3)

    assert "login" in driver.current_url
    print("✅ Успешный выход из профиля")
