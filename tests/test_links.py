import pytest
from config import config
from services.event_flow import EventFlow
from services.login_flow import LoginFlow


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30392")
def test_30392_guest_link_not_registered_user(driver):
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



@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30794")
def test_30794_quest_link_registered_user_no_authorization(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    guest_url = flow.get_guest_link_for_event(event_id)

    assert "join:" in guest_url, f"Некорректная гостевая ссылка: {guest_url}"

    final_url, is_joined = flow.join_via_guest_link_as_registered_user(
        guest_url=guest_url,
        username=config.TEST_USER2_EMAIL,
        password=config.TEST_USER2_PASSWORD,
    )

    assert is_joined, f"UI не подтвердил вход в конференцию, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("31121")
def test_31121_guest_link_ldap_user_no_authorization(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    guest_url = flow.get_guest_link_for_event(event_id)

    assert "join:" in guest_url, f"Некорректная гостевая ссылка: {guest_url}"

    final_url, is_joined = flow.join_via_guest_link_as_registered_user(
        guest_url=guest_url,
        username=config.TEST_LDAP_USER_EMAIL,
        password=config.TEST_LDAP_USER_PASSWORD,
    )

    assert is_joined, f"UI не подтвердил вход в конференцию, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"



@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30393")
def test_30393_guest_link_registered_user_no_authorization(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    guest_url = flow.get_guest_link_for_event(event_id)

    assert "join:" in guest_url, f"Некорректная гостевая ссылка: {guest_url}"

    final_url, is_joined = flow.join_via_guest_link_as_registered_user_login_before_open_guest_link(
        guest_url=guest_url,
        username=config.TEST_USER2_EMAIL,
        password=config.TEST_USER2_PASSWORD,
    )

    assert is_joined, f"UI не подтвердил вход в конференцию, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30435")
def test_30435_speaker_link_not_registered_user(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    speaker_url = flow.get_speaker_link_for_event(event_id)

    assert "join:" in speaker_url, f"Некорректная ссылка докладчика: {speaker_url}"

    join_result = flow.join_guest_via_link(speaker_url, guest_name="Auto Guest")

    is_joined = None
    if isinstance(join_result, tuple):
        final_url, is_joined = join_result
    else:
        final_url = join_result

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url

    assert is_conference_url or is_join_url, (
        f"После входа по ссылке докладчика получен неожиданный URL: {final_url}"
    )

    if is_joined is not None:
        assert is_joined, f"UI не подтвердил вход в конференцию по ссылке докладчика, URL: {final_url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("31412")
def test_31412_speaker_link_not_speaker_user(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    speaker_url = flow.get_speaker_link_for_event(event_id)

    assert "join:" in speaker_url, f"Некорректная ссылка докладчика: {speaker_url}"

    final_url, is_joined = flow.join_via_guest_link_as_registered_user(
        guest_url=speaker_url,
        username=config.TEST_USER2_EMAIL,
        password=config.TEST_USER2_PASSWORD,
    )

    assert is_joined, f"UI не подтвердил вход в конференцию, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30394")
def test_30394_speaker_link_registered_user_no_authorization(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    speaker_url = flow.get_speaker_link_for_event(event_id)

    assert "join:" in speaker_url, f"Некорректная гостевая ссылка: {speaker_url}"

    final_url, is_joined = flow.join_via_guest_link_as_registered_user_login_before_open_guest_link(
        guest_url=speaker_url,
        username=config.TEST_USER2_EMAIL,
        password=config.TEST_USER2_PASSWORD,
    )

    assert is_joined, f"UI не подтвердил вход в конференцию, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30855")
def test_30855_guest_link_adfs_user_no_authorization(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    guest_url = flow.get_guest_link_for_event(event_id)

    assert "join:" in guest_url, f"Некорректная гостевая ссылка: {guest_url}"

    final_url, is_joined = flow.join_via_guest_link_as_adfs_user(
        guest_url=guest_url,
        username=config.TEST_ADFS_USER_EMAIL,
        password=config.TEST_ADFS_USER_PASSWORD,
    )

    assert is_joined, f"UI не подтвердил вход в конференцию, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"