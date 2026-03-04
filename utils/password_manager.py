import secrets
import string
from pathlib import Path


class PasswordManager:
    """Менеджер для работы с динамическими паролями"""

    def __init__(self, filename="last_generated_password.txt"):
        self.password_file = Path(filename)

    def generate_password(self, length=12):
        """Генерирует случайный пароль"""
        if length < 8:
            raise ValueError("Минимальная длина пароля — 8 символов")

        # Минимальные требования: цифры, буквы, спецсимволы
        digits = [secrets.choice(string.digits) for _ in range(3)]
        letters = [secrets.choice(string.ascii_letters) for _ in range(length - 6)]
        special = [secrets.choice("!@#$%^&*") for _ in range(3)]

        all_chars = digits + letters + special
        secrets.SystemRandom().shuffle(all_chars)
        password = ''.join(all_chars)
        return password

    def save_password(self, password):
        """Сохраняет пароль в файл"""
        try:
            with open(self.password_file, 'w', encoding='utf-8') as f:
                f.write(password)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения пароля: {e}")
            return False

    def get_password(self):
        """Читает пароль из файла"""
        if not self.password_file.exists():
            return None

        try:
            with open(self.password_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except OSError:
            return None

    def clear_password(self):
        """Очищает файл с паролем"""
        if self.password_file.exists():
            self.password_file.unlink()
            return True
        return False