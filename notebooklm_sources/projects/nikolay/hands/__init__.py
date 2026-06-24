"""
hands/__init__.py — реестр инструментов Алины
"""

# Stage 1 инструменты (готовятся)
try:
    from .yandex.parser import parse_yandex_avito
    HANDS_AVAILABLE = {
        "yandex_fallback": {
            "function": parse_yandex_avito,
            "description": "Поиск лотов через Yandex (когда Avito парсер не работает)",
            "triggers": ["найди", "ищи", "покажи лоты", "что есть на авито"],
            "args": {"query": "str", "max_price": "int", "city": "str"}
        }
    }
except ImportError:
    HANDS_AVAILABLE = {}


def list_hands() -> list[str]:
    """Вернуть список доступных инструментов."""
    return list(HANDS_AVAILABLE.keys())


def get_hand(name: str):
    """Получить инструмент по имени."""
    return HANDS_AVAILABLE.get(name)
