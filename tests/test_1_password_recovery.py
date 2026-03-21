import allure
import pytest

from config import config
from pages.change_password_modal_page import ChangePasswordModalPage
from pages.login_page import LoginPage
from services.password_recovery_flow import PasswordRecoveryFlow
from services.password_service import PasswordService

CURRENT_PASSWORD = "__CURRENT_PASSWORD__"


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
        "change_password_modal": ChangePasswordModalPage(driver),
    }


def _resolve_password(value, current_password: str):
    return current_password if value == CURRENT_PASSWORD else value


def run_password_validation_step(change_password_modal: ChangePasswordModalPage, current_password: str, case: dict):
    change_password_modal.fill_form(
        old_password=_resolve_password(case["old_password"], current_password),
        new_password=_resolve_password(case["new_password"], current_password),
        confirm_password=_resolve_password(case["confirm_password"], current_password),
    ).save()

    for expected_group in case["expected_messages"]:
        change_password_modal.assert_any_error_text(expected_group, timeout=case.get("timeout", 5))


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
    ctx = login_for_password_change(driver)
    login_page = ctx["login_page"]
    current_password = ctx["current_password"]
    password_service = ctx["password_service"]
    change_password_modal = ctx["change_password_modal"]

    change_password_modal.open_from_profile()

    new_password = password_service.generate_and_persist_password()
    change_password_modal.fill_form(
        old_password=current_password,
        new_password=new_password,
        confirm_password=new_password,
    ).save()

    change_password_modal.logout_from_profile()
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
    change_password_modal = ctx["change_password_modal"]

    change_password_modal.open_from_profile()
    cases = [
        {
            "title": "Не заполнять поля и нажать сохранить",
            "old_password": None,
            "new_password": None,
            "confirm_password": None,
            "expected_messages": [
                ["Необходимо ввести старый пароль", "Old password can't be empty"],
                ["Необходимо ввести новый пароль", "New password can't be empty"],
            ],
        },
        {
            "title": "Ввести верный старый пароль, новый пароль и неверное подтверждение",
            "old_password": CURRENT_PASSWORD,
            "new_password": "NewPassword123",
            "confirm_password": "AnotherPassword123",
            "expected_messages": [
                [
                    "Новый пароль и подтверждение пароля не совпадают",
                    "New password and password confirmation do not match",
                ]
            ],
        },
        {
            "title": "Ввести верный старый пароль и слишком короткий новый пароль",
            "old_password": CURRENT_PASSWORD,
            "new_password": "123",
            "confirm_password": "123",
            "expected_messages": [
                ["Новый пароль должен быть не менее", "New password must be at least"]
            ],
        },
        {
            "title": "Не вводить старый пароль, ввести новый пароль и подтверждение",
            "old_password": None,
            "new_password": "ValidPass123",
            "confirm_password": "ValidPass123",
            "expected_messages": [
                ["Необходимо ввести старый пароль", "Old password can't be empty"]
            ],
        },
        {
            "title": "Ввести неверный старый пароль",
            "old_password": "WrongOldPassword123",
            "new_password": "ValidPass123",
            "confirm_password": "ValidPass123",
            "expected_messages": [
                ["Неверно указан старый пароль", "Invalid old password"]
            ],
            "timeout": 7,
        },
    ]

    for case in cases:
        with allure.step(case["title"]):
            run_password_validation_step(change_password_modal, current_password=current_password, case=case)