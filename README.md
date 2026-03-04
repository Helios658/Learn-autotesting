## Запуск тестов
```bash
# Все тесты
pytest -v

# Headless режим
pytest --headless -v

# Конкретный тест
pytest tests/test_login.py::test_30381_registered_user_can_login -v

# Локальный Allure-отчет
pytest -v --headless --alluredir=allure-results
allure serve allure-results
```

## Allure TestOps (опционально)
Если нужен автозалив результатов в TestOps из CI, добавьте переменные в GitLab CI/CD Variables:

```text
ALLURE_ENDPOINT=https://<your-company>.testops.cloud
ALLURE_PROJECT_ID=<project_id>
ALLURE_TOKEN=<token>
ALLURE_LAUNCH_AUTO_CLOSE=true
```

Для уведомления в Telegram используйте Webhook в Allure TestOps:

1. Откройте: **Настройки проекта → Webhooks**.
2. Выберите событие завершения запуска.
3. URL:

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/sendMessage
```

4. Тело запроса (короткое и без неподдерживаемых шаблонов):

```json
{
  "chat_id": "<TELEGRAM_CHAT_ID>",
  "text": "✅ Запуск {{launchName}} завершен\n🔗 {{launchUrl}}"
}
```

## Переменные из .env
```env
TEST_BASE_URL=
HEADLESS_MODE=true
BROWSER=chromium  # chromium | firefox | webkit
TEST_USER_EMAIL=
TEST_USER_PASSWORD=
MAIL_USERNAME=
MAIL_PASSWORD=
ADMIN_EMAIL=
ADMIN_PASSWORD=
TEST_LDAP_USER_EMAIL=
TEST_LDAP_USER_PASSWORD=
TEST_ADFS_USER_EMAIL=
TEST_ADFS_USER_PASSWORD=
TEST_USER2_EMAIL=
TEST_USER2_PASSWORD=
```

## Безопасное добавление файлов в git
```bash
git add --all :!.env :!.env.* :!*.secret :!*.key :!last_generated_password.txt
```


## CI артефакты
- `report.xml` (JUnit)
- `allure-results/` (сырые данные для Allure Report/TestOps)