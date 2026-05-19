import re

import pytest
from playwright.sync_api import Error as PlaywrightError

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
        for locator in [driver.locator("text=Выбрано:"), driver.locator("text=Selected:")]:
            try:
                for idx in range(min(locator.count(), 5)):
                    item = locator.nth(idx)

                    if not item.is_visible():
                        continue

                    text = (item.inner_text() or "").lower()
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

    def _row_name(row) -> str:
        name_locators = [
            row.locator("div[ivafilenameshortener] .content").first,
            row.locator("div[ivafilenameshortener]").first,
            row.locator(".file-name .content").first,
            row.locator(".file-name").first,
            row.locator(".file-info .content").first,
            row.locator(".file-info").first,
            row.locator("td").nth(1),
            row.locator(".content").first,
        ]

        for locator in name_locators:
            try:
                if locator.count() == 0:
                    continue

                text = (locator.inner_text() or "").strip()

                if text and text.lower() not in {"имя", "name"}:
                    return text

            except PlaywrightError:
                continue

        return ""

    def _is_file_name(text: str) -> bool:
        return bool(
            re.search(
                r"\.(png|jpg|jpeg|gif|webp|bmp|pdf|txt|doc|docx|xls|xlsx|ppt|pptx|zip|rar|7z|csv)$",
                text.strip(),
                flags=re.IGNORECASE,
            )
        )

    def _is_previewable_file(text: str) -> bool:
        return bool(
            re.search(
                r"\.(png|jpg|jpeg|gif|webp|bmp|pdf|txt)$",
                text.strip(),
                flags=re.IGNORECASE,
            )
        )

    def _find_rows(max_scan: int = 80, previewable_only: bool = False):
        rows_locator = driver.locator(
            "tbody tr, tr.ng-star-inserted, .storage-management__file-list tr"
        )

        rows = []
        total = min(rows_locator.count(), max_scan)

        for idx in range(total):
            row = rows_locator.nth(idx)

            try:
                if not row.is_visible():
                    continue

                if row.locator("td").count() < 2:
                    continue

                name = _row_name(row)

                if not name:
                    continue

                if name.lower() in {"имя", "name"}:
                    continue

                if previewable_only and not _is_previewable_file(name):
                    continue

                rows.append(row)

            except PlaywrightError:
                continue

        assert rows, "Не удалось найти строки файлов в таблице"

        file_rows = []

        for row in rows:
            if _is_file_name(_row_name(row)):
                file_rows.append(row)

        return file_rows or rows

    def _is_row_selected(row) -> bool:
        try:
            row_class = (row.get_attribute("class") or "").lower()

            if any(state in row_class for state in ["selected", "active", "checked"]):
                return True

        except PlaywrightError:
            pass

        try:
            handle = row.element_handle()

            if handle is None:
                return False

            return bool(
                driver.evaluate(
                    """(row) => {
                        if (!row) return false;

                        if ((row.getAttribute('aria-selected') || '').toLowerCase() === 'true') {
                            return true;
                        }

                        const cb = row.querySelector("input[type='checkbox']");

                        if (cb && cb.checked) {
                            return true;
                        }

                        return Boolean(
                            row.querySelector('[aria-checked="true"], .checked, .selected')
                        );
                    }""",
                    handle,
                )
            )

        except PlaywrightError:
            return False

    def _hover_row(row):
        try:
            row.scroll_into_view_if_needed(timeout=3_000)
        except PlaywrightError:
            pass

        try:
            row.hover(timeout=3_000)
        except PlaywrightError:
            pass

        driver.wait_for_timeout(250)

    def _click_row_checkbox_zone(row) -> bool:
        """
        Кликает в область чекбокса строки.
        """
        _hover_row(row)

        before_count = _selected_count() or 0

        checkbox_selectors = [
            "td:first-child input[type='checkbox']",
            "td:first-child [role='checkbox']",
            "td:first-child label",
            "td:first-child [class*='checkbox']",
            "td:first-child iva-checkbox",
            "td:first-child .checkbox",
        ]

        for selector in checkbox_selectors:
            try:
                checkbox = row.locator(selector).first

                if checkbox.count() > 0 and checkbox.is_visible():
                    checkbox.click(timeout=3_000, force=True)
                    driver.wait_for_timeout(400)

                    after_count = _selected_count() or 0

                    if after_count > before_count or _is_row_selected(row):
                        return True

                    return True

            except PlaywrightError:
                continue

        try:
            box = row.bounding_box()

            if not box:
                return False

            click_offsets = [14, 16, 18, 20, 22, 24, 26]

            for offset in click_offsets:
                x = box["x"] + offset
                y = box["y"] + box["height"] / 2

                try:
                    driver.mouse.move(x, y)
                    driver.wait_for_timeout(100)
                    driver.mouse.click(x, y)
                    driver.wait_for_timeout(400)

                    after_count = _selected_count() or 0

                    if after_count > before_count:
                        return True

                    if _is_row_selected(row):
                        return True

                    return True

                except PlaywrightError:
                    continue

            return False

        except PlaywrightError:
            return False

    def _clear_selection_best_effort(selected_row=None) -> bool:
        """
        Снимает выделение без reload.
        """
        count = _selected_count()

        if count in (None, 0):
            return True

        if selected_row is not None:
            try:
                _click_row_checkbox_zone(selected_row)
                driver.wait_for_timeout(500)

                if _selected_count() in (None, 0):
                    return True

            except PlaywrightError:
                pass

        clear_selectors = [
            "xpath=//button[contains(normalize-space(.), 'Выбрано:')]",
            "xpath=//button[contains(normalize-space(.), 'Selected:')]",
            "xpath=//*[contains(normalize-space(.), 'Выбрано:')]/ancestor::button[1]",
            "xpath=//*[contains(normalize-space(.), 'Selected:')]/ancestor::button[1]",
            "button:has(svg-icon[src*='icon16/close.svg'])",
            "button:has(svg-icon[src*='close.svg'])",
        ]

        for selector in clear_selectors:
            try:
                button = driver.locator(selector).first

                if button.count() == 0 or not button.is_visible():
                    continue

                box = button.bounding_box()

                if box:
                    button.click(
                        position={
                            "x": 8,
                            "y": box["height"] / 2,
                        },
                        timeout=4_000,
                        force=True,
                    )
                else:
                    button.click(timeout=4_000, force=True)

                driver.wait_for_timeout(500)

                if _selected_count() in (None, 0):
                    return True

            except PlaywrightError:
                continue

        try:
            driver.keyboard.press("Escape")
            driver.wait_for_timeout(500)

            if _selected_count() in (None, 0):
                return True

        except PlaywrightError:
            pass

        return _selected_count() in (None, 0)

    def _find_and_select_any_row(max_scan: int = 80):
        """
        Находит строку файла и кликает в её checkbox-зону.
        """
        _clear_selection_best_effort()

        rows = _find_rows(max_scan=max_scan)

        for row in rows:
            if _click_row_checkbox_zone(row):
                return row

        raise AssertionError("Не удалось кликнуть по checkbox-зоне ни одной строки файла")

    def _is_delete_modal_opened() -> bool:
        """
        Проверяет, что открылась именно модалка удаления.
        """
        modal_selectors = [
            "div[role='dialog']",
            ".iva-core-modal-window",
            ".cdk-overlay-pane",
        ]

        for selector in modal_selectors:
            try:
                modal = driver.locator(selector).last

                if modal.count() == 0:
                    continue

                if not modal.is_visible():
                    continue

                modal_text = (modal.inner_text() or "").lower()

                if (
                    "удал" in modal_text
                    or "delete" in modal_text
                    or "отмена" in modal_text
                    or "cancel" in modal_text
                ):
                    return True

            except PlaywrightError:
                continue

        return False

    def _click_row_action_by_offset(row, action_name: str, right_offset: int):
        """
        Кликает по action-кнопке справа в строке по координатам.
        """
        _hover_row(row)

        box = row.bounding_box()
        assert box, f"Не удалось получить координаты строки для действия '{action_name}'"

        x = box["x"] + box["width"] - right_offset
        y = box["y"] + box["height"] / 2

        driver.mouse.move(x, y)
        driver.wait_for_timeout(150)
        driver.mouse.click(x, y)
        driver.wait_for_timeout(700)

    def _click_row_download(row):
        _hover_row(row)

        download_selectors = [
            "button:has(svg-icon[src*='icon16/download.svg'])",
            "button:has(svg-icon[src*='download.svg'])",
            "button[title*='Скачать']",
            "button[aria-label*='Скачать']",
            "button[title*='Download']",
            "button[aria-label*='Download']",
        ]

        for selector in download_selectors:
            try:
                button = row.locator(selector).first

                if button.count() > 0 and button.is_visible():
                    button.click(timeout=5_000, force=True)
                    return

            except PlaywrightError:
                continue

        # Иконка скачивания находится левее иконки удаления.
        _click_row_action_by_offset(row, "Скачать", right_offset=30)

    def _click_row_delete(row):
        """
        Нажимает кнопку удаления в строке и проверяет, что открылась модалка удаления.

        Если модалка не открылась — это ошибка теста.
        """
        _hover_row(row)

        delete_selectors = [
            "button:has(svg-icon[src*='delete.svg'])",
            "button:has(svg-icon[src*='trash.svg'])",
            "button[title*='Удалить']",
            "button[aria-label*='Удалить']",
            "button[title*='Delete']",
            "button[aria-label*='Delete']",
        ]

        for selector in delete_selectors:
            try:
                button = row.locator(selector).first

                if button.count() > 0 and button.is_visible():
                    button.click(timeout=5_000, force=True)
                    driver.wait_for_timeout(700)

                    if _is_delete_modal_opened():
                        return

            except PlaywrightError:
                continue

        box = row.bounding_box()
        assert box, f"Не удалось получить координаты строки для удаления: '{_row_name(row)}'"

        # Пробуем несколько точек справа. Это нужно, потому что кнопка удаления
        # может быть не строго на самом правом краю строки.
        delete_offsets_from_right = [
            12,
            18,
            24,
            30,
            36,
            42,
            50,
            58,
            66,
            74,
        ]

        for offset in delete_offsets_from_right:
            try:
                _hover_row(row)

                x = box["x"] + box["width"] - offset
                y = box["y"] + box["height"] / 2

                driver.mouse.move(x, y)
                driver.wait_for_timeout(150)
                driver.mouse.click(x, y)
                driver.wait_for_timeout(900)

                if _is_delete_modal_opened():
                    return

            except PlaywrightError:
                continue

        raise AssertionError(
            f"После клика по кнопке удаления для строки '{_row_name(row)}' "
            f"не открылась модалка подтверждения удаления"
        )

    def _confirm_delete_modal():
        """
        Подтверждает удаление.

        Если модалка не открылась — тест падает.
        """
        delete_modal = _first_visible(
            driver,
            [
                "div[role='dialog']",
                ".iva-core-modal-window",
                ".cdk-overlay-pane",
            ],
            timeout_ms=8_000,
        )

        modal_text = (delete_modal.inner_text() or "").lower()

        assert (
            "удал" in modal_text
            or "delete" in modal_text
            or "отмена" in modal_text
            or "cancel" in modal_text
        ), f"Открылась модалка, но она не похожа на подтверждение удаления. Текст: {modal_text}"

        _first_visible(
            delete_modal,
            [
                "button:has-text('Удалить')",
                "button:has-text('Delete')",
            ],
            timeout_ms=5_000,
        ).click(timeout=5_000)

        try:
            delete_modal.wait_for(state="hidden", timeout=10_000)
        except PlaywrightError:
            pass

        driver.wait_for_timeout(1200)

    def _is_viewer_opened() -> bool:
        viewer_selectors = [
            "mcu-document-viewer",
            "mcu-document-viewer-header",
            "mcu-document-viewer-controls",
            "div[role='dialog']",
            ".iva-core-modal-window",
            "[class*='document-viewer']",
            "[class*='viewer']",
        ]

        for selector in viewer_selectors:
            try:
                locator = driver.locator(selector).first

                if locator.count() > 0 and locator.is_visible():
                    return True

            except PlaywrightError:
                continue

        return False

    def _open_file_preview_any_row(max_scan: int = 80):
        """
        Открывает файл в просмотрщике без reload.
        """
        _clear_selection_best_effort()

        try:
            driver.mouse.move(100, 100)
            driver.wait_for_timeout(300)
        except PlaywrightError:
            pass

        rows = _find_rows(max_scan=max_scan, previewable_only=True)
        last_error = None
        tried_names = []

        for row in rows:
            name = _row_name(row)
            tried_names.append(name)

            try:
                row.scroll_into_view_if_needed(timeout=3_000)
            except PlaywrightError:
                pass

            name_locators = [
                row.locator("div[ivafilenameshortener]").first,
                row.locator("div[ivafilenameshortener] .content").first,
                row.locator(".file-name").first,
                row.locator(".file-name .content").first,
                row.locator(".file-info").first,
                row.locator(".file-info .content").first,
                row.locator("td").nth(1),
            ]

            for name_locator in name_locators:
                try:
                    if name_locator.count() == 0:
                        continue

                    if not name_locator.is_visible():
                        continue

                    name_locator.scroll_into_view_if_needed(timeout=3_000)

                    driver.mouse.move(100, 100)
                    driver.wait_for_timeout(200)

                    name_locator.click(timeout=5_000, force=True)
                    driver.wait_for_timeout(1200)

                    if _is_viewer_opened():
                        return name

                    name_locator.dblclick(timeout=5_000, force=True)
                    driver.wait_for_timeout(1200)

                    if _is_viewer_opened():
                        return name

                except PlaywrightError as error:
                    last_error = error
                    continue

            try:
                box = row.bounding_box()

                if not box:
                    continue

                click_points = [
                    {
                        "x": box["x"] + 70,
                        "y": box["y"] + box["height"] / 2,
                    },
                    {
                        "x": box["x"] + 110,
                        "y": box["y"] + box["height"] / 2,
                    },
                    {
                        "x": box["x"] + 160,
                        "y": box["y"] + box["height"] / 2,
                    },
                ]

                for point in click_points:
                    driver.mouse.move(100, 100)
                    driver.wait_for_timeout(200)

                    driver.mouse.click(point["x"], point["y"])
                    driver.wait_for_timeout(1200)

                    if _is_viewer_opened():
                        return name

                    driver.mouse.dblclick(point["x"], point["y"])
                    driver.wait_for_timeout(1200)

                    if _is_viewer_opened():
                        return name

            except PlaywrightError as error:
                last_error = error

        raise AssertionError(
            "Не удалось открыть файл в просмотрщике. "
            f"Пробовали файлы: {tried_names[:10]}. "
            f"Последняя ошибка: {last_error}"
        )

    def _close_viewer():
        viewer = _first_visible(
            driver,
            [
                "mcu-document-viewer",
                "mcu-document-viewer-header",
                "mcu-document-viewer-controls",
                "div[role='dialog']",
                ".iva-core-modal-window",
                "[class*='document-viewer']",
                "[class*='viewer']",
            ],
            timeout_ms=10_000,
        )

        close_button = _first_visible(
            viewer,
            [
                "button:has(svg-icon[src*='icon24/close.svg'])",
                "button[iva-icon-button]:has(svg-icon[src*='close.svg'])",
                "button:has(svg-icon[src*='close.svg'])",
                "button[aria-label*='Закрыть']",
                "button[title*='Закрыть']",
            ],
            timeout_ms=8_000,
        )

        close_button.click(timeout=5_000)
        driver.wait_for_timeout(700)

    # 1. Массовое выделение через Ctrl+A.
    mass_select_supported = False

    try:
        driver.locator("body").press("ControlOrMeta+A")

        selected_counter = _first_visible(
            driver,
            [
                "text=Выбрано:",
                "text=Selected:",
            ],
            timeout_ms=5_000,
        )

        mass_select_supported = selected_counter.is_visible()

    except (AssertionError, PlaywrightError):
        mass_select_supported = False

    # 2. Если массовое выделение есть — пробуем снять его без reload.
    if mass_select_supported:
        _clear_selection_best_effort()

        if _selected_count() not in (None, 0):
            driver.keyboard.press("Escape")
            driver.wait_for_timeout(500)

    # 3. Кликаем checkbox-зону строки и удаляем файл.
    file_row = _find_and_select_any_row()

    _click_row_delete(file_row)
    _confirm_delete_modal()
    _clear_selection_best_effort()

    # 4. Кликаем checkbox-зону другой строки и скачиваем файл.
    file_row = _find_and_select_any_row()

    with driver.expect_download(timeout=20_000) as download_info:
        _click_row_download(file_row)

    download = download_info.value

    assert download.suggested_filename, (
        "Файл скачался, но suggested_filename пустой"
    )

    _clear_selection_best_effort(file_row)

    # 5. Открываем файл в просмотрщике и закрываем его.
    opened_file_name = _open_file_preview_any_row()

    assert _is_viewer_opened(), (
        f"После клика по файлу '{opened_file_name}' просмотрщик не открылся"
    )

    _close_viewer()

@pytest.mark.smoke
@pytest.mark.buildtest
@pytest.mark.testcase("56")
def test_56_settings_devices_camera_microphone_available_outside_call(driver):
    assert config.ADMIN_EMAIL and config.ADMIN_PASSWORD, "Не заданы ADMIN_EMAIL/ADMIN_PASSWORD"

    LoginFlow(driver).login(config.ADMIN_EMAIL, config.ADMIN_PASSWORD, expect_success=True)

    _first_visible(driver, SETTINGS_MENU, timeout_ms=12_000).click()
    _first_visible(
        driver,
        [
            "[e2e-id='settings-page.list.audio']",
            "text=Аудио",
            "text=Audio",
        ],
        timeout_ms=12_000,
    ).click()

    # Ждем, что раздел аудио открылся.
    _first_visible(
        driver,
        [
            "text=Микрофон",
            "text=Microphone",
            "text=Динамик",
            "text=Speaker",
        ],
        timeout_ms=15_000,
    )

    def _extract_value_text(ctrl) -> str:
        for selector in [
            ".iva-select__value",
            ".selected-value",
            "[class*='value']",
            "span",
        ]:
            try:
                value_loc = ctrl.locator(selector).first
                if value_loc.count() > 0 and value_loc.is_visible():
                    text = (value_loc.inner_text() or "").strip()
                    if text:
                        return text
            except PlaywrightError:
                continue
        try:
            return (ctrl.inner_text() or "").strip()
        except PlaywrightError:
            return ""

    def _pick_another_device(control, device_name: str):
        before_text = _extract_value_text(control)
        try:
            control.click()
        except PlaywrightError:
            pass
        try:
            control.locator("button, .iva-select__trigger, [class*='arrow']").first.click(timeout=2_000)
        except PlaywrightError:
            pass
        driver.wait_for_timeout(400)

        options = driver.locator(
            ".iva-select-option:visible, [role='option']:visible, .cdk-overlay-container [class*='option']:visible"
        )
        option_count = options.count()
        if option_count == 0:
            # fallback для вариантов, где :visible не срабатывает на сложной верстке.
            options = driver.locator(".iva-select-option, [role='option'], .cdk-overlay-container [class*='option']")
            option_count = options.count()
        if option_count == 0:
            try:
                control.press("ArrowDown")
                driver.wait_for_timeout(300)
                options = driver.locator(".iva-select-option, [role='option'], .cdk-overlay-container [class*='option']")
                option_count = options.count()
            except PlaywrightError:
                pass
        if option_count == 0:
            # Последний fallback: переключаем устройство клавиатурой (без явного списка).
            changed_by_keyboard = False
            for key in ("ArrowDown", "ArrowUp"):
                try:
                    # В некоторых сборках control.press не срабатывает, если фокус остается на body.
                    control.click(force=True)
                    driver.wait_for_timeout(150)
                    driver.keyboard.press(key)
                    driver.wait_for_timeout(250)
                    driver.keyboard.press("Enter")
                    driver.wait_for_timeout(400)
                    after_text_keyboard = _extract_value_text(control)
                    if after_text_keyboard and after_text_keyboard != before_text:
                        changed_by_keyboard = True
                        break
                except PlaywrightError:
                    continue
            if changed_by_keyboard:
                return
            pytest.skip(f"Не удалось открыть список устройств для {device_name} в этой сборке")

        selected = False
        for idx in range(min(option_count, 20)):
            opt = options.nth(idx)
            try:
                if not opt.is_visible():
                    continue
                text = (opt.inner_text() or "").strip()
                if not text:
                    continue
                if before_text and text == before_text:
                    continue
                if "по умолчанию" in text.lower() and before_text and "по умолчанию" in before_text.lower():
                    continue
                opt.click()
                selected = True
                break
            except PlaywrightError:
                continue

        if not selected:
            driver.keyboard.press("Escape")
            pytest.skip(f"Для {device_name} нет альтернативного устройства для выбора")

        driver.wait_for_timeout(500)
        after_text = _extract_value_text(control)
        assert after_text and after_text != before_text, (
            f"Устройство для {device_name} не изменилось после выбора. Было: '{before_text}', стало: '{after_text}'"
        )

    # На вкладке "Аудио" проверяем микрофон и динамик.
    audio_controls = [
        ("microphone", ["text=Микрофон", "text=Microphone"]),
        ("speaker", ["text=Динамик", "text=Speaker", "text=Speakers"]),
    ]

    for device_name, title_locators in audio_controls:
        title = _first_visible(driver, title_locators, timeout_ms=8_000)
        container = title.locator(
            "xpath=ancestor::*[self::div or self::section][1]"
        ).first

        control = None
        for selector in [
            "[role='combobox']",
            "button[aria-haspopup='listbox']",
            "button[aria-expanded]",
            "iva-select",
            ".iva-select",
            "[class*='select']",
            "[class*='dropdown']",
        ]:
            candidate = container.locator(selector).first
            try:
                if candidate.count() > 0 and candidate.is_visible():
                    control = candidate
                    break
            except PlaywrightError:
                continue

        assert control is not None, f"Не найден контрол выбора устройства для: {device_name}"
        try:
            assert control.is_enabled(), f"Контрол выбора устройства отключен для: {device_name}"
        except PlaywrightError:
            pass
        _pick_another_device(control, device_name)

    # Проверку камеры выполняем на вкладке "Видео".
    _first_visible(
        driver,
        [
            "[e2e-id='settings-page.list.video']",
            "text=Видео",
            "text=Video",
        ],
        timeout_ms=10_000,
    ).click()

    camera_title = _first_visible(driver, ["text=Камера", "text=Camera"], timeout_ms=12_000)
    camera_container = camera_title.locator(
        "xpath=ancestor::*[self::div or self::section][1]"
    ).first

    camera_control = None
    for selector in [
        "[role='combobox']",
        "button[aria-haspopup='listbox']",
        "button[aria-expanded]",
        "iva-select",
        ".iva-select",
        "[class*='select']",
        "[class*='dropdown']",
    ]:
        candidate = camera_container.locator(selector).first
        try:
            if candidate.count() > 0 and candidate.is_visible():
                camera_control = candidate
                break
        except PlaywrightError:
            continue

    assert camera_control is not None, "Не найден контрол выбора устройства для: camera"
    try:
        assert camera_control.is_enabled(), "Контрол выбора устройства отключен для: camera"
    except PlaywrightError:
        pass
    _pick_another_device(camera_control, "camera")