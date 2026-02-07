import random
import string
from pathlib import Path


class PasswordManager:
    """Менеджер для работы с динамическими паролями"""

    def __init__(self, filename="last_generated_password.txt"):
        self.password_file = Path(filename)

    def generate_password(self, length=12):
        """Генерирует случайный пароль"""
        # Минимальные требования: цифры, буквы, спецсимволы
        digits = random.choices(string.digits, k=3)
        letters = random.choices(string.ascii_letters, k=length - 6)
        special = random.choices("!@#$%^&*", k=3)

        all_chars = digits + letters + special
        random.shuffle(all_chars)
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
        except:
            return None

    def clear_password(self):
        """Очищает файл с паролем"""
        if self.password_file.exists():
            self.password_file.unlink()
            return True
        return False