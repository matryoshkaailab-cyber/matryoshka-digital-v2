#!/usr/bin/env python3.12
"""
telegram_inline.py — Отправка сообщений с inline-кнопками через Telegram Bot API.

Позволяет message_router отправлять сообщения с настоящими кнопками
в Telegram, которые Николай может тапнуть вместо ввода текста.

Использование:
  from telegram_inline import send_with_buttons
  send_with_buttons(chat_id=123, text="...", buttons=[
    [{"text": "✅ Да", "callback_data": "confirm"}],
    [{"text": "❌ Нет", "callback_data": "cancel"}]
  ])
"""

import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

ENV_FILE = Path("/root/.hermes/profiles/alina/.env")


def get_bot_token() -> str:
    """Читает TELEGRAM_BOT_TOKEN из .env."""
    if not ENV_FILE.exists():
        return None
    import re
    content = ENV_FILE.read_text()
    m = re.search(r'^TELEGRAM_BOT_TOKEN\s*=\s*"?([^\s"#]+)"?', content, re.M)
    if m:
        return m.group(1)
    return None


def get_chat_id() -> str:
    """Читает TELEGRAM_HOME_CHANNEL из .env (chat_id Николая)."""
    if not ENV_FILE.exists():
        return None
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("TELEGRAM_HOME_CHANNEL="):
            val = line.split("=", 1)[1].strip()
            if val:
                return val
    return None


def send_with_buttons(text: str, buttons: list, chat_id: str = None, parse_mode: str = None) -> dict:
    """
    Отправить сообщение в Telegram с inline-кнопками.

    Args:
        text: текст сообщения
        buttons: [[{text, callback_data}, ...], ...] — массив рядов кнопок
        chat_id: ID чата (по умолчанию — из .env)
        parse_mode: "Markdown", "HTML" или None

    Returns:
        dict от Telegram API {ok, result: {...}}
    """
    token = get_bot_token()
    if not token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN не найден"}

    chat_id = chat_id or get_chat_id()
    if not chat_id:
        return {"ok": False, "error": "TELEGRAM_HOME_CHANNEL не найден"}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": json.dumps({"inline_keyboard": buttons}),
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def send_confirmation_buttons(summary: str, intent: str, chat_id: str = None) -> dict:
    """Шлёт summary с тремя inline-кнопками: ✅ Да / ❌ Нет / ✏️ Поправить."""
    buttons = [
        [
            {"text": "✅ Да, записать", "callback_data": f"confirm:{intent}"},
            {"text": "❌ Нет", "callback_data": f"cancel:{intent}"},
        ],
        [
            {"text": "✏️ Поправить", "callback_data": f"edit:{intent}"},
        ],
    ]
    return send_with_buttons(summary, buttons, chat_id)


def answer_callback(callback_query_id: str, text: str = "", show_alert: bool = False) -> dict:
    """Ответить на callback query (после нажатия кнопки)."""
    token = get_bot_token()
    if not token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN не найден"}

    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert,
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    # Test
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "test"

    if cmd == "test":
        result = send_with_buttons(
            "Тест inline-кнопок:\n\nЕсли видишь кнопки ниже — работает! 🎉",
            [
                [{"text": "✅ Да", "callback_data": "confirm:test"}],
                [{"text": "❌ Нет", "callback_data": "cancel:test"}],
            ]
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif cmd == "confirm":
        summary = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Тест"
        result = send_confirmation_buttons(summary, "inventory.add")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: telegram_inline.py [test|confirm <text>]")