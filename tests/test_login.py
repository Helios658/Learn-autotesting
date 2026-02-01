import pytest
from pages.login_page import LoginPage


def test_successful_login(login_page):
    """
    Тест успешного логина с использованием Page Object
    """
    # Используем фикстуру login_page
    success = login_page.login("admin@admin1.ru", "123456")

    assert success is True
    assert "login" not in login_page.driver.current_url
    print("✅ Успешный логин через Page Object")


def test_invalid_password(login_page):
    """
    Тест неверного пароля
    """
    login_page.login("admin@admin1.ru", "wrong_password")

    # Проверяем что остались на странице логина
    assert login_page.is_on_login_page()

    # Проверяем сообщение об ошибке
    error_message = login_page.get_error_message()
    assert error_message is not None
    print(f"✅ Обнаружена ошибка: {error_message}")


def test_login_chain_methods(login_page):
    """
    Тест с цепочкой вызовов (method chaining)
    """
    # Можно вызывать методы цепочкой
    login_page.open() \
        .enter_username("admin@admin1.ru") \
        .enter_password("123456") \
        .click_login_button()

    # Проверяем результат
    login_page.wait.until(lambda d: "login" not in d.current_url)
    print("✅ Логин через цепочку методов")