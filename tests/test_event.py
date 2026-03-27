import pytest
from config import config
from services.login_flow import LoginFlow
from services.event_flow import EventFlow


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("1")
def test_1_events_one_time_login_only(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)

    assert event_id in (driver.url or ""), (
        f"После создания не остались в карточке мероприятия {event_id}. URL: {driver.url}"
    )