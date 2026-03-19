import pytest
from config import config
from services.login_flow import LoginFlow
from pages.login_page import LoginPage
from pages.mail_page import MailPage


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("10")
def test_10_registered_user_can_login(driver):
    assert LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True) == 0


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("11")
def test_11_invalid_password(driver):
    error_code = LoginFlow(driver).login(config.ADMIN_EMAIL, "wrong_password_123", expect_success=False)
    has_login_error = LoginPage(driver).check_400_error(timeout=config.EXPLICIT_WAIT)
    assert error_code == 400 or has_login_error, (
        f"Ожидали HTTP 400 или явную UI-ошибку авторизации, получили: error_code={error_code}, url={driver.url}"
    )


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("12")
def test_12_ldap_login(driver):
    assert LoginFlow(driver).login(config.TEST_LDAP_USER_EMAIL, config.TEST_LDAP_USER_PASSWORD, expect_success=True) == 0

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("13")
def test_13_adfs_login(login_page):
    username_adfs = config.TEST_ADFS_USER_EMAIL
    password_adfs = config.TEST_ADFS_USER_PASSWORD

    login_page.open()
    login_page.click_show_all()
    login_page.adfs_link_open()
    login_page.enter_username_adfs(username_adfs)
    login_page.enter_password_adfs(password_adfs)

    assert login_page.get_entered_username_adfs() == username_adfs
    assert login_page.get_entered_password_adfs() == password_adfs

    login_page.click_login_button_adfs()
    assert login_page.wait_for_successful_login(timeout=config.EXPLICIT_WAIT * 2), (
        f"ADFS логин неуспешен, текущий URL: {login_page.page.url}"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("28")
def test_28_2fa_login(driver):
    flow = LoginFlow(driver)
    result = LoginFlow(driver).login_with_2fa(
        username=config.TEST_2FA_USER_EMAIL,
        password=config.TEST_2FA_USER_PASSWORD,
    )
    assert result == 0

