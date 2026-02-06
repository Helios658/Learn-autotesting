import pytest
import time
import random
import string
from selenium.webdriver.common.by import By
from pages.login_page import LoginPage
from pages.password_recovery_page import PasswordRecoveryPage
from pages.mail_page import MailPage
from pages.new_password_page import NewPasswordPage


def generate_random_password():
    """Генерирует случайный пароль"""
    prefix = "NewPassword"
    random_digits = ''.join(random.choices(string.digits, k=3))
    special_chars = "!@#$%^&*"
    random_special = random.choice(special_chars)
    password = f"{prefix}{random_digits}{random_special}"
    print(f"📋 Сгенерирован пароль: {password}")
    return password


def test_password_recovery(driver):
    """Полный тест восстановления пароля"""

    # 1. Запрос восстановления
    login_page = LoginPage(driver)
    login_page.open()

    # Переходим на страницу восстановления
    driver.find_element(
        By.CSS_SELECTOR,
        "[e2e-id='login-page.login-form.recovery-password-link']"
    ).click()

    # Используем PasswordRecoveryPage
    recovery_page = PasswordRecoveryPage(driver)
    recovery_page.request_password_recovery('v.kornienko@iva.ru')

    time.sleep(10)  # Ждем отправки письма

    # 2. Работа с почтой
    mail_page = MailPage(driver)
    mail_page.login('v.kornienko@iva-tech.ru', 'Helios998!')
    reset_link = mail_page.get_password_reset_link(wait_for_email=True)

    # 3. Смена пароля
    driver.get(reset_link)
    new_password = generate_random_password()

    new_password_page = NewPasswordPage(driver)
    new_password_page.set_new_password(new_password)
    new_password_page.go_to_login()

    # 4. Логин с новым паролем
    login_page.enter_username('v.kornienko@iva.ru')
    login_page.enter_password(new_password)
    login_page.click_login_button()

    time.sleep(3)

    assert "login" not in driver.current_url.lower()
    print(f"🎉 УСПЕХ! Вошли с новым паролем: {new_password}")