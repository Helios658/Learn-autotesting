import time
import allure
import pytest
from config import config
from pages.login_page import LoginPage
from services.password_service import PasswordService
from services.password_recovery_flow import PasswordRecoveryFlow


def fill_change_password_form(driver, old_password=None, new_password=None, confirm_password=None):
    old_input = driver.locator("[e2e-id='settings-page.change-password-modal.old-password-input']").first
    new_input = driver.locator("[e2e-id='settings-page.change-password-modal.new-password-input']").first
    confirm_input = driver.locator("[e2e-id='settings-page.change-password-modal.new-password-confirm-input']").first

    old_input.fill("")
    new_input.fill("")
    confirm_input.fill("")

    if old_password is not None:
        old_input.fill(old_password)

    if new_password is not None:
        new_input.fill(new_password)

    if confirm_password is not None:
        confirm_input.fill(confirm_password)


def save_change_password(driver):
    driver.locator("[e2e-id='settings-page.change-password-modal.save-btn']").first.click()


def expect_any_error_text(driver, variants, timeout=5):
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            body_text = driver.locator("body").inner_text()
            normalized_body = " ".join(body_text.split()).lower()

            for text in variants:
                normalized_expected = " ".join(text.split()).lower()
                if normalized_expected in normalized_body:
                    return True
        except Exception:
            pass

        driver.wait_for_timeout(250)

    return False


def login_for_password_change(driver):
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

    return {
        "login_page": login_page,
        "current_password": current_password,
        "password_service": password_service,
    }


def open_change_password_modal_from_profile(driver):
    driver.locator("[e2e-id='shared-core.navigation-menu.settings']").first.click()
    driver.locator("[e2e-id='settings-page.list.profile']").first.click()
    driver.locator("[e2e-id='settings-page.profile.cng-pwd-link']").first.click()

    driver.locator("[e2e-id='settings-page.change-password-modal.old-password-input']").first.wait_for(
        state="visible",
        timeout=config.EXPLICIT_WAIT * 1000,
    )


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


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("29")
def test_29_change_password_invalid_input_cases(driver):
    ctx = login_for_password_change(driver)
    current_password = ctx["current_password"]

    open_change_password_modal_from_profile(driver)

    with allure.step("Не заполнять поля и нажать сохранить"):
        fill_change_password_form(
            driver,
            old_password=None,
            new_password=None,
            confirm_password=None,
        )
        save_change_password(driver)

        assert expect_any_error_text(driver, [
            "Необходимо ввести старый пароль",
            "Old password can't be empty",
        ]), "Не нашли ошибку для пустого старого пароля"

        assert expect_any_error_text(driver, [
            "Необходимо ввести новый пароль",
            "New password can't be empty",
        ]), "Не нашли ошибку для пустого нового пароля"

    with allure.step("Ввести верный старый пароль, новый пароль и неверное подтверждение"):
        fill_change_password_form(
            driver,
            old_password=current_password,
            new_password="NewPassword123",
            confirm_password="AnotherPassword123",
        )
        save_change_password(driver)

        assert expect_any_error_text(driver, [
            "Новый пароль и подтверждение пароля не совпадают",
            "New password and password confirmation do not match",
        ]), "Не нашли ошибку о несовпадении пароля и подтверждения"

    with allure.step("Ввести верный старый пароль и слишком короткий новый пароль"):
        fill_change_password_form(
            driver,
            old_password=current_password,
            new_password="123",
            confirm_password="123",
        )
        save_change_password(driver)

        assert expect_any_error_text(driver, [
            "Новый пароль должен быть не менее",
            "New password must be at least",
        ]), "Не нашли ошибку о минимальной длине нового пароля"

    with allure.step("Не вводить старый пароль, ввести новый пароль и подтверждение"):
        fill_change_password_form(
            driver,
            old_password=None,
            new_password="ValidPass123",
            confirm_password="ValidPass123",
        )
        save_change_password(driver)

        assert expect_any_error_text(driver, [
            "Необходимо ввести старый пароль",
            "Old password can't be empty",
        ]), "Не нашли ошибку для пустого старого пароля"

    with allure.step("Ввести неверный старый пароль"):
        fill_change_password_form(
            driver,
            old_password="WrongOldPassword123",
            new_password="ValidPass123",
            confirm_password="ValidPass123",
        )
        save_change_password(driver)

        assert expect_any_error_text(driver, [
            "Неверно указан старый пароль",
            "Invalid old password",
        ]), "Не нашли ошибку для неверного старого пароля"