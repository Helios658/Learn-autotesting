import pytest

from config import config
from services.event_flow import EventFlow
from services.login_flow import LoginFlow


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("XXXX")
def test_guest_link_not_registred_user(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    guest_url = flow.get_guest_link_for_event(event_id)

    # Проверяем, что ссылку вообще получили, а затем выполняем join.
    assert "join:" in guest_url, f"Некорректная гостевая ссылка: {guest_url}"

    join_result = flow.join_guest_via_link(guest_url, guest_name="Auto Guest")

    # Совместимость: helper мог вернуть (url, flag) или только url.
    is_joined = None
    if isinstance(join_result, tuple):
        final_url, is_joined = join_result
    else:
        final_url = join_result

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url

    assert is_conference_url or is_join_url, (
        f"После входа получен неожиданный URL: {final_url}"
    )

    if is_joined is not None:
        assert is_joined, f"UI не подтвердил вход в конференцию, URL: {final_url}"