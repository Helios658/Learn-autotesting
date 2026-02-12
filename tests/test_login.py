# tests/test_login.py
import time

import pytest
from config import config

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("30381")
def test_30381_registered_user_can_login(login_page):
    """
    #30381: Вход в систему зарегистрированного пользователя (smoketest).

    Важно: после клика "Войти" может быть небольшая задержка редиректа,
    поэтому используем явное ожидание успешного перехода.
    """
    username = config.ADMIN_EMAIL
    password = config.ADMIN_PASSWORD

    login_page.open()
    login_page.enter_username(username)
    login_page.enter_password(password)

    # ER 1.1: данные отображаются в полях
    assert login_page.get_entered_username() == username
    assert login_page.get_entered_password() == password

    # ER 1.1: кнопка "Войти" активна
    assert login_page.is_login_button_enabled(), "Кнопка 'Войти' должна быть активна"

    login_page.click_login_button()

    # ER 1.1: открывается страница чатов (ожидаем уход со страницы логина)
    logged_in = login_page.wait_for_successful_login()
    if not logged_in:
        error_code = login_page.get_network_error()
        pytest.fail(
            f"Не удалось войти: URL остался {login_page.driver.current_url}, "
            f"network_error={error_code}. Проверьте тестовые данные/окружение."
        )


def test_invalid_password(login_page):
    """Неверный пароль - проверяем ошибку 400"""
    print("🧪 Тест: вход с неверным паролем (ожидаем 400)")

    login_page.open()
    login_page.enter_username(config.ADMIN_EMAIL)
    login_page.enter_password("wrong_password_123")
    login_page.click_login_button()

    has_400_error = login_page.check_400_error()

    assert has_400_error, "Не обнаружена ошибка 400 при неверном пароле"

    print("✅ Тест пройден: ошибка 400 корректно возвращается сервером")

def test_ldap_login(login_page):
    #Логин LDAP user
    username_ldap = config.TEST_LDAP_USER_EMAIL
    password_ldap = config.TEST_LDAP_USER_PASSWORD

    login_page.open()
    login_page.enter_username(username_ldap)
    login_page.enter_password(password_ldap)

    assert login_page.get_entered_username() == username_ldap
    assert login_page.get_entered_password() == password_ldap

    assert login_page.is_login_button_enabled(), "Кнопка 'Войти' должна быть активна"

    login_page.click_login_button()

    logged_in = login_page.wait_for_successful_login()
    if not logged_in:
        error_code = login_page.get_network_error()
        pytest.fail(
            f"Не удалось войти: URL остался {login_page.driver.current_url}, "
            f"network_error={error_code}. Проверьте тестовые данные/окружение."
        )

def test_adfs_login(login_page):
    # Логин ADFS
    username_adfs = config.TEST_ADFS_USER_EMAIL
    password_adfs = config.TEST_ADFS_USER_PASSWORD

    login_page.open()
    login_page.click_show_all()
    login_page.adfs_link_open()
    login_page.enter_username_adfs(username_adfs)
    login_page.enter_password_adfs(password_adfs)

    assert login_page.get_entered_username_adfs() == username_adfs
    assert login_page.get_entered_password_adfs() == password_adfs

    login_page.click_login_button_adfs()
