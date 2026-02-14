import time
import pytest
from config import config
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CONFERENCES_TAB = (By.CSS_SELECTOR, "[e2e-id='shared-core.navigation-menu.conferences']")
ADD_BUTTON = (By.CSS_SELECTOR, "[e2e-id='ADD']")
SETTINGS_MODAL_BUTTON = (By.XPATH, "//span[text()=' Войти ']/parent::button")
CLOSE_MODAL_BUTTON = (By.CSS_SELECTOR, "button.close-button.iva-icon-button")
HAMBURGER_BUTTON = (By.CSS_SELECTOR, "button.hamburger.iva-icon-button")
EVENTS_TAB = (By.CSS_SELECTOR, "[e2e-id='shared-core.navigation-menu.conferences']")


def _click_when_ready(wait: WebDriverWait, locator: tuple[str, str]):
    element = wait.until(EC.element_to_be_clickable(locator))
    element.click()


def _select_conference_template(wait: WebDriverWait, template_name: str):
    template_locator = (
        By.XPATH,
        "//div[contains(@class, 'conference-card')]"
        f"[.//h4[contains(@class, 'conference-name') and normalize-space()='{template_name}']]",
    )
    _click_when_ready(wait, template_locator)

@pytest.mark.buildtest
@pytest.mark.testcase("30887")
def test_30887_events_one_time_login_only(login_page, driver):
    """#30887: логин + создание конференции через конкретный шаблон."""
    wait = WebDriverWait(driver, config.EXPLICIT_WAIT)

    error_code = login_page.login_with_network_check(
        username=config.ADMIN_EMAIL,
        password=config.ADMIN_PASSWORD,
        expect_success=True,
    )

    assert error_code == 0, f"Ошибка сети при логине: {error_code}"
    assert login_page.wait_for_successful_login(), (
        f"Логин неуспешен, текущий URL: {login_page.driver.current_url}"
    )

    # 1. Переход на вкладку Конференции и создание по шаблону
    _click_when_ready(wait, CONFERENCES_TAB)
    _click_when_ready(wait, ADD_BUTTON)
    _select_conference_template(wait, "Деление участников на группы")

    # 2. Нажимаем на кнопку "Войти" в модальном окне
    _click_when_ready(wait, SETTINGS_MODAL_BUTTON)
    print("✅ Нажали кнопку 'Войти' в модальном окне")
    # 3. Закрываем модальное окно
    _click_when_ready(wait, CLOSE_MODAL_BUTTON)
    print("✅ Закрыли модальное окно")

    # 4. Двигаем мышку, чтобы появился гамбургер
    conference_header = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".conference-header, .conference-title, h1"))
    )

    action_chains = ActionChains(driver)
    action_chains.move_to_element(conference_header).perform()
    print("✅ Навели мышь на заголовок конференции")

    # 5. Нажимаем на гамбургер
    _click_when_ready(wait, HAMBURGER_BUTTON)
    print("✅ Нажали на кнопку-гамбургер")

    # 6. Возвращаемся на страницу списка мероприятий
    events_tab = wait.until(
        EC.presence_of_element_located(EVENTS_TAB)
    )
    driver.execute_script("arguments[0].click();", events_tab)
    print("✅ Вернулись на страницу списка мероприятий")
    time.sleep(3)
