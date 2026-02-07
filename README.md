# Learn-autotesting
autotests_gamma/
├── pages/ # Page Object Models
│ ├── base_page.py # Базовый класс всех страниц
│ ├── login_page.py # Страница логина (готово)
│ ├── main_page.py # Главная страница (новое)
│ ├── call_page.py # Страница звонка (новое)
│ ├── recovery_page.py # Восстановление пароля
│ ├── mail_page.py # Работа с почтой
│ └── new_password_page.py # Установка нового пароля
├── tests/ # Тесты
│ ├── test_login.py # Тесты логина
│ ├── test_logout.py # Тесты выхода
│ └── test_password_recovery.py # Восстановление пароля
├── config.py # Конфигурация
├── conftest.py # Pytest фиктуры
├── requirements.txt # Зависимости
└── README.md # Документация

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
