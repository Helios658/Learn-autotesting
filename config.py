# config.py
import os
from dotenv import load_dotenv
from utils.password_manager import PasswordManager

# Загружаем переменные из .env файла
load_dotenv()


def get_dynamic_password():
    """Получает последний сгенерированный пароль из файла"""
    password_file = Path("last_generated_password.txt")

    if password_file.exists():
        """Получает последний сгенерированный пароль из файла через PasswordManager."""
        manager = PasswordManager()
        password = manager.get_password()

        if password:
            print(f"📁 Прочитан динамический пароль из {manager.password_file.name}")
            return password

        if manager.password_file.exists():
            print(f"⚠️ Файл {manager.password_file.name} пустой")

    # Если файла нет или он пустой - используем значение из .env или дефолт
    env_password = os.getenv('TEST_USER_PASSWORD', '')
    if env_password:
        print("📝 Используем пароль из .env файла")
        return env_password

    print("⚠️ Динамический пароль не найден, будет использована пустая строка")
    return ""


class Config:
    """Конфигурация тестового окружения"""

    # ========== Базовые настройки ==========
    BASE_URL = os.getenv('TEST_BASE_URL', 'https://gamma.hi-tech.org')
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '5'))
    EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', '10'))

    # ========== Пользовательские данные ==========
    # Основной тестовый пользователь
    USER_EMAIL = os.getenv('TEST_USER_EMAIL', 'v.kornienko@iva.ru')

    # 🔧 ДИНАМИЧЕСКИЙ ПАРОЛЬ - читается из файла
    @property
    def USER_PASSWORD(self):
        """Динамическое свойство - пароль всегда свежий"""
        return get_dynamic_password()

    # Почтовый ящик для восстановления пароля
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'v.kornienko@iva-tech.ru')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')

    # Администратор
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@admin1.ru')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '123456')

    # ========== Настройки запуска ==========
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    BROWSER = os.getenv('BROWSER', 'chrome')

    # ========== URL endpoints ==========
    @property
    def LOGIN_URL(self):
        return f"{self.BASE_URL}/v2/login"

    @property
    def MAIL_URL(self):
        return "https://mail.hi-tech.org"


# Создаем экземпляр конфигурации
config = Config()

# Тестовая проверка
if __name__ == "__main__":
    print(f"USER_EMAIL: {config.USER_EMAIL}")
    print(f"USER_PASSWORD: {'*' * len(config.USER_PASSWORD) if config.USER_PASSWORD else '(пусто)'}")
    print(f"Пароль из файла: {get_dynamic_password()}")