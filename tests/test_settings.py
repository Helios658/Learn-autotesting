import re
import pytest
from playwright.sync_api import Error as PlaywrightError, expect
from config import config
from services.login_flow import LoginFlow

SETTINGS_MENU = "[e2e-id='shared-core.navigation-menu.settings']"
GENERAL_TAB = "[e2e-id='settings-page.list.general']"
STORAGE_MANAGEMENT_TAB = "[e2e-id='settings-page.list.storage_management']"


def _first_visible(page, selectors: list[str] | str, timeout_ms: int = 10_000):
    selectors = [selectors] if isinstance(selectors, str) else selectors
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            locator.wait_for(state="visible", timeout=timeout_ms)
            return locator
        except PlaywrightError:
            continue
    raise AssertionError(f"Не нашли видимый элемент: {selectors}")


def _open_general_settings(page):
    _first_visible(page, SETTINGS_MENU, timeout_ms=12_000).click()
    _first_visible(page, GENERAL_TAB, timeout_ms=12_000).click()

def _open_storage_management(page):
    _first_visible(page, SETTINGS_MENU, timeout_ms=12_000).click()
    _first_visible(page, STORAGE_MANAGEMENT_TAB, timeout_ms=12_000).click()


def _select_language(page, labels: list[str]):
    for label in labels:
        candidate_selectors = [
            f"xpath=//label[contains(@class,'radio-button')][.//span[contains(normalize-space(), '{label}')]]",
            f"xpath=//*[contains(@class,'radio-button')][.//span[contains(normalize-space(), '{label}')]]",
            f"text={label}",
        ]
        for selector in candidate_selectors:
            try:
                option = _first_visible(page, selector, timeout_ms=3_000)
                option.click()
                page.wait_for_timeout(700)
                return
            except (AssertionError, PlaywrightError):
                continue

    raise AssertionError(f"Не удалось выбрать язык. Проверяли подписи: {labels}")


@pytest.mark.buildtest
@pytest.mark.testcase("53")
def test_53_settings_general_language_switch_ru_en_ru(driver):
    assert config.ADMIN_EMAIL and config.ADMIN_PASSWORD, "Не заданы ADMIN_EMAIL/ADMIN_PASSWORD"

    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    _open_general_settings(driver)

    # Переключаемся на English и проверяем, что интерфейс стал английским.
    _select_language(driver, ["English"])
    _first_visible(driver, ["text=Settings", "text=General", "text=Language, timezone"], timeout_ms=15_000)

    # Возвращаемся на русский и проверяем, что интерфейс снова русский.
    _select_language(driver, ["Русский", "Russian"])
    _first_visible(driver, ["text=Настройки", "text=Общее", "text=Язык, часовой пояс"], timeout_ms=15_000)


@pytest.mark.buildtest
@pytest.mark.testcase("54")
def test_54_storage_file_left_click_selects_file_and_checkbox(driver):
    assert config.ADMIN_EMAIL and config.ADMIN_PASSWORD, "Не заданы ADMIN_EMAIL/ADMIN_PASSWORD"

    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)
    _open_storage_management(driver)

    storage_tab = _first_visible(driver, STORAGE_MANAGEMENT_TAB, timeout_ms=10_000)
    tab_class = (storage_tab.get_attribute("class") or "").lower()

    assert "selected" in tab_class or "active" in tab_class, (
        "Раздел 'Управление диском' должен быть активным"
    )

    driver.wait_for_timeout(1200)

    def _selected_count() -> int | None:
        """
        Возвращает количество выбранных файлов из панели 'Выбрано: N'.
        Если панели нет — возвращает None.
        """
        selected_locators = [
            driver.locator("xpath=//*[contains(normalize-space(), 'Выбрано:')]"),
            driver.locator("xpath=//*[contains(normalize-space(), 'Selected:')]"),
        ]

        for locator in selected_locators:
            try:
                count = locator.count()

                for idx in range(min(count, 5)):
                    item = locator.nth(idx)

                    if not item.is_visible():
                        continue

                    text = (item.inner_text() or "").strip()

                    match = re.search(
                        r"(выбрано|selected)\s*:\s*(\d+)",
                        text,
                        flags=re.IGNORECASE,
                    )

                    if match:
                        return int(match.group(2))

            except PlaywrightError:
                continue

        return None

    def _find_file_row(max_scan: int = 50, name_contains: str | None = None):
        """
        Находит первую видимую строку файла в таблице.
        Не привязываемся к конкретному имени файла, размеру или дате.
        """
        row_locators = [
            driver.locator("tbody tr"),
            driver.locator("virtual-scroller tbody tr"),
            driver.locator(".storage-management__file-list tr"),
            driver.locator("tr.ng-star-inserted"),
        ]

        for rows in row_locators:
            try:
                rows_count = rows.count()
            except PlaywrightError:
                continue

            if rows_count == 0:
                continue

            scan_count = min(rows_count, max_scan)

            for idx in range(scan_count):
                row = rows.nth(idx)

                try:
                    if not row.is_visible():
                        continue
                except PlaywrightError:
                    continue

                name_locators = [
                    row.locator("div[ivafilenameshortener] .content").first,
                    row.locator(".file-name .content").first,
                    row.locator(".file-info .content").first,
                    row.locator("td").nth(1),
                    row.locator(".content").first,
                ]

                for name_locator in name_locators:
                    try:
                        name_text = (name_locator.inner_text() or "").strip()
                    except PlaywrightError:
                        continue

                    if not name_text:
                        continue

                    if name_text.lower() in {"имя", "name"}:
                        continue

                    if name_contains and name_contains.lower() not in name_text.lower():
                        continue

                    return row, name_locator, name_text

        raise AssertionError("Не удалось найти строку файла с непустым именем")

    def _clear_selection():
        """
        Сбрасывает массовое выделение после Ctrl+A.

        В этой сборке кнопка сброса определяется Playwright как:
        get_by_role("button", name="Выбрано:")
        Поэтому сначала кликаем именно по кнопке с текстом 'Выбрано:' / 'Selected:'.
        """

        def _is_cleared() -> bool:
            count = _selected_count()
            return count in (None, 0)

        def _click_left_side(locator) -> bool:
            """
            Кликает в левую часть кнопки.
            Это важно, потому что крестик находится слева от текста 'Выбрано: 50'.
            """
            try:
                if locator.count() == 0:
                    return False

                target = locator.first

                if not target.is_visible():
                    return False

                box = target.bounding_box()

                if box:
                    target.click(
                        position={
                            "x": 8,
                            "y": box["height"] / 2,
                        },
                        timeout=5_000,
                        force=True,
                    )
                else:
                    target.click(timeout=5_000, force=True)

                return True

            except PlaywrightError:
                return False

        for _ in range(6):
            if _is_cleared():
                return

            clear_locators = [
                # Самый важный вариант — именно так кнопку увидел Playwright codegen.
                driver.get_by_role(
                    "button",
                    name=re.compile(r"(Выбрано|Selected)\s*:?", re.IGNORECASE),
                ),

                # Если role/name не сработает — ищем button по тексту.
                driver.locator(
                    "xpath=//button[contains(normalize-space(.), 'Выбрано:') "
                    "or contains(normalize-space(.), 'Selected:')]"
                ),

                # Если текст лежит внутри вложенного элемента, поднимаемся к button.
                driver.locator(
                    "xpath=//*[contains(normalize-space(.), 'Выбрано:') "
                    "or contains(normalize-space(.), 'Selected:')]/ancestor::button[1]"
                ),

                # Старые варианты оставляем как fallback.
                driver.locator("button:has(svg-icon[src*='icon16/close.svg'])"),
                driver.locator("button:has(svg-icon[src*='close.svg'])"),
            ]

            clicked = False

            for locator in clear_locators:
                if _click_left_side(locator):
                    clicked = True
                    break

            if not clicked:
                # Координатный fallback: ищем текст 'Выбрано:' и кликаем рядом слева.
                try:
                    label = driver.locator(
                        "xpath=//*[contains(normalize-space(.), 'Выбрано:') "
                        "or contains(normalize-space(.), 'Selected:')]"
                    ).first

                    if label.count() > 0 and label.is_visible():
                        box = label.bounding_box()

                        if box:
                            driver.mouse.click(
                                max(box["x"] - 10, 0),
                                box["y"] + box["height"] / 2,
                            )
                            clicked = True

                except PlaywrightError:
                    pass

            driver.wait_for_timeout(700)

            if _is_cleared():
                return

        # Последние fallback-варианты.
        for key in ["Escape", "Control+A", "ControlOrMeta+A"]:
            try:
                driver.keyboard.press(key)
                driver.wait_for_timeout(700)

                if _is_cleared():
                    return

            except PlaywrightError:
                continue

        buttons_debug = driver.locator("button").evaluate_all(
            """buttons => buttons.map((b, i) => ({
                index: i,
                text: b.innerText,
                aria: b.getAttribute('aria-label'),
                title: b.getAttribute('title'),
                className: b.className
            }))"""
        )

        print("DEBUG BUTTONS:", buttons_debug)

        raise AssertionError(
            f"Не удалось сбросить выделение файлов. Текущее значение: {_selected_count()}"
        )

    def _click_row_download(row):
        """
        Нажимает кнопку скачивания в строке файла.
        """
        try:
            row.scroll_into_view_if_needed(timeout=3_000)
        except PlaywrightError:
            pass

        try:
            row.hover(timeout=3_000)
        except PlaywrightError:
            pass

        driver.wait_for_timeout(300)

        download_selectors = [
            "button:has(svg-icon[src*='download.svg'])",
            "button[title*='Скачать']",
            "button[aria-label*='Скачать']",
            "button:has-text('Скачать')",
        ]

        for selector in download_selectors:
            try:
                btn = row.locator(selector).first

                if btn.count() > 0 and btn.is_visible():
                    btn.click(timeout=5_000)
                    return

            except PlaywrightError:
                continue

        # fallback как в codegen: первая кнопка в строке
        buttons = row.get_by_role("button")
        assert buttons.count() > 0, "В строке файла не найдена кнопка скачивания"
        buttons.first.click(timeout=5_000)

    def _click_row_delete(row):
        """
        Нажимает кнопку удаления в строке файла.
        """
        try:
            row.scroll_into_view_if_needed(timeout=3_000)
        except PlaywrightError:
            pass

        try:
            row.hover(timeout=3_000)
        except PlaywrightError:
            pass

        driver.wait_for_timeout(300)

        delete_selectors = [
            "button:has(svg-icon[src*='delete.svg'])",
            "button:has(svg-icon[src*='trash.svg'])",
            "button[title*='Удалить']",
            "button[aria-label*='Удалить']",
            "button:has-text('Удалить')",
        ]

        for selector in delete_selectors:
            try:
                btn = row.locator(selector).first

                if btn.count() > 0 and btn.is_visible():
                    btn.click(timeout=5_000)
                    return

            except PlaywrightError:
                continue

        # fallback как в codegen: вторая кнопка в строке
        buttons = row.get_by_role("button")
        assert buttons.count() >= 2, "В строке файла не найдена кнопка удаления"
        buttons.nth(1).click(timeout=5_000)

    def _confirm_delete():
        modal = _first_visible(
            driver,
            [
                "div[role='dialog']",
                ".iva-core-modal-window",
                ".cdk-overlay-pane",
            ],
            timeout_ms=10_000,
        )

        _first_visible(
            modal,
            [
                "button:has-text('Удалить')",
                "button:has-text('Delete')",
            ],
            timeout_ms=8_000,
        ).click()

        expect(modal).to_be_hidden(timeout=15_000)

    def _cancel_delete():
        modal = _first_visible(
            driver,
            [
                "div[role='dialog']",
                ".iva-core-modal-window",
                ".cdk-overlay-pane",
            ],
            timeout_ms=10_000,
        )

        _first_visible(
            modal,
            [
                "button:has-text('Отмена')",
                "button:has-text('Cancel')",
            ],
            timeout_ms=8_000,
        ).click()

        expect(modal).to_be_hidden(timeout=15_000)

    def _open_file_preview(row):
        """
        Открывает файл кликом по имени файла, а не по кнопкам строки.
        """
        try:
            row.scroll_into_view_if_needed(timeout=3_000)
        except PlaywrightError:
            pass

        name_locators = [
            row.locator("div[ivafilenameshortener] .content").first,
            row.locator(".file-name .content").first,
            row.locator(".file-info .content").first,
            row.locator("td").nth(1),
            row.locator(".content").first,
        ]

        for name_locator in name_locators:
            try:
                if name_locator.count() > 0 and name_locator.is_visible():
                    name_locator.click(timeout=6_000)
                    return
            except PlaywrightError:
                continue

        box = row.bounding_box()
        assert box, "Не удалось получить координаты строки файла для открытия предпросмотра"

        driver.mouse.click(
            box["x"] + 140,
            box["y"] + box["height"] / 2,
        )

    def _close_file_preview():
        viewer_modal = _first_visible(
            driver,
            [
                "mcu-document-viewer",
                "div[role='dialog']",
                ".iva-core-modal-window",
            ],
            timeout_ms=15_000,
        )

        close_btn = _first_visible(
            viewer_modal,
            [
                "button:has(svg-icon[src*='icon24/close.svg'])",
                "button[iva-icon-button]:has(svg-icon[src*='close.svg'])",
                "button:has(svg-icon[src*='close.svg'])",
            ],
            timeout_ms=10_000,
        )

        close_btn.click(timeout=5_000)
        expect(viewer_modal).to_be_hidden(timeout=10_000)

    # 1. Массовое выделение файлов через Ctrl+A.
    driver.locator("body").press("ControlOrMeta+A")

    selected_counter = _first_visible(
        driver,
        [
            "xpath=//*[contains(normalize-space(), 'Выбрано:')]",
            "xpath=//*[contains(normalize-space(), 'Selected:')]",
        ],
        timeout_ms=10_000,
    )

    assert selected_counter.is_visible(), (
        "После Ctrl+A не появился индикатор массового выделения файлов"
    )

    selected_count = _selected_count()

    assert selected_count is not None and selected_count > 0, (
        f"После Ctrl+A ожидалось количество выбранных файлов > 0, получено: {selected_count}"
    )

    # 2. Снимаем массовое выделение.
    _clear_selection()

    assert _selected_count() in (None, 0), (
        f"После сброса выделения всё ещё есть выбранные файлы: {_selected_count()}"
    )

    # 3. Скачиваем файл из строки.
    file_row, _, file_name = _find_file_row()

    with driver.expect_download(timeout=20_000) as download_info:
        _click_row_download(file_row)

    download = download_info.value

    assert download.suggested_filename, (
        f"Файл '{file_name}' скачался, но имя скачанного файла пустое"
    )

    # 4. Проверяем удаление через кнопку в строке, сначала отмена.
    file_row, _, file_name = _find_file_row()

    _click_row_delete(file_row)
    _cancel_delete()

    # 5. Повторно удаляем файл и подтверждаем удаление.
    file_row, _, file_name = _find_file_row()

    _click_row_delete(file_row)
    _confirm_delete()

    driver.wait_for_timeout(1000)

    # 6. Открываем другой файл в просмотрщике кликом по имени.
    file_row, _, file_name = _find_file_row()

    _open_file_preview(file_row)

    viewer_modal = _first_visible(
        driver,
        [
            "mcu-document-viewer",
            "div[role='dialog']",
            ".iva-core-modal-window",
        ],
        timeout_ms=15_000,
    )

    assert viewer_modal.is_visible(), (
        f"После клика по файлу '{file_name}' не открылся просмотрщик"
    )

    # 7. Закрываем просмотрщик.
    _close_file_preview()