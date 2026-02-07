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
