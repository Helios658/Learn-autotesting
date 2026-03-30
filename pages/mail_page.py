import email
import imaplib
import re
import time
from email.header import decode_header
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
    SID_LINK_PATTERN = r"https?://[^\s<>\"']*[\?&]sid=[^\s<>\"'&]+[^\s<>\"']*"

    def __init__(self, page=None):
        self.page = page  # совместимость со старыми вызовами
        self.RECOVERY_SUBJECT_KEYWORDS = [
            "Восстановление пароля",
            "Password Recovery",
            "Set a new password",
            "Video Conference System Password Recovery",
            "gamma.hi-tech.org Video Confer",
        ]
        self.CODE_2FA_SUBJECT_KEYWORDS = [
            "Подтверждение входа",
            "Verification code",
            "Login confirmation",
            "Security code",
        ]
        self.INVITATION_SUBJECT_KEYWORDS = [
            "Приглашение на мероприятие",
            "Event invitation",
        ]
        self._imap_last_invitation_message = None
        self._imap_last_2fa_message = None

    @staticmethod
    def _decode_mime_header(value: str) -> str:
        if not value:
            return ""
        chunks = decode_header(value)
        decoded = []
        for chunk, enc in chunks:
            if isinstance(chunk, bytes):
                decoded.append(chunk.decode(enc or "utf-8", errors="ignore"))
            else:
                decoded.append(chunk)
        return "".join(decoded)

    def _ensure_imap_config(self):
        if not config.MAIL_IMAP_HOST:
            raise MailPageError(
                "IMAP режим обязателен, но не задан MAIL_IMAP_HOST. "
                "Укажите MAIL_IMAP_HOST/MAIL_IMAP_PORT/MAIL_IMAP_FOLDER в .env"
            )

    def _imap_search_messages(self, timeout_sec: int = 60, unread_only: bool = False):
        self._ensure_imap_config()

        deadline = time.time() + timeout_sec
        username = config.MAIL_USERNAME
        password = config.MAIL_PASSWORD
        folder = config.MAIL_IMAP_FOLDER or "INBOX"
        host = config.MAIL_IMAP_HOST
        port = config.MAIL_IMAP_PORT

        while time.time() < deadline:
            try:
                with imaplib.IMAP4_SSL(host, port) as imap:
                    imap.login(username, password)
                    imap.select(folder)
                    search_criteria = "UNSEEN" if unread_only else "ALL"
                    status, data = imap.search(None, search_criteria)
                    if status != "OK":
                        time.sleep(2)
                        continue

                    message_ids = data[0].split()[-50:]
                    messages = []
                    for message_id in reversed(message_ids):
                        fetch_status, msg_data = imap.fetch(message_id, "(RFC822)")
                        if fetch_status != "OK" or not msg_data:
                            continue

                        raw_msg = msg_data[0][1]
                        msg = email.message_from_bytes(raw_msg)
                        subject = self._decode_mime_header(msg.get("Subject", ""))
                        message_id_header = msg.get("Message-ID", "")
                        date_header = msg.get("Date", "")

                        body_parts = []
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition") or "")
                                if "attachment" in content_disposition.lower():
                                    continue
                                if content_type in ("text/plain", "text/html"):
                                    payload = part.get_payload(decode=True) or b""
                                    charset = part.get_content_charset() or "utf-8"
                                    body_parts.append(payload.decode(charset, errors="ignore"))
                        else:
                            payload = msg.get_payload(decode=True) or b""
                            charset = msg.get_content_charset() or "utf-8"
                            body_parts.append(payload.decode(charset, errors="ignore"))

                        body = "\n".join(body_parts)
                        signature = f"{message_id_header}|{date_header}|{subject}"
                        messages.append(
                            {
                                "subject": subject,
                                "body": body,
                                "signature": signature,
                                "message_id": message_id.decode(errors="ignore"),
                            }
                        )
                    return messages
            except Exception:
                time.sleep(2)
                continue

        return []

    def _imap_snapshot(self, keywords: list[str]) -> set[str]:
        signatures = set()
        for item in self._imap_search_messages(timeout_sec=8):
            haystack = f"{item['subject']}\n{item['body']}".lower()
            if any(keyword.lower() in haystack for keyword in keywords):
                signatures.add(item["signature"])
        return signatures

    def _imap_find_new_message(
        self,
        keywords: list[str],
        exclude_signatures: set[str] | None,
        timeout_sec: int = 60,
        unread_only: bool | None = None,
    ):
        exclude_signatures = exclude_signatures or set()
        if unread_only is None:
            unread_only = config.MAIL_IMAP_UNREAD_ONLY
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            for item in self._imap_search_messages(timeout_sec=10, unread_only=unread_only):
                if item["signature"] in exclude_signatures:
                    continue
                haystack = f"{item['subject']}\n{item['body']}".lower()
                if any(keyword.lower() in haystack for keyword in keywords):
                    return item
            time.sleep(2)
        return None

    @staticmethod
    def _extract_first_http_url(text):
        if not text:
            return None

        variants = [text, unescape(text), unquote(unescape(text))]
        pattern = r"https?://[^\s<>\"']+"
        for variant in variants:
            match = re.search(pattern, variant)
            if match:
                return unescape(match.group(0))
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

    def _extract_join_link_from_text(self, text):
        if not text:
            return None

        variants = [text, unescape(text), unquote(unescape(text))]
        join_link_pattern = r"https?://[^\s<>\"']+#join:[^\s<>\"']+"
        preferred_host = (urlparse(config.BASE_URL).hostname or "").lower()

        def _rank(link: str) -> tuple:
            host = (urlparse(link).hostname or "").lower()
            return (1 if preferred_host and host == preferred_host else 0, 1 if "#join:s" in link.lower() else 0)

        for variant in variants:
            matches = [m.group(0).rstrip("\"'.,;:!?)>]") for m in re.finditer(join_link_pattern, variant)]
            matches = [m for m in matches if "#join:" in m]
            if matches:
                return sorted(matches, key=_rank, reverse=True)[0]

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

    def _extract_sid_link_from_text(self, text):
        if not text:
            return None

        variants = [text, unescape(text), unquote(unescape(text))]
        for variant in variants:
            match = re.search(self.SID_LINK_PATTERN, variant, flags=re.IGNORECASE)
            if not match:
                continue
            link = unescape(match.group(0)).rstrip("\"'.,;:!?)>]")
            if "sid=" in link.lower():
                return link
        return None

    def login(self, username=None, password=None):
        # Для IMAP-режима "логин" — это проверка соединения без чтения писем.
        self._ensure_imap_config()
        username = username or config.MAIL_USERNAME
        password = password or config.MAIL_PASSWORD
        folder = config.MAIL_IMAP_FOLDER or "INBOX"
        host = config.MAIL_IMAP_HOST
        port = config.MAIL_IMAP_PORT

        with imaplib.IMAP4_SSL(host, port) as imap:
            imap.login(username, password)
            imap.select(folder)

        print(f"✅ Успешное IMAP-подключение: {username}")
        return self

    def _wait_for_email(self, keywords, timeout=60, exclude_signatures: set[str] | None = None):
        return self._imap_find_new_message(
            keywords=keywords,
            exclude_signatures=exclude_signatures,
            timeout_sec=timeout,
        )

    def snapshot_recovery_emails(self):
        return self._imap_snapshot(self.RECOVERY_SUBJECT_KEYWORDS)

    def snapshot_invitation_emails(self):
        return self._imap_snapshot(self.INVITATION_SUBJECT_KEYWORDS)

    def snapshot_2fa_emails(self):
        return self._imap_snapshot(self.CODE_2FA_SUBJECT_KEYWORDS)

    def wait_for_recovery_email(self, timeout=60, exclude_signatures: set[str] | None = None):
        return self._wait_for_email(self.RECOVERY_SUBJECT_KEYWORDS, timeout=timeout, exclude_signatures=exclude_signatures) is not None

    def wait_for_invitation_email(self, timeout=60, exclude_signatures: set[str] | None = None):
        return self._wait_for_email(self.INVITATION_SUBJECT_KEYWORDS, timeout=timeout, exclude_signatures=exclude_signatures) is not None

    def wait_for_2fa_code_email(self, timeout=60, exclude_signatures: set[str] | None = None):
        return self._wait_for_email(self.CODE_2FA_SUBJECT_KEYWORDS, timeout=timeout, exclude_signatures=exclude_signatures) is not None

    def get_password_reset_link(self, wait_for_email=True, exclude_signatures: set[str] | None = None):
        message = self._imap_find_new_message(
            keywords=self.RECOVERY_SUBJECT_KEYWORDS,
            exclude_signatures=exclude_signatures,
            timeout_sec=60 if wait_for_email else 5,
        )
        if not message:
            raise RecoveryEmailNotReceivedError("Письмо с восстановлением не пришло")

        link = self._extract_reset_link_from_text(message["body"]) or self._extract_first_http_url(message["body"])
        if not link:
            raise RecoveryLinkNotFoundError("Не нашли ссылку восстановления в письме (IMAP)")

        print(f"✅ Нашли recovery ссылку через IMAP: {link}")
        return link

    def open_invitation_email(self, wait_for_email=True, exclude_signatures: set[str] | None = None):
        message = self._imap_find_new_message(
            keywords=self.INVITATION_SUBJECT_KEYWORDS,
            exclude_signatures=exclude_signatures,
            timeout_sec=60 if wait_for_email else 5,
        )
        if not message:
            raise InvitationEmailNotReceivedError("Письмо с приглашением не пришло")

        self._imap_last_invitation_message = message
        return self

    def get_invitation_join_link(self):
        if not self._imap_last_invitation_message:
            raise InvitationLinkNotFoundError("Invitation message не открыт (IMAP)")

        join_link = self._extract_join_link_from_text(self._imap_last_invitation_message.get("body", ""))
        if not join_link:
            raise InvitationLinkNotFoundError("Не нашли ссылку приглашения в письме (IMAP)")

        print(f"✅ Нашли invitation join ссылку через IMAP: {join_link}")
        return join_link

    def open_2fa_email(self, wait_for_email=True, exclude_signatures: set[str] | None = None):
        message = self._imap_find_new_message(
            keywords=self.CODE_2FA_SUBJECT_KEYWORDS,
            exclude_signatures=exclude_signatures,
            timeout_sec=60 if wait_for_email else 5,
        )
        if not message:
            raise Code2FAEmailNotReceivedError("Письмо с кодом не пришло")

        self._imap_last_2fa_message = message
        return self

    def get_2fa_code_from_email(self, wait_for_email=True, exclude_signatures: set[str] | None = None):
        if wait_for_email:
            self.open_2fa_email(wait_for_email=True, exclude_signatures=exclude_signatures)

        if not self._imap_last_2fa_message:
            raise Code2FANotFoundError("2FA message не открыт (IMAP)")

        code_2fa = self._extract_code_from_text(self._imap_last_2fa_message.get("body", ""))
        if not code_2fa:
            raise Code2FANotFoundError("Код 2FA не найден в письме (IMAP)")

        print("✅ Код 2FA найден через IMAP")
        return code_2fa

    def get_invitation_sid_link(self):
        if not self._imap_last_invitation_message:
            raise InvitationLinkNotFoundError("Invitation message не открыт (IMAP)")

        sid_link = self._extract_sid_link_from_text(self._imap_last_invitation_message.get("body", ""))
        if not sid_link:
            raise InvitationLinkNotFoundError("Не нашли sid-ссылку приглашения в письме (IMAP)")

        print(f"✅ Нашли sid-ссылку приглашения через IMAP: {sid_link}")
        return sid_link