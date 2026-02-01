import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # ← ДОБАВЬТЕ ЭТО!


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def test_login_ivcs(driver):
    """
    Простой и стабильный тест логина с явными ожиданиями
    """
    USERNAME = "admin@admin1.ru"
    PASSWORD = "123456"  # Верный пароль
    wait = WebDriverWait(driver, 3)

    print("🎬 Начинаю тест...")

    # 1. Открываем страницу
    driver.get('https://gamma.hi-tech.org/v2/login')

    # 2. Ждем загрузки страницы (явное ожидание)
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')

    # 3. Ждем и заполняем логин
    login_input = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='login-page.login-form.login-input']"))
    )
    login_input.send_keys(USERNAME)

    # 4. Ждем и заполняем пароль
    password_input = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='login-page.login-form.password-input']"))
    )
    password_input.send_keys(PASSWORD)

    # 5. Ждем и нажимаем кнопку
    login_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[e2e-id='login-form__login-button']"))
    )
    login_button.click()

    # 6. ПРОСТАЯ ПРОВЕРКА: ждем изменения URL (макс 10 сек)
    try:
        # Сохраняем текущий URL для сравнения
        url_before_click = driver.current_url

        # Ждем пока URL изменится
        wait.until(EC.url_changes(url_before_click))

        # Проверяем что ушли со страницы login
        current_url = driver.current_url
        if "login" not in current_url:
            print("✅ ТЕСТ ПРОЙДЕН: успешный логин, ушли со страницы login")
            print(f"   Текущий URL: {current_url}")
        else:
            print(f"❌ ТЕСТ НЕ ПРОЙДЕН: остались на странице login")
            print(f"   Текущий URL: {current_url}")
            assert False, "Остались на странице login после ввода верных данных"

    except TimeoutException:  # ← Теперь это будет работать
        # URL не изменился за 10 секунд - логин не удался
        print("❌ ТЕСТ НЕ ПРОЙДЕН: URL не изменился, логин не удался")
        print(f"   Остались на URL: {driver.current_url}")
        assert False, "Не удалось выйти со страницы login (таймаут)"