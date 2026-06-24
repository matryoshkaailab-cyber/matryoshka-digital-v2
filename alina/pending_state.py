#!/usr/bin/env python3.12
"""
pending_state.py — Хранение pending state между запросами для подтверждений.

Файл: /root/matryoshka/alina/state/pending.json
Формат: {"<user_id>": {"intent": ..., "entities": ..., "waiting_confirm": True, "ts": ...}}

Каждое сообщение от пользователя → проверяем есть ли pending state
Если есть и текст = "да" → выполняем action, удаляем state
Если есть и текст != "да" → отменяем (или обновляем)
Если нет → обычная обработка, после action создаём state
"""

import json
import time
from pathlib import Path

STATE_DIR = Path("/root/matryoshka/alina/state")
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = STATE_DIR / "pending.json"

# TTL для pending state (5 минут — если за 5 мин не подтвердил, сбрасываем)
TTL_SECONDS = 300


def _load() -> dict:
    """Загрузить все pending states."""
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict):
    """Сохранить pending states."""
    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _cleanup_expired(data: dict) -> dict:
    """Удалить просроченные."""
    now = time.time()
    return {
        uid: state for uid, state in data.items()
        if now - state.get("ts", 0) < TTL_SECONDS
    }


def get(user_id: str) -> dict | None:
    """Получить pending state для user_id. Возвращает None если нет или истёк."""
    data = _cleanup_expired(_load())
    return data.get(str(user_id))


def set_state(user_id: str, intent: str, entities: dict):
    """Сохранить pending state."""
    data = _cleanup_expired(_load())
    data[str(user_id)] = {
        "intent": intent,
        "entities": entities,
        "waiting_confirm": True,
        "ts": time.time(),
    }
    _save(data)


def clear(user_id: str):
    """Удалить pending state."""
    data = _load()
    data.pop(str(user_id), None)
    _save(data)


def is_confirmation(text: str) -> bool:
    """Проверяет — это подтверждение ('да', '✅', '1')?"""
    lower = text.strip().lower()
    confirm_words = {
        "да", "верно", "ок", "окей", "ага", "угу", "yes", "ok",
        "✅", "👍", "правильно", "всё так", "записывай", "подтверждаю",
        "1", "запиши", "готово", "погнали",
    }
    if lower in confirm_words:
        return True
    if any(lower.startswith(w) for w in ["да,", "верно,", "ок,", "1,"]):
        return True
    return False


def is_cancellation(text: str) -> bool:
    """Проверяет — это отмена ('нет', '❌', '2', 'отмена')?"""
    lower = text.strip().lower()
    cancel_words = {
        "нет", "отмена", "отмени", "не надо", "❌", "2", "стоп", "стой",
        "неверно", "не записывай",
    }
    if lower in cancel_words:
        return True
    if any(lower.startswith(w) for w in ["нет,", "не,", "2,"]):
        return True
    return False


def is_edit_intent(text: str) -> bool:
    """Проверяет — это правка ('поправить', '✏️', '3')?"""
    lower = text.strip().lower()
    return lower in ("поправить", "✏️", "3", "измени", "исправь", "поправь")


if __name__ == "__main__":
    # CLI test
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"

    if cmd == "show":
        data = _load()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif cmd == "clear" and len(sys.argv) > 2:
        clear(sys.argv[2])
        print(f"Cleared pending for {sys.argv[2]}")
    elif cmd == "test":
        set_state("123", "inventory.add", {"model": "iPhone 13", "storage": "128GB", "buy_price": 13500})
        print("Set test state for user 123")
        print(f"Get: {get('123')}")
    else:
        print("Usage: pending_state.py [show|clear <uid>|test]")