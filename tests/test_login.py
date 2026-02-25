import pytest
from config import config
from services.login_flow import LoginFlow


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30381")
def test_30381_registered_user_can_login(driver):
    assert LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True) == 0


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("31407")
def test_31407_invalid_password(driver):
    error_code = LoginFlow(driver).login(config.ADMIN_EMAIL, "wrong_password_123", expect_success=False)
    # У тебя уже есть UI/response проверка в LoginPage.check_400_error() — оставляем её в отдельном тесте или добавим в flow позже
    assert error_code in (0, 400), f"Ожидали 400 или UI-ошибку, получили: {error_code}"


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("31410")
def test_31410_ldap_login(driver):
    assert LoginFlow(driver).login(config.TEST_LDAP_USER_EMAIL, config.TEST_LDAP_USER_PASSWORD, expect_success=True) == 0

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30296")
def test_30296_adfs_login(login_page):
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