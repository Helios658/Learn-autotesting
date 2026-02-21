import pytest
from config import config


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30545")
def test_30545_logout_menu(login_page, driver):
    error_code = login_page.login_with_network_check(
        username=config.ADMIN_EMAIL,
        password=config.ADMIN_PASSWORD,
        expect_success=True,
    )
    assert error_code == 0

    driver.locator(".participant").first.click()
    driver.locator("[e2e-id='profile-action__logout']").first.click()
    driver.wait_for_url("**/login**", timeout=config.EXPLICIT_WAIT * 1000)

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30255")
def test_30255_logout_profile(login_page, driver):
    error_code = login_page.login_with_network_check(
        username=config.ADMIN_EMAIL,
        password=config.ADMIN_PASSWORD,
        expect_success=True,
    )
    assert error_code == 0

    driver.locator("[e2e-id='shared-core.navigation-menu.settings']").first.click()
    driver.locator("[e2e-id='settings-page.list.profile']").first.click()
    driver.locator("[e2e-id='settings-page.profile.logout-link']").first.click()
    driver.wait_for_url("**/login**", timeout=config.EXPLICIT_WAIT * 1000)