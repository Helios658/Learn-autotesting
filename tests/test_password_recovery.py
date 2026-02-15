import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from pages.password_recovery_page import PasswordRecoveryPage
from pages.mail_page import MailPage
from pages.new_password_page import NewPasswordPage
from config import config
from services.password_service import PasswordService


#@pytest.mark.skip(reason="Требует работающей корпоративной почты")
def test_password_recovery(driver):
    """Полный тест восстановления пароля"""
    wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

    # 1. Запрос восстановления
    login_page = LoginPage(driver)
    login_page.open()

    recovery_link = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='login-page.login-form.recovery-password-link']"))
    )
    recovery_link.click()

    recovery_page = PasswordRecoveryPage(driver)
    recovery_page.request_password_recovery(config.USER_EMAIL)

    try:
        success_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.layout-bottom-margin_2.text-align_center"))
        )
        message_text = success_element.text.lower()
        if any(word in message_text for word in ["отправлен", "отправлены", "отправлено"]):
            print(f"✅ Подтверждение отправки: '{success_element.text}'")
        else:
            print(f"⚠️ Неожиданный текст: '{success_element.text}'")
    except Exception as e:
        print(f"⚠️ Не дождались подтверждения: {e}")

    # 2. Работа с почтой
    try:
        mail_page = MailPage(driver)
        mail_page.login()  # ← Без параметров, использует данные из конфига
        reset_link = mail_page.get_password_reset_link(wait_for_email=True)

        # 3. Смена пароля
        driver.get(reset_link)
        password_service = PasswordService()
        new_password = password_service.generate_and_persist_password()
        new_password_page = NewPasswordPage(driver)
        new_password_page.set_new_password(new_password)
        new_password_page.go_to_login()

        # 4. Логин с новым паролем
        login_page.enter_username(config.USER_EMAIL)
        current_password = new_password
        login_page.enter_password(current_password)
        login_page.click_login_button()

        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".participant"))
            )
            print("✅ Успешный вход с новым паролем подтвержден")
        except:
            print("⚠️ Не дождались явного признака успешного входа")

        assert "login" not in driver.current_url.lower()
        print(f"🎉 УСПЕХ! Вошли с новым паролем: {new_password}")

    except Exception as e:
        if "почта" in str(e).lower() or "mail" in str(e).lower():
            pytest.skip(f"Пропускаем тест из-за проблем с почтой: {e}")
        else:
            raise

def test_password_recovery_profile(driver):
    wait = WebDriverWait(driver, config.EXPLICIT_WAIT)
    password_service = PasswordService()
    current_password = password_service.get_current_password(config.USER_PASSWORD)
    if not current_password:
        pytest.skip("Нет текущего пароля: файл last_generated_password.txt и TEST_USER_PASSWORD пусты")

    login_page = LoginPage(driver)
    login_page.open()
    login_page.enter_username(config.USER_EMAIL)
    login_page.enter_password(current_password)
    login_page.click_login_button()

    assert login_page.wait_for_successful_login(timeout=config.EXPLICIT_WAIT * 2), (
        f"Не удалось дождаться входа перед переходом в настройки: {driver.current_url}"
    )

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='shared-core.navigation-menu.settings']"))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='settings-page.list.profile']"))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='settings-page.profile.cng-pwd-link']"))).click()

    old_pass_input = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,"[e2e-id='settings-page.change-password-modal.old-password-input']"))
    )
    old_pass_input.click()
    old_pass_input.clear()
    old_pass_input.send_keys(current_password)

    new_password = password_service.generate_and_persist_password()

    new_pass_input = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[e2e-id='settings-page.change-password-modal.new-password-input']"))
    )
    new_pass_input.clear()
    new_pass_input.send_keys(new_password)

    confirm_pass_input = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[e2e-id='settings-page.change-password-modal.new-password-confirm-input']"))
    )
    confirm_pass_input.clear()
    confirm_pass_input.send_keys(new_password)

    save_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='settings-page.change-password-modal.save-btn']"))
    )
    save_button.click()

    logout_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='settings-page.profile.logout-link']"))
    )
    logout_button.click()

    wait.until(EC.url_contains("login"))

    error_code = login_page.login_with_network_check(
        username=config.USER_EMAIL,
        password=new_password,
        expect_success=True,
    )
    assert error_code == 0, f"После смены пароля логин вернул сетевую ошибку: {error_code}"
    assert login_page.wait_for_successful_login(), (
        f"После смены пароля остались на странице логина: {driver.current_url}"
    )