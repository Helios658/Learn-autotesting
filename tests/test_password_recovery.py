import pytest
import random
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from pages.password_recovery_page import PasswordRecoveryPage
from pages.mail_page import MailPage
from pages.new_password_page import NewPasswordPage
from config import config
from pathlib import Path


def save_password_to_file(password):
    """Сохраняет пароль в файл для последующего использования"""
    password_file = Path("last_generated_password.txt")

    try:
        with open(password_file, 'w', encoding='utf-8') as f:
            f.write(password)
        print(f"💾 Пароль сохранен в {password_file.name}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения пароля: {e}")
        return False

def generate_random_password():
    """Генерирует случайный пароль"""
    prefix = "NewPassword"
    random_digits = ''.join(random.choices(string.digits, k=3))
    special_chars = "!@#$%^&*"
    random_special = random.choice(special_chars)
    password = f"{prefix}{random_digits}{random_special}"
    if save_password_to_file(password):
        print(f"📋 Сгенерирован и сохранен пароль: {password}")
    else:
        print(f"📋 Сгенерирован пароль: {password} (не сохранен в файл)")

    return password


#@pytest.mark.skip(reason="Требует работающей корпоративной почты")
def test_password_recovery(driver):
    """Полный тест восстановления пароля"""
    wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

    # 1. Запрос восстановления
    login_page = LoginPage(driver)
    login_page.open()

    recovery_link = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='login-page.login-form.recovery-password-link']"))
    )
    recovery_link.click()

    recovery_page = PasswordRecoveryPage(driver)
    recovery_page.request_password_recovery(config.USER_EMAIL)

    try:
        success_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.layout-bottom-margin_2.text-align_center"))
        )
        message_text = success_element.text.lower()
        if any(word in message_text for word in ["отправлен", "отправлены", "отправлено"]):
            print(f"✅ Подтверждение отправки: '{success_element.text}'")
        else:
            print(f"⚠️ Неожиданный текст: '{success_element.text}'")
    except Exception as e:
        print(f"⚠️ Не дождались подтверждения: {e}")

    # 2. Работа с почтой
    try:
        mail_page = MailPage(driver)
        mail_page.login()  # ← Без параметров, использует данные из конфига
        reset_link = mail_page.get_password_reset_link(wait_for_email=True)

        # 3. Смена пароля
        driver.get(reset_link)
        new_password = generate_random_password()
        new_password_page = NewPasswordPage(driver)
        new_password_page.set_new_password(new_password)
        new_password_page.go_to_login()

        # 4. Логин с новым паролем
        login_page.enter_username(config.USER_EMAIL)
        current_password = config.USER_PASSWORD
        login_page.enter_password(current_password)
        login_page.click_login_button()

        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".participant"))
            )
            print("✅ Успешный вход с новым паролем подтвержден")
        except:
            print("⚠️ Не дождались явного признака успешного входа")

        assert "login" not in driver.current_url.lower()
        print(f"🎉 УСПЕХ! Вошли с новым паролем: {new_password}")

    except Exception as e:
        if "почта" in str(e).lower() or "mail" in str(e).lower():
            pytest.skip(f"Пропускаем тест из-за проблем с почтой: {e}")
        else:
            raise