import pytest
from urllib.parse import parse_qs, urlparse
from config import config
from services.login_flow import LoginFlow
from pages.chat_page import ChatPage
from utils.generate_random_message import generate_unique_message
import time
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from services.chat_flow import ChatFlow


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30")
def test_30_create_or_open_p2p_chat_with_test_user2(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.create_or_open_p2p_chat(config.TEST_USER2_EMAIL)

    assert chat_page.is_p2p_chat_opened(config.TEST_USER2_EMAIL), (
        "P2P чат с TEST_USER2 не открылся"
    )


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("31")
def test_31_send_and_receive_text_message_p2p(two_users):
    page_a = two_users["a"]
    page_a1 = two_users["a1"]

    message_text = generate_unique_message("autotest-31")

    LoginFlow(page_a).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    LoginFlow(page_a1).login(config.TEST_USER2_EMAIL, config.TEST_USER2_PASSWORD, expect_success=True)

    chat_a = ChatPage(page_a)
    chat_a1 = ChatPage(page_a1)

    chat_a.open()
    chat_a.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    with page_a.expect_response("**/send-message") as response_info:
        chat_a.send_message(message_text)

    response = response_info.value
    assert response.ok, "Запрос send-message завершился неуспешно"

    payload = response.json()
    assert payload["message"] == message_text, (
        f"В send-message вернулся не тот текст: {payload}"
    )

    chat_a1.open()
    chat_a1.open_existing_p2p_chat_via_search(config.ADMIN_EMAIL)

    assert chat_a1.wait_for_message(message_text), (
        f"A1 не получил сообщение: {message_text}"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("35")
def test_35_create_group_chat_and_capture_chat_id(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    flow = ChatFlow(driver)
    participants = flow.pick_group_participants(required_count=2)
    chat_id = flow.create_group_chat(participants)

    chat_page = flow.chat_page
    unique_group_name = f"autotest-group-{chat_id[:8]}"
    chat_page.rename_opened_chat(unique_group_name)


@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("36")
def test_36_convert_existing_p2p_chat_to_group_chat(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    chat_page.create_group_chat_from_opened_p2p()

    participant_to_add = config.TEST_LDAP_USER_EMAIL
    assert participant_to_add, "Для теста 36 должен быть задан TEST_LDAP_USER_EMAIL."
    assert participant_to_add not in {config.ADMIN_EMAIL, config.TEST_USER2_EMAIL}, (
        "TEST_LDAP_USER_EMAIL должен отличаться от ADMIN и TEST_USER2."
    )

    chat_page.search_user_for_new_chat(participant_to_add)
    chat_page.select_user_checkbox_from_new_chat_results(participant_to_add)

    chat_page.click_create_chat_submit()

    driver.locator(chat_page.CHAT_HEADER).first.wait_for(
        state="visible",
        timeout=config.EXPLICIT_WAIT * 1000,
    )

    unique_group_name = f"autotest-converted-{int(time.time())}"
    rename_error = None
    for _ in range(3):
        try:
            chat_page.rename_opened_chat(unique_group_name)
            rename_error = None
            break
        except (PlaywrightTimeoutError, AssertionError) as exc:
            rename_error = exc
            driver.wait_for_timeout(1500)

    assert rename_error is None, (
        f"Не удалось переименовать чат после конвертации p2p->group: {rename_error}"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("37")
def test_37_edit_last_sent_message_p2p(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    original_text = generate_unique_message("autotest-37")
    edited_text = generate_unique_message("autotest-37-edit")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(original_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message завершился неуспешно"
    assert chat_page.wait_for_message(original_text), (
        f"Не удалось дождаться отправленного сообщения: {original_text}"
    )

    chat_page.open_context_menu_for_last_own_message()
    chat_page.click_edit_message_action()

    with driver.expect_response(
        lambda r: "/api/rest/chats/" in r.url and "/messages/" in r.url and r.request.method in ("PUT", "PATCH")
    ) as edit_response_info:
        chat_page.send_message(edited_text)

    edit_response = edit_response_info.value
    assert edit_response.ok, f"Запрос редактирования завершился неуспешно: {edit_response.status}"

    assert chat_page.wait_for_last_own_message_text(edited_text), (
        f"Текст последнего сообщения не обновился до ожидаемого значения: '{edited_text}'"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("38")
def test_38_copy_last_sent_message_and_resend_p2p(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    original_text = generate_unique_message("autotest-38")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(original_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message завершился неуспешно"
    assert chat_page.wait_for_message(original_text), (
        f"Не удалось дождаться отправленного сообщения: {original_text}"
    )

    chat_page.open_context_menu_for_last_own_message()
    chat_page.click_copy_message_action()

    copied_text = chat_page.paste_clipboard_to_message_input()
    assert copied_text == original_text, (
        f"Скопированный текст не совпадает с исходным. "
        f"Ожидалось: '{original_text}', получено: '{copied_text}'"
    )

    with driver.expect_response("**/send-message") as resend_response_info:
        chat_page.click_send()

    resend_response = resend_response_info.value
    assert resend_response.ok, "Запрос повторной отправки сообщения завершился неуспешно"

    payload = resend_response.json()
    assert payload["message"] == original_text, (
        f"В повторном send-message вернулся не тот текст: {payload}"
    )
    assert chat_page.wait_for_last_own_message_text(original_text), (
        "Последнее отправленное сообщение не совпадает со скопированным текстом"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("39")
def test_39_copy_message_link_and_send_p2p(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    original_text = generate_unique_message("gamma.hi-tech.org autotest-39")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(original_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message завершился неуспешно"
    assert chat_page.wait_for_message(original_text), (
        f"Не удалось дождаться отправленного сообщения: {original_text}"
    )

    chat_page.open_context_menu_for_last_own_message()
    chat_page.click_copy_message_link_action()

    copied_link = chat_page.paste_clipboard_to_message_input().strip()
    assert "gamma.hi-tech.org" in copied_link, (
        f"Скопированная ссылка не содержит ожидаемый домен: {copied_link}"
    )

    with driver.expect_response("**/send-message") as resend_response_info:
        chat_page.click_send()

    resend_response = resend_response_info.value
    assert resend_response.ok, "Запрос отправки скопированной ссылки завершился неуспешно"

    payload = resend_response.json()
    assert payload["message"] == copied_link, (
        f"В send-message вернулся не тот текст ссылки: {payload}"
    )
    assert chat_page.wait_for_last_own_message_text(copied_link), (
        "Последнее отправленное сообщение не совпадает со скопированной ссылкой"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("40")
def test_40_delete_last_sent_message_p2p(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    message_text = generate_unique_message("autotest-40")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(message_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message завершился неуспешно"
    assert chat_page.wait_for_message(message_text), (
        f"Не удалось дождаться отправленного сообщения: {message_text}"
    )

    chat_page.open_context_menu_for_last_own_message()

    with driver.expect_response(
        lambda r: (
            "/api/rest/chats/" in r.url
            and (
                ("/messages/" in r.url and r.request.method == "DELETE")
                or ("/messages/remove" in r.url and r.request.method in ("POST", "DELETE"))
            )
        )
    ) as delete_response_info:
        chat_page.click_delete_message_action()
        chat_page.try_confirm_delete_message_action(timeout_ms=3500)

    delete_response = delete_response_info.value
    assert delete_response.ok, f"Запрос удаления сообщения завершился неуспешно: {delete_response.status}"
    assert chat_page.wait_for_message_absent(message_text), (
        f"Сообщение не удалилось из списка сообщений: {message_text}"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("41")
def test_41_clear_p2p_chat(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    chat_page.click_clear_chat()

    with driver.expect_response(
        lambda r: (
            "/api/rest/chats/" in r.url
            and "/clear-history" in r.url
            and r.request.method == "POST"
        )
    ) as clear_response_info:
        chat_page.confirm_clear_chat()

    response = clear_response_info.value

    assert response.ok, f"Очистка чата завершилась неуспешно: status={response.status}, url={response.url}"

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("42")
def test_42_clear_group_chat(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    flow = ChatFlow(driver)
    participants = flow.pick_group_participants(required_count=2)
    chat_id = flow.create_group_chat(participants)
    chat_page = flow.chat_page

    chat_page.click_clear_chat()

    with driver.expect_response(
        lambda r: (
            "/api/rest/chats/" in r.url
            and "/clear-history" in r.url
            and r.request.method == "POST"
        )
    ) as clear_response_info:
        chat_page.confirm_clear_chat()

    response = clear_response_info.value

    assert response.ok, f"Очистка чата завершилась неуспешно: status={response.status}, url={response.url}"

    unique_group_name = f"autotest42-group-{chat_id[:8]}"
    chat_page.rename_opened_chat(unique_group_name)

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("43")
def test_43_reply_to_last_message_p2p(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)

    original_text = generate_unique_message("autotest-43-original")
    reply_text = generate_unique_message("autotest-43-reply")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(original_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message для исходного сообщения завершился неуспешно"
    assert chat_page.wait_for_last_own_message_text(original_text), (
        f"Не удалось дождаться исходного сообщения перед ответом: {original_text}"
    )

    chat_page.open_context_menu_for_last_own_message()
    chat_page.click_reply_message_action()

    assert chat_page.is_message_context_menu_closed(), (
        "Список действий с сообщением не закрылся после выбора действия 'Ответить'"
    )

    with driver.expect_response("**/send-message") as reply_response_info:
        chat_page.focus_message_input()
        chat_page.type_message(reply_text)
        chat_page.click_send()

    reply_response = reply_response_info.value
    assert reply_response.ok, "Запрос send-message для ответа завершился неуспешно"
    assert chat_page.wait_for_last_own_message_text(reply_text), (
        f"Ответ на сообщение не появился в истории: {reply_text}"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("44")
def test_44_forward_last_message_to_ldap_user(driver):
    LoginFlow(driver).login(config.TEST_USER2_EMAIL, config.TEST_USER2_PASSWORD, expect_success=True)

    ldap_user = config.TEST_LDAP_USER_EMAIL
    assert ldap_user, "Для теста 44 должен быть задан TEST_LDAP_USER_EMAIL."
    assert ldap_user != config.TEST_USER2_EMAIL, "Получатель пересылки должен отличаться от отправителя."

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_existing_p2p_chat_via_search(config.ADMIN_EMAIL)

    original_text = generate_unique_message("autotest-44-forward")

    with driver.expect_response("**/send-message") as send_response_info:
        chat_page.send_message(original_text)
    send_response = send_response_info.value
    assert send_response.ok, "Запрос send-message для исходного сообщения завершился неуспешно"
    assert chat_page.wait_for_last_own_message_text(original_text), (
        f"Не удалось дождаться исходного сообщения перед пересылкой: {original_text}"
    )

    chat_page.open_context_menu_for_last_own_message()
    chat_page.click_forward_message_action()
    assert chat_page.is_message_context_menu_closed(), (
        "Список действий с сообщением не закрылся после выбора действия 'Переслать'"
    )

    chat_page.forward_last_own_message_to_recipient(ldap_user)

    ldap_identifier = ldap_user.split("@")[0]
    assert chat_page.wait_for_chat_title_contains(ldap_identifier), (
        "После пересылки не открылся чат с LDAP пользователем"
    )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("45")
def test_45_interactive_chat_search(driver):
    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    chat_page = ChatPage(driver)
    chat_page.open()
    chat_page.open_chat_search()

    total_chats_before_search = chat_page.get_chat_list_count()
    assert total_chats_before_search > 0, "Перед началом теста список чатов пуст."

    chat_page.set_chat_search_text("")
    assert chat_page.get_chat_search_value() == "", "Строка поиска должна быть пустой после очистки."
    assert chat_page.is_chat_search_visible(), "Строка поиска не должна закрываться после очистки."

    total_chats_after_clear = chat_page.get_chat_list_count()
    assert total_chats_after_clear >= total_chats_before_search, (
        "После очистки поиска должен отображаться полный список чатов."
    )

    def search_and_get_payload(search_term: str) -> dict:
        def is_expected_search_response(response) -> bool:
            if "/api/rest/chats/search" not in response.url:
                return False
            try:
                query = parse_qs(urlparse(response.url).query)
                return query.get("searchCriteria", [""])[0] == search_term
            except Exception:
                return False

        with driver.expect_response(is_expected_search_response) as search_response_info:
            chat_page.set_chat_search_text(search_term)

        search_response = search_response_info.value
        assert search_response.ok, (
            f"Поисковый запрос '{search_term}' завершился неуспешно: {search_response.status}"
        )
        return search_response.json()

    payload_check = search_and_get_payload("test@test")
    assert payload_check.get("data"), "Поиск 'test@test' должен вернуть результаты."

    payload_no_results = search_and_get_payload("провер1")
    assert not payload_no_results.get("data"), "Поиск 'провер1' не должен вернуть результаты."
    assert chat_page.is_chat_search_empty_state_visible(), (
        "При поиске 'провер1' должен отображаться empty state 'Чатов не найдено / No chats found'."
    )

    payload_email = search_and_get_payload("test@test1")
    data = payload_email.get("data", [])
    expected_user_email = "test@test1.ru"
    assert any(
        any((user.get("name") or "").lower() == expected_user_email for user in (chat.get("users") or []))
        for chat in data
    ), f"В ответе /chats/search не найден пользователь {expected_user_email}."

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("46")
def test_46_send_image_attachments_p2p(two_users):
    page_a = two_users["a"]
    page_a1 = two_users["a1"]

    LoginFlow(page_a).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    LoginFlow(page_a1).login(config.TEST_USER2_EMAIL, config.TEST_USER2_PASSWORD, expect_success=True)

    chat_a = ChatPage(page_a)
    chat_a1 = ChatPage(page_a1)

    chat_a.open()
    chat_a.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)
    chat_a1.open()
    chat_a1.open_existing_p2p_chat_via_search(config.ADMIN_EMAIL)

    file_paths = [
        "tests/resources/chat_attachments/sample.jpg",
        "tests/resources/chat_attachments/sample.png",
        "tests/resources/chat_attachments/sample.jpeg",
    ]

    for file_path in file_paths:
        file_name = file_path.split("/")[-1]
        chat_a.close_attachment_preview_if_open()
        own_count_before = chat_a.get_message_bubble_count()
        peer_count_before = chat_a1.get_message_bubble_count()

        with page_a.expect_response("**/send-message") as response_info:
            chat_a.attach_file_via_dialog(file_path)
            assert chat_a.get_message_input_value() == "", "Строка ввода должна оставаться пустой"
            chat_a.click_send()

        response = response_info.value
        assert response.ok, f"Запрос send-message завершился неуспешно для {file_name}"

        assert chat_a.wait_for_message_bubble_count_at_least(own_count_before + 1), (
            f"В истории чата у A не появилось новое сообщение после отправки файла: {file_name}"
        )
        assert chat_a.is_last_own_message_without_text(), (
            "В отправленном бабле с файлом не должно быть текста"
        )

        assert chat_a1.wait_for_message_bubble_count_at_least(peer_count_before + 1, timeout_ms=20000), (
            f"Пользователь A1 не получил новое сообщение с файлом: {file_name}"
        )

        chat_a1.open_attachment_in_last_message(file_name=file_name, source="peer")
        assert chat_a1.has_visible_image_preview(), (
            f"Пользователь A1 не увидел превью изображения: {file_name}"
        )
        assert chat_a1.close_attachment_preview_if_open(), (
            f"Пользователь A1 не смог закрыть просмотр вложения: {file_name}"
        )
        assert not chat_a1.is_attachment_preview_open(), (
            f"У пользователя A1 просмотр вложения остался открыт: {file_name}"
        )

        chat_a.open_attachment_in_last_message(file_name=file_name)
        assert chat_a.has_visible_image_preview(), (
            f"Не удалось увидеть превью изображения после открытия файла: {file_name}"
        )
        assert chat_a.close_attachment_preview_if_open(), (
            f"Пользователь A не смог закрыть просмотр вложения: {file_name}"
        )

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("47")
def test_47_typing_status_p2p_and_group_two_users(two_users):
    page_a = two_users["a"]
    page_a1 = two_users["a1"]

    LoginFlow(page_a).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    LoginFlow(page_a1).login(config.TEST_USER2_EMAIL, config.TEST_USER2_PASSWORD, expect_success=True)

    chat_a = ChatPage(page_a)
    chat_a1 = ChatPage(page_a1)

    third_user_candidates = [
        getattr(config, "TEST_LDAP_USER_EMAIL", None),
        getattr(config, "TEST_ADFS_USER_EMAIL", None),
        getattr(config, "USER_EMAIL", None),
    ]
    third_user_email = next(
        (
            user for user in third_user_candidates
            if user and user not in {config.ADMIN_EMAIL, config.TEST_USER2_EMAIL}
        ),
        None,
    )

    assert third_user_email, (
        "Нужен третий тестовый пользователь для конвертации p2p -> group. "
        "Заполни TEST_LDAP_USER_EMAIL, TEST_ADFS_USER_EMAIL или USER_EMAIL."
    )

    def typing_request_matcher(response) -> bool:
        return "/api/rest/chats/" in response.url and "/typing" in response.url

    def assert_typing_request_from_sender(sender_page, receiver_page, sender_action):
        receiver_typing_requests: list[str] = []

        def on_receiver_response(response):
            if typing_request_matcher(response):
                receiver_typing_requests.append(response.url)

        receiver_page.on("response", on_receiver_response)
        try:
            with sender_page.expect_response(typing_request_matcher, timeout=15000) as typing_response_info:
                sender_action()

            assert typing_response_info.value.ok, (
                f"Typing-запрос отправителя завершился неуспешно: {typing_response_info.value.status}"
            )

            receiver_page.wait_for_timeout(500)
        finally:
            receiver_page.remove_listener("response", on_receiver_response)

        if receiver_typing_requests:
            print(f"[DEBUG] Receiver typing requests detected: {receiver_typing_requests}")

    def get_receiver_typing_status(chat_page: ChatPage, timeout_ms: int = 8000) -> str:
        try:
            status = chat_page.wait_for_typing_status_visible(timeout_ms=timeout_ms)
            if status.strip():
                return status
        except Exception:
            pass

        if hasattr(chat_page, "wait_for_any_chat_list_typing_status"):
            try:
                status = chat_page.wait_for_any_chat_list_typing_status(timeout_ms=timeout_ms)  # type: ignore[attr-defined]
                if status.strip():
                    return status
            except AssertionError:
                pass

        for candidate in (config.ADMIN_EMAIL, config.TEST_USER2_EMAIL, third_user_email):
            if not candidate:
                continue
            try:
                status = chat_page.wait_for_chat_list_typing_status(candidate, timeout_ms=2500)
                if status.strip():
                    return status
            except AssertionError:
                continue

        raise AssertionError("Не найден typing-статус у получателя ни в header, ни в списке чатов.")

    def trigger_typing_until_status(
        sender_page,
        receiver_page,
        sender_chat: ChatPage,
        receiver_chat: ChatPage,
        message_prefix: str,
        max_wait_ms: int = 25000,
    ) -> str:
        deadline = time.time() + max_wait_ms / 1000
        attempt = 0

        while time.time() < deadline:
            attempt += 1

            assert_typing_request_from_sender(
                sender_page=sender_page,
                receiver_page=receiver_page,
                sender_action=lambda: sender_chat.type_message_with_keyboard(
                    generate_unique_message(f"{message_prefix}-{attempt}"),
                    delay_ms=120,
                ),
            )

            try:
                status = get_receiver_typing_status(receiver_chat, timeout_ms=2000).lower()
                if ("печатает" in status) or ("typing" in status):
                    return status
            except AssertionError:
                pass

            receiver_page.wait_for_timeout(350)

        raise AssertionError(f"Не удалось поймать typing-статус у получателя за {max_wait_ms} мс.")

    def wait_group_creation_modal_closed(page, timeout_ms: int = 15000):
        modal_candidates = (
            "app-chat-members-adding",
            "app-add-members-modal",
            "app-chat-creation",
        )
        deadline = time.time() + timeout_ms / 1000

        while time.time() < deadline:
            any_visible = False

            for selector in modal_candidates:
                locator = page.locator(selector).first
                try:
                    if locator.count() > 0 and locator.is_visible():
                        any_visible = True
                        break
                except Exception:
                    continue

            if not any_visible:
                return

            page.wait_for_timeout(300)

        raise AssertionError("Модалка создания группового чата не закрылась.")

    def rename_group_chat_with_retry(chat_page: ChatPage, new_name: str, timeout_ms: int = 15000):
        deadline = time.time() + timeout_ms / 1000
        last_error = None

        while time.time() < deadline:
            try:
                chat_page.rename_opened_chat(new_name)
                chat_page.close_chat_secondary_panel_if_open(timeout_ms=5000)
                return
            except Exception as exc:
                last_error = exc
                chat_page.page.wait_for_timeout(500)

        raise AssertionError(f"Не удалось переименовать групповой чат: {last_error}")

    def open_chat_by_name_with_retry(chat_page: ChatPage, chat_name: str, timeout_ms: int = 20000):
        deadline = time.time() + timeout_ms / 1000
        last_error = None

        while time.time() < deadline:
            try:
                chat_page.set_chat_search_text(chat_name)
                chat_page.open_existing_p2p_chat_via_search(chat_name)
                chat_page.set_chat_search_text("")
                return
            except Exception as exc:
                last_error = exc
                try:
                    chat_page.set_chat_search_text("")
                except Exception:
                    pass
                chat_page.page.wait_for_timeout(500)

        raise AssertionError(f"Не удалось открыть чат '{chat_name}': {last_error}")

    chat_a.open()
    chat_a1.open()

    chat_a.open_existing_p2p_chat_via_search(config.TEST_USER2_EMAIL)
    chat_a1.open_existing_p2p_chat_via_search(config.ADMIN_EMAIL)

    chat_a.set_chat_search_text("")
    chat_a1.set_chat_search_text("")

    p2p_status = trigger_typing_until_status(
        sender_page=page_a,
        receiver_page=page_a1,
        sender_chat=chat_a,
        receiver_chat=chat_a1,
        message_prefix="autotest-47-p2p-typing",
        max_wait_ms=25000,
    )

    assert ("печатает" in p2p_status) or ("typing" in p2p_status), (
        f"В p2p не найден typing-статус. Получено: {p2p_status}"
    )

    chat_a.create_group_chat_from_opened_p2p()
    chat_a.search_user_for_new_chat(third_user_email)
    chat_a.select_user_checkbox_from_new_chat_results(third_user_email)
    chat_a.click_create_chat_submit()

    wait_group_creation_modal_closed(page_a, timeout_ms=15000)

    group_name = generate_unique_message("autotest-47-group")
    page_a.wait_for_timeout(1000)
    rename_group_chat_with_retry(chat_a, group_name, timeout_ms=15000)

    page_a.wait_for_timeout(1000)
    page_a1.wait_for_timeout(1500)

    open_chat_by_name_with_retry(chat_a1, group_name, timeout_ms=20000)

    group_status = trigger_typing_until_status(
        sender_page=page_a,
        receiver_page=page_a1,
        sender_chat=chat_a,
        receiver_chat=chat_a1,
        message_prefix="autotest-47-group-typing",
        max_wait_ms=25000,
    )

    assert ("печатает" in group_status) or ("typing" in group_status), (
        f"В group chat не найден typing-статус. Получено: {group_status}"
    )