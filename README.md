# Learn-autotesting

## Установка зависимостей
```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```
> Важно: `allure-pytest==2.13.2` сейчас совместим с `pytest<9`, поэтому в проекте зафиксирован `pytest==8.3.5`.

## Запуск тестов
```bash
# Все тесты
pytest -v

# Headless режим
pytest --headless -v

# Конкретный тест
pytest tests/test_login.py::test_30381_registered_user_can_login -v

# С отчетом Allure
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```
## Рекомендуемая интеграция с Allure TestOps (один правильный вариант)
Проект настроен на **native-загрузку результатов напрямую из GitLab CI через `allurectl watch`**.

### Что нужно добавить в CI/CD Variables в GitLab
- `ALLURE_ENDPOINT` — URL вашего Allure TestOps (например, `https://allure.example.com`)
- `ALLURE_TOKEN` — персональный токен пользователя/бота в Allure TestOps
- `ALLURE_PROJECT_ID` — ID проекта в Allure TestOps
- `ALLURE_LAUNCH_NAME` *(опционально)* — шаблон имени запуска (если не задан, allurectl возьмёт имя по умолчанию)

После этого pipeline сам:
1. запускает `pytest`;
2. пишет результаты в `allure-results`;
3. отправляет их в TestOps через `allurectl watch`;
4. прикладывает `allure-results` как артефакт.

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