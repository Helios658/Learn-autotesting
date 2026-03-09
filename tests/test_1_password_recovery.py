import pytest
from config import config
from pages.login_page import LoginPage
from services.password_service import PasswordService
from services.password_recovery_flow import PasswordRecoveryFlow

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("16")
def test_16_password_recovery(driver):
    flow = PasswordRecoveryFlow(driver)
    assert flow.run(), "Не удалось восстановить пароль и войти с новым"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("17")
def test_17_password_recovery_profile(driver):
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