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
    Тест неверного пароля (#30974)
    """
    # Используем новый метод для негативного сценария
    result = login_page.login_with_invalid_credentials(
        username="admin@admin1.ru",
        password="wrong_password"
    )
    # Тест считается пройденным если:
    # 1. Есть сообщение об ошибке ("error:" в начале) ИЛИ
    # 2. Остались на странице логина ("stay_on_login")
    if result.startswith("error:") or result == "stay_on_login":
        print("✅ ТЕСТ ПРОЙДЕН: система правильно отклонила неверный пароль")
        assert True
    else:
        print(f"❌ ТЕСТ НЕ ПРОЙДЕН: неожиданный результат - {result}")
        print(f"   Текущий URL: {login_page.driver.current_url}")
        assert False, f"Неверный результат: {result}"