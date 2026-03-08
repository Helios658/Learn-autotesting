import time
import pytest
from config import config
from services.event_flow import EventFlow
from services.login_flow import LoginFlow


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("2")
def test_2_guest_link_not_registered_user(driver):
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
@pytest.mark.testcase("3")
def test_3_quest_link_registered_user_no_authorization(driver):
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
@pytest.mark.testcase("4")
def test_4_guest_link_ldap_user_no_authorization(driver):
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
@pytest.mark.testcase("5")
def test_5_guest_link_registered_user_with_authorization(driver):
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
@pytest.mark.testcase("6")
def test_6_speaker_link_not_registered_user(driver):
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
@pytest.mark.testcase("7")
def test_7_speaker_link_registered_no_authorization(driver):
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
@pytest.mark.testcase("8")
def test_8_speaker_link_registered_user_with_authorization(driver):
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
@pytest.mark.testcase("9")
def test_9_guest_link_adfs_user_no_authorization(driver):
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

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("18")
def test_18_moderator_link_not_registered_user(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    moderator_url = flow.get_moderator_link_for_event(event_id)

    assert "join:" in moderator_url, f"Некорректная ссылка докладчика: {moderator_url}"

    join_result = flow.join_guest_via_link(moderator_url, guest_name="Auto Guest")

    is_joined = None
    if isinstance(join_result, tuple):
        final_url, is_joined = join_result
    else:
        final_url = join_result

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url

    assert is_conference_url or is_join_url, (
        f"После входа по ссылке модератора получен неожиданный URL: {final_url}"
    )

    if is_joined is not None:
        assert is_joined, f"UI не подтвердил вход в конференцию по ссылке модератора, URL: {final_url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("19")
def test_19_moderator_link_registered_no_authorization(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    moderator_url = flow.get_moderator_link_for_event(event_id)

    assert "join:" in moderator_url, f"Некорректная ссылка докладчика: {moderator_url}"

    final_url, is_joined = flow.join_via_guest_link_as_registered_user(
        guest_url=moderator_url,
        username=config.TEST_USER2_EMAIL,
        password=config.TEST_USER2_PASSWORD,
    )
    assert is_joined, f"UI не подтвердил вход в конференцию, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("20")
def test_20_moderator_link_registered_user_with_authorization(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    moderator_url = flow.get_moderator_link_for_event(event_id)

    assert "join:" in moderator_url, f"Некорректная гостевая ссылка: {moderator_url}"

    final_url, is_joined = flow.join_via_guest_link_as_registered_user_login_before_open_guest_link(
        guest_url=moderator_url,
        username=config.TEST_USER2_EMAIL,
        password=config.TEST_USER2_PASSWORD,
    )

    assert is_joined, f"UI не подтвердил вход в конференцию, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("21")
def test_21_guest_link_registered_ldap_with_authorization(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    guest_url = flow.get_guest_link_for_event(event_id)

    assert "join:" in guest_url, f"Некорректная гостевая ссылка: {guest_url}"

    final_url, is_joined = flow.join_via_guest_link_as_registered_user_login_before_open_guest_link(
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
@pytest.mark.testcase("22")
def test_22_guest_link_registered_adfs_with_authorization(driver):
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

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("23")
def test_23_link_for_the_invited(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    #Так мы создаем эвент завтра надо:
    #1)Открыть список участников
    #2)Добавить открытие списка в event_page
    #3)Добавить приглашение пользователя в мероприятие в event_flow
    #4)Открыть почту
    #5)Перейти по ссылке
    #6)У меня есть аккаунт
    #7)Ввести логин и пароль
