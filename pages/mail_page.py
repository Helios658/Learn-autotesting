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

class Code2FAEmailNotReceivedError(MailPageError):
    """Письмо с кодом 2FA не было получено вовремя."""

class Code2FANotFoundError(MailPageError):
    """Код 2FA не найден в письме."""

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
        self.RECOVERY_SUBJECT_KEYWORDS = [
            "Восстановление пароля",
            "Password Recovery",
            "Set a new password",
            "Video Conference System Password Recovery",
            "gamma.hi-tech.org Video Confer",
        ]
        self.EMAIL_SUBJECT_LOCATORS = [
            "xpath=//a[contains(., 'Восстановление пароля')]",
            "xpath=//a[contains(., 'Password Recovery')]",
            "xpath=//a[contains(., 'Set a new password')]",
            "xpath=//a[contains(., 'Video Conference System Password Recovery')]",
            "xpath=//a[contains(., 'gamma.hi-tech.org Video Confer')]",
            "xpath=//span[contains(., 'Восстановление пароля')]/ancestor::a[1]",
            "xpath=//span[contains(., 'Password Recovery')]/ancestor::a[1]",
        ]
        self.CODE_2FA_SUBJECT_KEYWORDS = [
            "Подтверждение входа",
            "Verification code",
            "Login confirmation",
            "Security code",
        ]
        self.INVITE_EMAIL_SUBJECT = "xpath=//*[contains(text(), 'Приглашение на мероприятие')]"
        self.CODE_2FA_EMAIL_SUBJECT = "xpath=//*[contains(text(), 'Подтверждение входа')]"

    @staticmethod
    def _escape_xpath_text(value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ", \"'\", ".join([f"'{part}'" for part in parts]) + ")"

    @staticmethod
    def _first_visible(locator, limit: int = 30):
        try:
            count = locator.count()
        except Exception:
            return None

        for idx in range(min(count, limit)):
            candidate = locator.nth(idx)
            try:
                if candidate.is_visible():
                    return candidate
            except Exception:
                continue
        return None

    def _find_recovery_email_subject(self):
        for selector in self.EMAIL_SUBJECT_LOCATORS:
            try:
                subject = self._first_visible(self.page.locator(selector))
                if subject is not None:
                    return subject
            except Exception:
                continue
        return self._find_email_subject_by_keywords(self.RECOVERY_SUBJECT_KEYWORDS)

    def _find_2fa_email_subject(self):
        # Приоритет — старый, уже известный локатор.
        try:
            subject = self._first_visible(self.page.locator(self.CODE_2FA_EMAIL_SUBJECT))
            if subject is not None:
                return subject
        except Exception:
            pass

        return self._find_email_subject_by_keywords(self.CODE_2FA_SUBJECT_KEYWORDS)

    def _find_email_subject_by_keywords(self, keywords):
        for keyword in keywords:
            escaped = self._escape_xpath_text(keyword)
            selectors = [
                f"xpath=//a[contains(., {escaped})]",
                f"xpath=//span[contains(., {escaped})]/ancestor::a[1]",
                f"xpath=//span[contains(., {escaped})]/ancestor::div[1]",
                f"xpath=//div[contains(., {escaped}) and @role='option']",
            ]
            for selector in selectors:
                try:
                    subject = self._first_visible(self.page.locator(selector))
                    if subject is not None:
                        return subject
                except Exception:
                    continue
        return None

    def _open_email_by_subject(self, subject):
        try:
            subject.click(timeout=5_000)
            return
        except Exception:
            pass

        try:
            parent_anchor = subject.locator("xpath=ancestor::a[1]").first
            if parent_anchor.count() > 0 and parent_anchor.is_visible():
                parent_anchor.click(timeout=5_000)
                return
        except Exception:
            pass

        subject.click(force=True, timeout=5_000)

    def _click_reset_link_if_present(self):
        """
        Пытается получить reset-link из видимого anchor:
        1) из href / outerHTML;
        2) через открытие новой вкладки;
        3) через переход в этой же вкладке.
        Проверяет как текущую страницу, так и iframe письма.
        Возвращает reset-link (str) или None.
        """
        link_locators = [
            "a:has-text('link')",
            "a:has-text('ссылке')",
            "a[href*='/v2/login/new-password']",
        ]

        search_contexts = [self.page, *self.page.frames]

        for context in search_contexts:
            for selector in link_locators:
                try:
                    links = context.locator(selector)
                    count = links.count()
                except Exception:
                    continue

                for idx in range(min(count, 10)):
                    link = links.nth(idx)
                    try:
                        if not link.is_visible():
                            continue
                    except Exception:
                        continue

                    # 1) Сначала пытаемся вытащить URL без клика (href / html)
                    for href_expr in (
                            "el => el.getAttribute('href') || ''",
                            "el => el.href || ''",
                    ):
                        try:
                            href = link.evaluate(href_expr) or ""
                            reset_link = self._extract_reset_link_from_text(href)
                            if reset_link:
                                return reset_link
                        except Exception:
                            pass

                    try:
                        outer_html = link.evaluate("el => el.outerHTML")
                        reset_link = self._extract_reset_link_from_text(outer_html or "")
                        if reset_link:
                            return reset_link
                    except Exception:
                        pass

                    # 2) Пытаемся кликнуть и поймать новую вкладку
                    try:
                        with self.page.context.expect_page(timeout=3000) as page_info:
                            link.click(force=True, timeout=2000)
                        new_page = page_info.value
                        try:
                            new_page.wait_for_load_state("domcontentloaded", timeout=5000)
                        except Exception:
                            pass

                        popup_url = new_page.url or ""
                        reset_link = self._extract_reset_link_from_text(popup_url)
                        if reset_link:
                            return reset_link
                    except Exception:
                        pass

                    # 3) Переход в текущей вкладке
                    try:
                        before_url = self.page.url
                        link.click(force=True, timeout=2000)
                        self.page.wait_for_timeout(800)
                        after_url = self.page.url

                        if after_url and after_url != before_url:
                            reset_link = self._extract_reset_link_from_text(after_url)
                            if reset_link:
                                return reset_link
                    except Exception:
                        continue

        return None

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

    def _extract_code_from_text(self, text):
        if not text:
            return None

        variants = [text, unescape(text), unquote(unescape(text))]
        patterns = [
            r"Код подтверждения входа:\s*(\d{4,8})",
            r"Код подтверждения:\s*(\d{4,8})",
            r"код\s+подтверждения[\s:]+(\d{4,8})",
        ]

        for variant in variants:
            for pattern in patterns:
                match = re.search(pattern, variant, flags=re.IGNORECASE)
                if match:
                    return match.group(1)

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
            if self._find_recovery_email_subject() is not None:
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

        subject = self._find_recovery_email_subject()
        if subject is None:
            raise RecoveryEmailNotReceivedError("Письмо с восстановлением не найдено в списке")

        self._open_email_by_subject(subject)
        self.page.wait_for_timeout(1500)

        deadline = time.time() + config.EXPLICIT_WAIT
        while time.time() < deadline:
            clicked_link = self._click_reset_link_if_present()
            if clicked_link:
                print(f"✅ Нашли ссылку по anchor-click: {clicked_link}")
                return clicked_link

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
        self._open_email_by_subject(subject)
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

    def _extract_2fa_code_from_page_or_frames(self):
        code = self._extract_code_from_text(self.page.content())
        if code:
            return code

        visible_text = self.page.locator("body").inner_text(timeout=2000)
        code = self._extract_code_from_text(visible_text)
        if code:
            return code

        for frame in self.page.frames:
            try:
                code = self._extract_code_from_text(frame.content())
                if code:
                    return code
            except Exception:
                pass

            try:
                frame_text = frame.locator("body").inner_text(timeout=2000)
                code = self._extract_code_from_text(frame_text)
                if code:
                    return code
            except Exception:
                pass

        return None

    def wait_for_2fa_code_email(self, timeout=60):
        print(f"⏳ Ждем письмо (макс {timeout} сек)...")
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.page.reload(wait_until="domcontentloaded")
            if self._find_2fa_email_subject() is not None:
                print("✅ Письмо найдено!")
                return True
            self.page.wait_for_timeout(2000)

        print(f"❌ Письмо не пришло за {timeout} секунд")
        return False

    def open_2fa_email(self, wait_for_email=True):
        if wait_for_email and not self.wait_for_2fa_code_email():
            raise Code2FAEmailNotReceivedError("Письмо с кодом не пришло")

        subject = self._find_2fa_email_subject()
        if subject is None:
            raise Code2FAEmailNotReceivedError("Письмо с кодом не найдено в списке")
        subject.wait_for(state="visible", timeout=config.EXPLICIT_WAIT * 1000)
        subject.click()
        self.page.wait_for_timeout(1500)
        return self

    def get_2fa_code_from_email(self, wait_for_email=True):
        if wait_for_email:
            self.open_2fa_email(wait_for_email=True)

        deadline = time.time() + config.EXPLICIT_WAIT

        while time.time() < deadline:
            code_2fa = self._extract_2fa_code_from_page_or_frames()
            if code_2fa:
                print("✅ Код 2FA найден в письме")
                return code_2fa

            self.page.wait_for_timeout(500)

        raise Code2FANotFoundError("Код 2FA не найден в письме")