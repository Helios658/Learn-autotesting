import pytest
from playwright.sync_api import Error as PlaywrightError
from config import config
from services.login_flow import LoginFlow
from services.logout_flow import LogoutFlow

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("55")
def test_55_profile_displays_user_name_and_email(driver):
    assert config.ADMIN_EMAIL and config.ADMIN_PASSWORD, (
        "Не заданы ADMIN_EMAIL/ADMIN_PASSWORD"
    )

    LoginFlow(driver).login(
        config.ADMIN_EMAIL,
        config.ADMIN_PASSWORD,
        expect_success=True,
    )

    LogoutFlow(driver).navigator.open_profile_settings()

    expected_user = config.ADMIN_EMAIL

    profile_title = driver.get_by_text("Профиль", exact=True).first
    profile_title.wait_for(
        state="visible",
        timeout=config.EXPLICIT_WAIT * 1000,
    )

    driver.wait_for_timeout(1000)

    def _get_visible_text_occurrences(text: str) -> int:
        count = 0

        locators = [
            driver.get_by_text(text),
            driver.locator(f"xpath=//*[contains(normalize-space(.), '{text}')]"),
        ]

        for locator in locators:
            try:
                items_count = locator.count()

                for idx in range(items_count):
                    item = locator.nth(idx)

                    try:
                        if item.is_visible():
                            item_text = (item.inner_text() or "").strip()

                            if text in item_text:
                                count += 1

                    except PlaywrightError:
                        continue

            except PlaywrightError:
                continue

        return count

    def _get_input_value_occurrences(text: str) -> int:
        try:
            values = driver.locator("input, textarea").evaluate_all(
                """elements => elements
                    .filter(el => {
                        const style = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();

                        return style.visibility !== 'hidden'
                            && style.display !== 'none'
                            && rect.width > 0
                            && rect.height > 0;
                    })
                    .map(el => el.value || '')
                """
            )
        except PlaywrightError:
            return 0

        return sum(1 for value in values if text in value)

    def _profile_contains_expected_user_at_least_twice() -> bool:
        text_count = _get_visible_text_occurrences(expected_user)
        input_count = _get_input_value_occurrences(expected_user)

        total_count = text_count + input_count

        print(
            f"DEBUG PROFILE USER VALUES: "
            f"text_count={text_count}, input_count={input_count}, total={total_count}"
        )

        return total_count >= 2

    is_loaded = False

    for _ in range(10):
        if _profile_contains_expected_user_at_least_twice():
            is_loaded = True
            break

        driver.wait_for_timeout(500)

    assert is_loaded, (
        f"В профиле ожидалось минимум 2 значения '{expected_user}': "
        f"1) имя пользователя, 2) электронный адрес. "
        f"Фактически найдено меньше 2."
    )