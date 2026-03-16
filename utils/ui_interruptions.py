from playwright.sync_api import Error as PlaywrightError


# Кнопки/ссылки для безопасного закрытия окна приглашения/начала мероприятия.
# Важно: приоритет у отмены/закрытия, чтобы не уводить сценарий в конференцию кнопкой "Войти".
MEETING_POPUP_DISMISS_LOCATORS = [
    "button:has-text('Отмена')",
    "button:has-text('Cancel')",
    "button:has-text('Закрыть')",
    "a:has-text('Закрыть')",
    "xpath=//*[self::button or self::a][contains(normalize-space(.), 'Отмена') or contains(normalize-space(.), 'Закрыть') or contains(normalize-space(.), 'Cancel') or contains(normalize-space(.), 'Close')]",
]

# Маркеры присутствия pop-up (legacy/new).
MEETING_POPUP_ROOT_LOCATORS = [
    "[imarker='okButton']",
    "xpath=//div[@imarker='okButton'][.//*[contains(normalize-space(.), 'Войти') or contains(normalize-space(.), 'Join')]]",
    "xpath=//*[contains(., 'приглашает вас на мероприятие') or contains(., 'invites you to the meeting')]",
]


def close_meeting_start_popup_if_present(page) -> bool:
    """Пытается закрыть всплывающее окно приглашения/начала мероприятия.

    Возвращает True, если окно было обнаружено и была выполнена попытка закрытия.
    """
    popup_detected = False

    for marker in MEETING_POPUP_ROOT_LOCATORS:
        try:
            marker_locator = page.locator(marker).first
            if marker_locator.count() > 0 and marker_locator.is_visible():
                popup_detected = True
                break
        except PlaywrightError:
            continue
        except Exception:
            continue

    if not popup_detected:
        return False

    for selector in MEETING_POPUP_DISMISS_LOCATORS:
        try:
            dismiss = page.locator(selector).first
            if dismiss.count() > 0 and dismiss.is_visible():
                dismiss.click(force=True, timeout=1500)
                page.wait_for_timeout(200)
                return True
        except PlaywrightError:
            continue
        except Exception:
            continue

    # fallback: иногда видна только "Войти" (okButton). Не кликаем её специально,
    # чтобы не ломать текущий тестовый поток.
    return True