# tests/test_login.py
import pytest
from config import config  # ← ИМПОРТ КОНФИГА НАПРЯМУЮ


def test_successful_login(login_page):
    """Успешный логин с данными из конфига"""
    error_code = login_page.login_with_network_check(
        username=config.ADMIN_EMAIL,      # ← напрямую из config
        password=config.ADMIN_PASSWORD,    # ← напрямую из config
        expect_success=True
    )
    assert error_code == 0, f"При успешном логине ошибка {error_code}"
    assert "login" not in login_page.driver.current_url
    print(f"✅ Успешный логин, код: {error_code}")


def test_invalid_password(login_page):
    """Неверный пароль - проверяем ошибку 400"""
    print("🧪 Тест: вход с неверным паролем (ожидаем 400)")

    # Выполняем вход с неверным паролем
    login_page.open()
    login_page.enter_username(config.ADMIN_EMAIL)
    login_page.enter_password("wrong_password_123")
    login_page.click_login_button()

    # Проверяем наличие ошибки 400
    has_400_error = login_page.check_400_error()

    # Основная проверка: должна быть ошибка 400
    assert has_400_error, "Не обнаружена ошибка 400 при неверном пароле"

    print("✅ Тест пройден: ошибка 400 корректно возвращается сервером")