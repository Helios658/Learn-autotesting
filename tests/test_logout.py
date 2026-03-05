import pytest
from config import config
from services.login_flow import LoginFlow
from services.logout_flow import LogoutFlow


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("14")
def test_14_logout_menu(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    assert LogoutFlow(driver).logout_via_menu()


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("15")
def test_15_logout_profile(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    assert LogoutFlow(driver).logout_via_profile()