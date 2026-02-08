# Learn-autotesting

### Установка зависимостей
```bash
pip install -r requirements.txt

Запуск тестов
# Все тесты
pytest -v

# Headless режим (без UI браузера)
pytest --headless -v

# Конкретный тест
pytest tests/test_login.py::test_successful_login -v

# С отчетом Allure
pytest --alluredir=reports/allure-results
allure serve reports/allure-results

#Как добавлять код, что бы не попали чувствительные файлы
git add --all :!.env :!.env.* :!*.secret :!*.key :!last_generated_password.txt

#Параметры из .env
TEST_BASE_URL=
TEST_USER_EMAIL=
TEST_USER_PASSWORD=
MAIL_USERNAME=
MAIL_PASSWORD=
ADMIN_EMAIL=
ADMIN_PASSWORD=
