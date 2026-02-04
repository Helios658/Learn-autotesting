import pytest

def test_successful_login(login_page):
    """Успешный логин"""
    error_code = login_page.login_with_network_check(
        expect_success=True  # ← данные берутся по умолчанию
    )
    # Проверяем что ошибок нет и мы ушли со страницы логина
    assert error_code == 0, f"При успешном логине ошибка {error_code}"
    assert "login" not in login_page.driver.current_url
    print(f"✅ Успешный логин, код: {error_code}")

def test_invalid_password(login_page):
    """Неверный пароль"""
    error_code = login_page.login_with_network_check(
        password="wrong_password",  # ← меняем только пароль
        expect_success=False
    )
    # Проверяем что есть ошибка 401 и остались на login
    assert error_code == 400, f"Ожидалась ошибка 400, а получили {error_code}"
    assert "login" in login_page.driver.current_url
    print(f"✅ Неверный пароль, HTTP ошибка: {error_code}")