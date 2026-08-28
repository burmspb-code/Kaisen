"""
Вспомогательные функции для настроек.
"""

import os

def get_env(name: str) -> str:
    """Возвращает значение переменной окружения, либо возбуждается ошибка валидации."""
    try:
        return os.environ[name]
    except KeyError:
        raise ValueError(f"❌Переменная окружения {name} не задана")
