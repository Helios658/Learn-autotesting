import pytest
from config import config
from services.login_flow import LoginFlow
from services.navigator_flow import NavigatorFlow

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("34")
def test_34_open_administration_from_profile_menu(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    navigator = NavigatorFlow(driver)
    navigator.click_administration_menu()

    driver.wait_for_timeout(1200)
    target_page = driver.context.pages[-1]
    target_page.wait_for_url("**/administration.html", timeout=config.EXPLICIT_WAIT * 1000)

    final_url = (target_page.url or "").split("?")[0].rstrip("/")
    assert final_url == "https://gamma.hi-tech.org/administration.html", (
        f"Ожидали страницу администрирования, получили: {target_page.url}"
    )