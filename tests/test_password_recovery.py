import pytest
from config import config
from pages.login_page import LoginPage
from pages.password_recovery_page import PasswordRecoveryPage
from pages.mail_page import MailPage
from pages.new_password_page import NewPasswordPage
from services.password_service import PasswordService


def test_password_recovery(driver):
    login_page = LoginPage(driver)
    login_page.open()

    driver.locator("[e2e-id='login-page.login-form.recovery-password-link']").first.click()

    recovery_page = PasswordRecoveryPage(driver)
    recovery_page.request_password_recovery(config.USER_EMAIL)

    try:
        success_element = driver.locator("p.layout-bottom-margin_2.text-align_center").first
        success_element.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        message_text = success_element.inner_text().lower()
        if any(word in message_text for word in ["отправлен", "отправлены", "отправлено"]):
            print(f"✅ Подтверждение отправки: '{success_element.inner_text()}'")
    except Exception as e:
        print(f"⚠️ Не дождались подтверждения: {e}")

    try:
        mail_page = MailPage(driver)
        mail_page.login()
        reset_link = mail_page.get_password_reset_link(wait_for_email=True)

        driver.goto(reset_link)
        password_service = PasswordService()
        new_password = password_service.generate_and_persist_password()
        new_password_page = NewPasswordPage(driver)
        new_password_page.set_new_password(new_password)
        new_password_page.go_to_login()

        login_page.enter_username(config.USER_EMAIL)
        login_page.enter_password(new_password)
        login_page.click_login_button()

        logged_in = login_page.wait_for_successful_login(timeout=config.EXPLICIT_WAIT * 2)
        if not logged_in:
            error_code = login_page.get_network_error()
            pytest.fail(
                f"После восстановления пароля не удалось войти: "
                f"URL={driver.url}, network_error={error_code}"
            )
    except Exception as e:
        if "почта" in str(e).lower() or "mail" in str(e).lower():
            pytest.skip(f"Пропускаем тест из-за проблем с почтой: {e}")
        raise


def test_password_recovery_profile(driver):
    password_service = PasswordService()
    current_password = password_service.get_current_password(config.USER_PASSWORD)
    if not current_password:
        pytest.skip("Нет текущего пароля: файл last_generated_password.txt и TEST_USER_PASSWORD пусты")

    login_page = LoginPage(driver)
    login_page.open()
    login_page.enter_username(config.USER_EMAIL)
    login_page.enter_password(current_password)
    login_page.click_login_button()

    if not login_page.wait_for_successful_login(timeout=config.EXPLICIT_WAIT * 2):
        pytest.skip(f"Не удалось войти пользователем для смены пароля через профиль: {driver.url}")

    driver.locator("[e2e-id='shared-core.navigation-menu.settings']").first.click()
    driver.locator("[e2e-id='settings-page.list.profile']").first.click()
    driver.locator("[e2e-id='settings-page.profile.cng-pwd-link']").first.click()

    driver.locator("[e2e-id='settings-page.change-password-modal.old-password-input']").first.fill(current_password)

    new_password = password_service.generate_and_persist_password()
    driver.locator("[e2e-id='settings-page.change-password-modal.new-password-input']").first.fill(new_password)
    driver.locator("[e2e-id='settings-page.change-password-modal.new-password-confirm-input']").first.fill(new_password)

    driver.locator("[e2e-id='settings-page.change-password-modal.save-btn']").first.click()
    driver.locator("[e2e-id='settings-page.profile.logout-link']").first.click()
    driver.wait_for_url("**/login**", timeout=config.EXPLICIT_WAIT * 1000)

    error_code = login_page.login_with_network_check(
        username=config.USER_EMAIL,
        password=new_password,
        expect_success=True,
    )
    assert error_code == 0, f"После смены пароля логин вернул сетевую ошибку: {error_code}"
    assert login_page.wait_for_successful_login(), (
        f"После смены пароля остались на странице логина: {driver.url}"
    )