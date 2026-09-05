# ==============================================================================
# Этап 1: Сборка зависимостей (Builder)
# ==============================================================================
FROM python:3.14-rc-slim AS builder

# ==============================================================================
# НАСТРОЙКИ PYTHON И POETRY (ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ)
# ==============================================================================
# PYTHONUNBUFFERED=1           -> Отключает буферизацию вывода (логи в реальном времени)
# PYTHONDONTWRITEBYTECODE=1    -> Запрещает создавать папки __pycache__ и файлы .pyc
# POETRY_VERSION=2.2.1         -> Фиксируем версию Poetry
# POETRY_VIRTUALENVS_IN_PROJECT=true -> Создавать виртуальное окружение .venv внутри проекта
# POETRY_NO_INTERACTION=1      -> Отключает интерактивные вопросы при сборке
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_HTTP_TIMEOUT=120

# ==============================================================================
# УСТАНОВКА СИСТЕМНЫХ ЗАВИСИМОСТЕЙ LINUX (СБОРКА В ОДИН СЛОЙ)
# ==============================================================================
# apt-get update             -> Обновляем списки доступных пакетов
# --no-install-recommends    -> Ставим только строго обязательные пакеты (без мусора)
# -y                         -> Автоматически отвечать "Да" на все вопросы
# build-essential            -> Набор компиляторов (GCC, G++, make) для сборки пакетов на C
# libpq-dev                  -> Заголовочные файлы для работы с PostgreSQL (нужны для psycopg2)
# rm -rf ...                 -> Очищаем скачанные индексы пакетов, чтобы уменьшить вес слоя
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry 2.x в Docker через pipx/pip
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Устанавливаем рабочую директорию
WORKDIR /code

# Копируем только файлы зависимостей, чтобы Docker кешировал этот слой
COPY poetry.lock pyproject.toml ./

# Устанавливаем зависимости проекта (виртуальное окружение создастся прямо в папке /code/.venv)
# --only main - Устанавливает библиотеки только из основной группы (main) проекта
# Убран флаг --no-root, чтобы Poetry 2.x корректно сгенерировал бинарник celery
RUN poetry install --only main


# ==============================================================================
# Этап 2: Финальный образ для запуска приложения (Runner)
# ==============================================================================
FROM python:3.14-rc-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Пробрасываем путь к бинарникам виртуального окружения в PATH.
# Теперь команды python, manage.py, celery будут автоматически браться из окружения Poetry.
ENV PATH="/code/.venv/bin:$PATH"

# Устанавливаем легкую системную библиотеку, необходимую PostgreSQL на продакшене
RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Переносим готовое виртуальное окружение со всеми библиотеками из этапа сборки
COPY --from=builder /code/.venv /code/.venv

# Копируем исходный код текущего Django-проекта
COPY . .

EXPOSE 8000
