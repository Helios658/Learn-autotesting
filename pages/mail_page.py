import re
import time
from html import unescape
from urllib.parse import unquote
from config import config


class MailPage:
    def __init__(self, page):
        self.page = page
        self.LOGIN_INPUT = "#username"
        self.PASSWORD_INPUT = "#password"
        self.SIGNIN_BUTTON = ".signinTxt"
        self.EMAIL_SUBJECT = "xpath=//*[contains(text(), 'Восстановление пароля')]"

    def _extract_reset_link_from_text(self, text):
        if not text:
            return None

        variants = [text, unescape(text), unquote(unescape(text))]
        pattern = r"https://gamma\.hi-tech\.org/v2/login/new-password[^\s<>\"']+"

        for variant in variants:
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

    def get_password_reset_link(self, wait_for_email=True):
        if wait_for_email and not self.wait_for_recovery_email():
            raise Exception("Письмо с восстановлением не пришло")

        self.page.locator(self.EMAIL_SUBJECT).first.click()
        self.page.wait_for_timeout(1500)

        deadline = time.time() + config.EXPLICIT_WAIT
        while time.time() < deadline:
            reset_link = self._extract_link_from_page_or_frames()
            if reset_link:
                print(f"✅ Нашли ссылку: {reset_link}")
                return reset_link
            self.page.wait_for_timeout(500)

        raise Exception("Не нашли ссылку восстановления в письме")