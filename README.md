# Learn-autotesting

## Установка зависимостей
```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

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