import time
import pytest
from playwright.sync_api import Error as PlaywrightError
from config import config
from services.event_flow import EventFlow
from services.login_flow import LoginFlow
from pages.mail_page import InvitationLinkNotFoundError
from pages.guest_join_page import GuestJoinPage


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
def test_23_link_for_the_invited(driver, mail_page_session):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    invited_email = config.USER_EMAIL
    invited_password = config.USER_PASSWORD
    assert invited_email, "Не задан email приглашенного пользователя"
    assert invited_password, "Не задан пароль приглашенного пользователя"

    mail_page = mail_page_session
    invitation_baseline = mail_page.snapshot_invitation_emails()

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    flow.add_participant_in_event(invited_email)

    assert event_id in (driver.url or ""), (
        f"После приглашения участника потеряли текущую конференцию: {driver.url}"
    )

    mail_page.open_invitation_email(wait_for_email=True, exclude_signatures=invitation_baseline)
    invited_join_link = mail_page.get_invitation_join_link()
    assert "join:" in invited_join_link, f"Не удалось извлечь ссылку приглашения: {invited_join_link}"


    final_url, is_joined = flow.join_via_guest_link_as_registered_user_login_before_open_guest_link(
        guest_url=invited_join_link,
        username=invited_email,
        password=invited_password,
    )

    assert is_joined, f"UI не подтвердил вход в конференцию приглашенного пользователя, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"

@pytest.mark.buildtest
@pytest.mark.testcase("24")
def test_24_ticket_link_registered_user_with_authorization(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    ticket_user_email = config.TEST_USER2_EMAIL
    ticket_user_password = config.TEST_USER2_PASSWORD
    assert ticket_user_email, "Не задан email пользователя для ticket-ссылки"
    assert ticket_user_password, "Не задан пароль пользователя для ticket-ссылки"

    flow = EventFlow(driver)
    flow.switch_to_legacy_web_interface()

    ticket_url = flow.create_legacy_event_and_get_single_ticket_link()
    assert ticket_url.startswith("http"), f"Некорректная ticket-ссылка: {ticket_url}"

    final_url, is_joined = flow.join_via_ticket_link_as_registered_user_login_before_open_ticket_link(
        ticket_url=ticket_url,
        username=ticket_user_email,
        password=ticket_user_password,
    )

    assert is_joined, f"UI не подтвердил вход в мероприятие по ticket-ссылке, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"

@pytest.mark.buildtest
@pytest.mark.testcase("25")
def test_25_ticket_link_registered_user_with_authorization_open_link_first(driver):
    """Сценарий: сразу открыть ticket-ссылку в incognito и войти через 'У меня есть аккаунт'."""
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    ticket_user_email = config.TEST_USER2_EMAIL
    ticket_user_password = config.TEST_USER2_PASSWORD
    assert ticket_user_email, "Не задан email пользователя для ticket-ссылки"
    assert ticket_user_password, "Не задан пароль пользователя для ticket-ссылки"

    flow = EventFlow(driver)
    flow.switch_to_legacy_web_interface()

    ticket_url = flow.create_legacy_event_and_get_single_ticket_link()
    assert ticket_url.startswith("http"), f"Некорректная ticket-ссылка: {ticket_url}"

    final_url, is_joined = flow.join_via_ticket_link_as_registered_user(
        ticket_url=ticket_url,
        username=ticket_user_email,
        password=ticket_user_password,
    )

    assert is_joined, f"UI не подтвердил вход в мероприятие по ticket-ссылке, URL: {final_url}"

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа получен неожиданный URL: {final_url}"

@pytest.mark.buildtest
@pytest.mark.testcase("26")
def test_26_ticket_link_guest_user_open_link_first(driver):
    """Сценарий: сразу открыть ticket-ссылку в incognito и войти как гость."""
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    flow.switch_to_legacy_web_interface()

    ticket_url = flow.create_legacy_event_and_get_single_ticket_link()
    assert ticket_url.startswith("http"), f"Некорректная ticket-ссылка: {ticket_url}"

    final_url = flow.join_via_ticket_link_as_guest(
        ticket_url=ticket_url,
        guest_name="Auto Guest",
    )

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?token=" in final_url
    assert is_conference_url or is_join_url, f"После входа гостем получен неожиданный URL: {final_url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("27")
def test_27_registration_link_authorized_user(driver, mail_page_session):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    event_page = flow.event_page
    mail_page = mail_page_session
    invitation_baseline = mail_page.snapshot_invitation_emails()

    event_page.open()
    event_page.click_add()
    event_page.select_simple_event_template()
    event_page.enable_registration_form()
    event_page.click_plan_draft()

    registration_url = ""
    for _ in range(3):
        event_page.close_event_start_popup_if_present()
        event_page.click_copy_registration_link()
        driver.wait_for_timeout(600)
        registration_url = (flow._read_link_from_clipboard() or "").strip()
        if registration_url.startswith("http") or "join:" in registration_url:
            break

    assert registration_url.startswith("http") or "join:" in registration_url, (
        f"Некорректная ссылка регистрации: {registration_url}"
    )

    registration_email = "v.kornienko@iva-tech.ru"
    registration_password = config.USER_PASSWORD

    guest_context, guest_page = flow.submit_registration_link_and_login(
        registration_url=registration_url,
        email=registration_email,
        password=registration_password,
    )

    try:
        mail_page.open_invitation_email(wait_for_email=True, exclude_signatures=invitation_baseline)
        invited_join_link = mail_page.get_invitation_join_link()

        assert "join:" in invited_join_link, (
            f"Не удалось извлечь ссылку приглашения: {invited_join_link}"
        )

        guest_page.goto(invited_join_link, wait_until="domcontentloaded")
        guest_page.wait_for_load_state("domcontentloaded")

        guest_join_page = GuestJoinPage(guest_page)
        is_joined = guest_join_page.finalize_join_from_mail_link(timeout_ms=20_000)

        final_url = guest_page.url
        is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
        is_join_url = "/v2/join?token=" in final_url

        assert is_joined, f"Не удалось завершить вход по ссылке из письма. URL: {final_url}"
        assert is_conference_url or is_join_url, (
            f"После перехода по ссылке из письма получен неожиданный URL: {final_url}"
        )

    finally:
        guest_context.close()


@pytest.mark.buildtest
@pytest.mark.testcase("32")
def test_32_sid_link_for_unregistered_invited_user(driver, mail_page_session):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    invited_email = config.TEST_UNREGISTED_USER_EMAIL
    assert invited_email, "Не задан TEST_UNREGISTED_USER_EMAIL для проверки sid-ссылки"

    mail_page = mail_page_session
    invitation_baseline = mail_page.snapshot_invitation_emails()

    flow = EventFlow(driver)
    event_id = flow.create_event(return_to_list=False)
    flow.add_participant_in_event(invited_email)

    assert event_id in (driver.url or ""), (
        f"После приглашения пользователя потеряли текущую конференцию: {driver.url}"
    )

    mail_page.open_invitation_email(wait_for_email=True, exclude_signatures=invitation_baseline)
    sid_link = mail_page.get_invitation_sid_link()
    assert "sid=" in sid_link.lower(), f"Не удалось извлечь sid-ссылку приглашения: {sid_link}"

    guest_context, guest_page = flow.open_guest_link_in_incognito(sid_link)
    try:
        GuestJoinPage(guest_page).click_join_after_mail_link()
        guest_page.wait_for_load_state("domcontentloaded")
        final_url = guest_page.url
    finally:
        guest_context.close()

    is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
    is_join_url = "/v2/join?" in final_url and "token=" in final_url
    assert is_conference_url or is_join_url, (
        f"После входа по sid-ссылке получен неожиданный URL: {final_url}"
    )

@pytest.mark.buildtest
@pytest.mark.testcase("33")
def test_33_registration_link_unregistered_user_via_name_step(driver, mail_page_session):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    flow = EventFlow(driver)
    mail_page = mail_page_session
    invitation_baseline = mail_page.snapshot_invitation_emails()
    invited_email = config.TEST_UNREGISTED_USER_EMAIL
    assert invited_email, "Не задан TEST_UNREGISTED_USER_EMAIL для регистрации незарегистрированного пользователя"

    event_id = flow.create_event_draft_with_registration(return_to_list=False)
    registration_url = flow.get_registration_link_for_event(event_id)

    assert registration_url, "Не получили ссылку регистрации"
    assert registration_url.startswith("http") or "join:" in registration_url, (
        f"Некорректная ссылка регистрации: {registration_url}"
    )
    driver.wait_for_timeout(15_000)

    guest_context, guest_page = flow.submit_registration_link_without_login(
        registration_url=registration_url,
        email=invited_email,
        name="Auto Unregistered",
    )

    try:
        mail_page.open_invitation_email(wait_for_email=True, exclude_signatures=invitation_baseline)

        try:
            invited_link = mail_page.get_invitation_sid_link()
        except InvitationLinkNotFoundError:
            invited_link = mail_page.get_invitation_join_link()

        assert invited_link.startswith("http"), f"Не удалось извлечь ссылку входа из письма: {invited_link}"

        guest_page.goto(invited_link, wait_until="domcontentloaded")
        guest_page.wait_for_load_state("domcontentloaded")
        guest_page.wait_for_timeout(1500)

        guest_join_page = GuestJoinPage(guest_page)
        try:
            guest_join_page.click_join_after_mail_link()
        except (AssertionError, PlaywrightError):
            pass
        guest_page.wait_for_timeout(1200)
        guest_join_page.click_enter_on_prejoin_screen()
        guest_page.wait_for_timeout(1200)

        is_joined = guest_join_page.finalize_join_from_mail_link(timeout_ms=90_000)

        final_url = guest_page.url
        is_conference_url = "/v2/iva/home/conferences" in final_url and "conferenceSessionId=" in final_url
        is_direct_conference_url = "/v2/iva/conference/" in final_url and "conferenceSessionId=" in final_url
        is_join_url = "/v2/join?" in final_url and "token=" in final_url

        assert is_joined, f"Не удалось завершить вход по ссылке из письма после регистрации. URL: {final_url}"
        assert is_conference_url or is_direct_conference_url or is_join_url, (
            f"После перехода по ссылке из письма получен неожиданный URL: {final_url}"
        )
    finally:
        guest_context.close()