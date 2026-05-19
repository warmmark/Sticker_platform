# Sticker Platform

Веб-платформа для поиска исполнителей и оформления заказов на создание цифровых стикер-паков и эмоджи-паков.

## Функции

- регистрация, вход и выход;
- личный кабинет пользователя;
- редактирование профиля, аватара и ссылок;
- каталог объявлений;
- поиск, фильтрация и сортировка;
- создание объявлений в категориях «Стикеры» и «Эмоджи»;
- ограничение: у пользователя может быть одно активное объявление на стикеры и одно активное объявление на эмоджи;
- избранное;
- оформление заказов;
- изменение статуса заказа;
- личные сообщения между пользователями;
- админ-панель Django;
- тестовые данные через management command;
- базовые автотесты.

## Технологии

- Python 3.11+
- Django 5
- SQLite
- HTML/CSS
- Django Templates

## Установка

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Создай `.env` на основе `.env.example`.

## Запуск

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Открыть сайт:

```text
http://127.0.0.1:8000/
```

Админ-панель:

```text
http://127.0.0.1:8000/admin/
```

## Тесты

```bash
python manage.py test
```

## Демо-пользователи

Команда `seed_demo` создаёт пользователей:

- artist1 / demo12345
- artist2 / demo12345
- buyer1 / demo12345

## Переменные окружения

```env
SECRET_KEY=replace-this-with-your-local-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Реальные секреты нельзя публиковать в репозитории.
