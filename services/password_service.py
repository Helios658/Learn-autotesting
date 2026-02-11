from utils.password_manager import PasswordManager


class PasswordService:
    """Сервис для генерации и сохранения пароля после восстановления."""

    def __init__(self, manager=None):
        self.manager = manager or PasswordManager()

    def generate_and_persist_password(self):
        """Генерирует пароль и сохраняет его для последующего входа."""
        password = self.manager.generate_password()
        is_saved = self.manager.save_password(password)

        if is_saved:
            print(f"📋 Сгенерирован и сохранен пароль: {password}")
        else:
            print(f"📋 Сгенерирован пароль: {password} (не сохранен в файл)")

        return password