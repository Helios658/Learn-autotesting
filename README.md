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
```

После этого job сам загрузит `allure-results` через `allurectl`.

Чтобы запуск в Allure TestOps закрывался сразу после завершения CI job (а не по таймауту авто-закрытия, например 1 час), добавьте переменную:

```text
ALLURE_LAUNCH_AUTO_CLOSE=true
```

В CI дополнительно используется fallback-команда `allurectl launch close`, если авто-закрытие не отработало.

Для уведомления в Telegram лучше использовать **Webhooks в Allure TestOps** (а не отправку из CI):

1. В TestOps откройте: **Настройки проекта → Webhooks**.
2. Создайте webhook на событие завершения/закрытия запуска (Launch finished/closed).
3. Для Telegram-бота укажите URL:

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/sendMessage
```

4. Пример JSON-тела (расширенный, с итогами запуска):

```json
{
  "chat_id": "1834535141",
  "text": "{{#if (eq launchStatus \"PASSED\")}}✅{{else}}❌{{/if}} Запуск \"{{launchName}}\" завершен\nСтатус: {{launchStatus}}\n📊 Total: {{total}} | Passed: {{passed}} | Failed: {{failed}} | Skipped: {{skipped}}\n🔗 {{launchUrl}}"
}
```

> Если `launchStatus/total/passed/...` или условный шаблон не поддерживаются вашей версией TestOps, используйте упрощенный вариант:

```json
{
  "chat_id": "1834535141",
  "text": "🚀 Запуск \"{{launchName}}\"\n🔗 {{launchUrl}}"
}
```

## Переменные из .env
```env
TEST_BASE_URL=
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
```

## Безопасное добавление файлов в git
```bash
git add --all :!.env :!.env.* :!*.secret :!*.key :!last_generated_password.txt
```


## CI артефакты
- `report.xml` (JUnit)
- `allure-results/` (сырые данные для Allure Report/TestOps)