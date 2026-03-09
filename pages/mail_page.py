import re
import time
from html import unescape
from urllib.parse import unquote, urlparse
from config import config

class MailPageError(RuntimeError):
    """Базовая ошибка для сценариев работы с почтой."""


class RecoveryEmailNotReceivedError(MailPageError):
    """Письмо для восстановления пароля не было получено вовремя."""


class RecoveryLinkNotFoundError(MailPageError):
    """Ссылка на восстановление пароля не найдена в письме."""

class InvitationEmailNotReceivedError(MailPageError):
    """Письмо с приглашением на мероприятие не было получено вовремя."""


class InvitationLinkNotFoundError(MailPageError):
    """Ссылка приглашения на мероприятие не найдена в письме."""

class MailPage:
    JOIN_LINK_STRICT_PATTERN = (
        r"https?://[^\s<>\"']+#join:[a-zA-Z]"
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )

    def __init__(self, page):
        self.page = page
        self.LOGIN_INPUT = "#username"
        self.PASSWORD_INPUT = "#password"
        self.SIGNIN_BUTTON = ".signinTxt"
        self.EMAIL_SUBJECT = "xpath=//*[contains(text(), 'Восстановление пароля')]"
        self.INVITE_EMAIL_SUBJECT = "xpath=//*[contains(text(), 'Приглашение на мероприятие')]"

    def _extract_reset_link_from_text(self, text):
        if not text:
            return None

        variants = [text, unescape(text), unquote(unescape(text))]
        base_url_pattern = rf"{re.escape(config.BASE_URL.rstrip('/'))}/v2/login/new-password[^\s<>\"']+"
        fallback_pattern = r"https?://[^\s<>\"']+/v2/login/new-password[^\s<>\"']+"

        for variant in variants:
            for pattern in (base_url_pattern, fallback_pattern):
                match = re.search(pattern, variant)
                if match:
                    return unescape(match.group())

        return None

    def _extract_link_from_page_or_frames(self):
        # 1) Быстрый путь: HTML текущей страницы
        link = self._extract_reset_link_from_text(self.page.content())
        if link:
            return link

        # 2) Ссылки из DOM текущей страницы
        hrefs = self.page.evaluate(
            """
            () => Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href') || '')
            """
        )
        for href in hrefs:
            link = self._extract_reset_link_from_text(href)
            if link:
                return link

        # 3) Проверка контента/ссылок во фреймах (часто письмо рендерится во внутреннем iframe)
        for frame in self.page.frames:
            try:
                link = self._extract_reset_link_from_text(frame.content())
                if link:
                    return link
                frame_hrefs = frame.evaluate(
                    """
                    () => Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href') || '')
                    """
                )
                for href in frame_hrefs:
                    link = self._extract_reset_link_from_text(href)
                    if link:
                        return link
            except Exception:
                continue

        return None

    def _extract_join_link_from_text(self, text):
        if not text:
            return None

        variants = [text, unescape(text), unquote(unescape(text))]
        join_link_pattern = r"https?://[^\s<>\"']+#join:[^\s<>\"']+"

        browser_entry_patterns = [
            r"Для\s+входа\s+через\s+браузер\s*:\s*(https?://[^\s<>\"']+#join:[^\s<>\"']+)",
            r"Для\s+входа\s+через\s+браузер[\s\S]{0,250}?(https?://[^\s<>\"']+#join:[^\s<>\"']+)",
        ]

        preferred_host = (urlparse(config.BASE_URL).hostname or "").lower()

        def _rank(link: str) -> tuple:
            host = (urlparse(link).hostname or "").lower()
            return (
                1 if preferred_host and host == preferred_host else 0,
                1 if "#join:s" in link.lower() else 0,
            )

        for variant in variants:
            browser_candidates = []
            for pattern in browser_entry_patterns:
                for match in re.finditer(pattern, variant, flags=re.IGNORECASE):
                    cleaned = self._normalize_join_link(match.group(1))
                    if cleaned:
                        browser_candidates.append(cleaned)

            if browser_candidates:
                return sorted(browser_candidates, key=_rank, reverse=True)[0]

            strict_matches = [
                self._normalize_join_link(m.group(0))
                for m in re.finditer(self.JOIN_LINK_STRICT_PATTERN, variant, flags=re.IGNORECASE)
            ]
            strict_matches = [m for m in strict_matches if m]
            if strict_matches:
                return sorted(strict_matches, key=_rank, reverse=True)[0]

            matches = [
                self._normalize_join_link(m.group(0))
                for m in re.finditer(join_link_pattern, variant)
            ]
            matches = [m for m in matches if m]
            if matches:
                return sorted(matches, key=_rank, reverse=True)[0]

        return None

    def _normalize_join_link(self, link: str):
        if not link:
            return None

        normalized = unescape(link).strip()
        normalized = normalized.rstrip("\"'.,;:!?)>]")

        strict_match = re.search(self.JOIN_LINK_STRICT_PATTERN, normalized, flags=re.IGNORECASE)
        if strict_match:
            return strict_match.group(0)

        return normalized if "#join:" in normalized else None

    def _extract_join_link_from_page_or_frames(self):
        link = self._extract_join_link_from_text(self.page.content())
        if link:
            return link

        hrefs = self.page.evaluate(
            """
            () => Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href') || '')
            """
        )
        for href in hrefs:
            link = self._extract_join_link_from_text(href)
            if link:
                return link

        for frame in self.page.frames:
            try:
                link = self._extract_join_link_from_text(frame.content())
                if link:
                    return link

                frame_hrefs = frame.evaluate(
                    """
                    () => Array.from(document.querySelectorAll('a[href]')).map(a => a.getAttribute('href') || '')
                    """
                )
                for href in frame_hrefs:
                    link = self._extract_join_link_from_text(href)
                    if link:
                        return link
            except Exception:
                continue

        return None

    def login(self, username=None, password=None):
        username = username or config.MAIL_USERNAME
        password = password or config.MAIL_PASSWORD

        self.page.goto(config.MAIL_URL, wait_until="domcontentloaded")
        self.page.locator(self.LOGIN_INPUT).first.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        self.page.locator(self.LOGIN_INPUT).first.fill(username)
        self.page.locator(self.PASSWORD_INPUT).first.fill(password)
        self.page.locator(self.SIGNIN_BUTTON).first.click()

        try:
            self.page.wait_for_url(re.compile(r"/mail/"), timeout=config.EXPLICIT_WAIT * 1000)
            print(f"✅ Успешный вход на почту: {username}")
        except Exception:
            print("⚠️ Возможно проблемы со входом, но продолжаем...")

        return self

    def wait_for_recovery_email(self, timeout=60):
        print(f"⏳ Ждем письмо (макс {timeout} сек)...")
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.page.reload(wait_until="domcontentloaded")
            if self.page.locator(self.EMAIL_SUBJECT).count() > 0:
                print("✅ Письмо найдено!")
                return True
            self.page.wait_for_timeout(2000)

        print(f"❌ Письмо не пришло за {timeout} секунд")
        return False

    def wait_for_invitation_email(self, timeout=60):
        print(f"⏳ Ждем письмо с приглашением (макс {timeout} сек)...")
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.page.reload(wait_until="domcontentloaded")
            if self.page.locator(self.INVITE_EMAIL_SUBJECT).count() > 0:
                print("✅ Письмо-приглашение найдено!")
                return True
            self.page.wait_for_timeout(2000)

        print(f"❌ Письмо-приглашение не пришло за {timeout} секунд")
        return False

    def get_password_reset_link(self, wait_for_email=True):
        if wait_for_email and not self.wait_for_recovery_email():
            raise RecoveryEmailNotReceivedError("Письмо с восстановлением не пришло")

        self.page.locator(self.EMAIL_SUBJECT).first.click()
        self.page.wait_for_timeout(1500)

        deadline = time.time() + config.EXPLICIT_WAIT
        while time.time() < deadline:
            reset_link = self._extract_link_from_page_or_frames()
            if reset_link:
                print(f"✅ Нашли ссылку: {reset_link}")
                return reset_link
            self.page.wait_for_timeout(500)

        raise RecoveryLinkNotFoundError("Не нашли ссылку восстановления в письме")

    def open_invitation_email(self, wait_for_email=True):
        if wait_for_email and not self.wait_for_invitation_email():
            raise InvitationEmailNotReceivedError("Письмо с приглашением не пришло")

        subject = self.page.locator(self.INVITE_EMAIL_SUBJECT).first
        subject.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        subject.click()
        self.page.wait_for_timeout(1500)
        return self

    def get_invitation_join_link(self):
        deadline = time.time() + config.EXPLICIT_WAIT
        while time.time() < deadline:
            join_link = self._extract_join_link_from_page_or_frames()
            if join_link:
                print(f"✅ Нашли ссылку приглашения: {join_link}")
                return join_link
            self.page.wait_for_timeout(500)

        raise InvitationLinkNotFoundError("Не нашли ссылку приглашения в уже открытом письме")