# Kaisen API

Django REST API проект для управления пользователями и привычками с токенной аутентификацией.

## Технологии

- **Python 3.14**
- **Django 6.1**
- **Django REST Framework 3.18**
- **PostgreSQL** (база данных)
- **Redis** (для Celery)
- **Celery** (фоновые задачи)
- **Poetry** (управление зависимостями)

## Функциональность

### Пользователи
- Регистрация с email и паролем
- Аутентификация с выдачей токена
- Просмотр и редактирование профиля
- Мягкое удаление аккаунта (деактивация)
- Список пользователей (для администраторов)
- Выход из системы с инвалидацией токена

### API документация
- Swagger UI: `/api/docs/swagger/`
- ReDoc: `/api/docs/redoc/`
- OpenAPI схема: `/api/schema/`

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd Kaisen
```

### 2. Создание виртуального окружения и установка зависимостей
```bash
poetry install
poetry shell
```

### 3. Настройка переменных окружения
Скопируйте файл `.env.sample` в `.env` и заполните его:
```bash
cp .env.sample .env
```

Обязательные переменные в `.env`:
```env
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=kaisen_db
DB_USER=kaisen_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin-password
```

### 4. Запуск контейнеров Docker (PostgreSQL, Redis)
```bash
docker-compose up -d
```

### 5. Применение миграций
```bash
python manage.py migrate
```

### 6. Создание суперпользователя
```bash
python manage.py csu
```

### 7. Запуск сервера разработки
```bash
python manage.py runserver
```

API будет доступен по адресу: `http://127.0.0.1:8000`

## API эндпоинты

### Аутентификация
- `POST /api/v1/users/register/` - Регистрация пользователя
- `POST /api/v1/auth/login/` - Вход в систему (возвращает токен)
- `POST /api/v1/auth/logout/` - Выход из системы

### Пользователи
- `GET /api/v1/users/profile/` - Получить профиль текущего пользователя
- `PUT /api/v1/users/profile/` - Полное обновление профиля
- `PATCH /api/v1/users/profile/` - Частичное обновление профиля
- `DELETE /api/v1/users/profile/` - Удаление аккаунта (деактивация)
- `GET /api/v1/users/` - Список пользователей (только для админов)

## Использование токена

После регистрации или входа сохраните полученный токен и используйте его в заголовке Authorization:

```bash
curl -H "Authorization: Token your-token-here" http://127.0.0.1:8000/api/v1/users/profile/
```

## Структура проекта

```
Kaisen/
├── config/          # Основные настройки Django
├── users/           # Приложение управления пользователями
├── routines/        # Приложение для управления привычками
├── static/          # Статические файлы
├── docker-compose.yml
├── pyproject.toml
└── manage.py
```

## Разработка

### Линтинг
```bash
poetry run ruff check .
poetry run ruff format .
```

### Типизация
```bash
poetry run mypy .
```

### Тесты
```bash
python manage.py test
```

## Лицензия

MIT License