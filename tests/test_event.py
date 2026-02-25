from services.login_flow import LoginFlow
from services.event_flow import EventFlow
from config import config


def test_30887_events_one_time_login_only(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event()

    flow.return_to_events_list()
    card = flow.open_event_from_list(event_id)

    assert card.is_visible(), f"Мероприятие c id={event_id} найдено, но не отображается в списке"