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
    event_id = flow.create_event()

    card = flow.open_event_from_list(event_id)
    assert card.is_visible(), f"Мероприятие {event_id} не отображается"