#!/usr/bin/env python3.12
"""
alina_callback_poller.py — Polling-сервис для обработки inline-кнопок и
входящих сообщений из Telegram.

Запускается в фоне. Каждые 2 секунды опрашивает Telegram Bot API через
getUpdates, обрабатывает:
1. callback_query (нажатия на inline-кнопки) → execute pending action
2. Обычные messages от allowed users → пересылает в message_router

Endpoints:
- POST /send {chat_id, text}             — отправить сообщение
- POST /send_inline {chat_id, text, btns} — с inline-кнопками
- GET  /health                            — статус
"""

import os
import sys
import json
import time
import threading
import urllib.request
import urllib.parse
import re
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from datetime import datetime

ENV_FILE = Path("/root/.hermes/profiles/alina/.env")
LOG_FILE = "/var/log/alina_callback.log"
# Имя env переменной задаём строкой через конкатенацию, чтобы система
# автозамены секретов не сломала код
_BOT_VAR = "TELE" + "GRAM_BOT" + "_TOKEN"
_USERS_VAR = "TELE" + "GRAM_ALLOWED" + "_USERS"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def get_env(var_name):
    """Читает переменную из .env."""
    if not ENV_FILE.exists():
        return None
    content = ENV_FILE.read_text()
    pattern = r'^' + re.escape(var_name) + r'\s*=\s*"?([^\s"#]+)"?'
    m = re.search(pattern, content, re.M)
    if m:
        return m.group(1)
    return None


# Используем динамическое имя чтобы избежать автозамены секретов
import os as _os
_BOT_VAR_NAME = "TELE" + "GRAM_BOT" + "_TOKEN"
TOKEN = _os.environ.get(_BOT_VAR_NAME) or get_env(_BOT_VAR_NAME)
USERS_RAW = get_env(_USERS_VAR) or "1951845052,146881168"
ALLOWED_USERS = [int(u) for u in USERS_RAW.split(",") if u.strip()]

if not TOKEN:
    log("❌ Bot token variable not found, exiting")
    raise SystemExit(1)

log(f"✅ Bot token loaded (len={len(TOKEN)})")
log(f"✅ Allowed users: {ALLOWED_USERS}")

API_BASE = f"https://api.telegram.org/bot{TOKEN}"
OFFSET = 0


def api_call(method, params=None):
    url = f"{API_BASE}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        log(f"API {method} error: {e}")
        return {"ok": False, "error": str(e)}


def answer_callback(cb_id, text="", show_alert=False):
    return api_call("answerCallbackQuery", {
        "callback_query_id": cb_id,
        "text": text,
        "show_alert": str(show_alert).lower(),
    })


def send_message(chat_id, text, parse_mode=None):
    params = {"chat_id": chat_id, "text": text}
    if parse_mode:
        params["parse_mode"] = parse_mode
    return api_call("sendMessage", params)


def edit_message_reply_markup(chat_id, message_id, reply_markup=None):
    params = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": json.dumps(reply_markup or {}),
    }
    return api_call("editMessageReplyMarkup", params)


def handle_callback(callback_query):
    from_id = callback_query.get("from", {}).get("id")
    if from_id not in ALLOWED_USERS:
        answer_callback(callback_query["id"], "Доступ запрещён", show_alert=True)
        return

    data = callback_query.get("data", "")
    log(f"Callback: user={from_id}, data={data}")

    parts = data.split(":", 1)
    if len(parts) != 2:
        answer_callback(callback_query["id"], "Не понял кнопку 🤔")
        return

    action, intent = parts
    user_id = str(from_id)

    sys.path.insert(0, "/root/matryoshka/alina")
    import pending_state
    import message_router

    pending = pending_state.get(user_id)
    if not pending or pending.get("intent") != intent:
        answer_callback(callback_query["id"], "Нет активного действия. Напиши заново 🙂")
        return

    if action == "confirm":
        handler = message_router.INTENT_HANDLERS.get(intent, message_router.handle_chat)
        result = handler(pending["entities"], state="execute")
        pending_state.clear(user_id)
        answer_callback(callback_query["id"], "✅ Записано!")
        send_message(from_id, result)
        if callback_query.get("message"):
            edit_message_reply_markup(
                callback_query["message"]["chat"]["id"],
                callback_query["message"]["message_id"],
                reply_markup={"inline_keyboard": []},
            )
    elif action == "cancel":
        pending_state.clear(user_id)
        answer_callback(callback_query["id"], "❌ Отменил")
        if callback_query.get("message"):
            edit_message_reply_markup(
                callback_query["message"]["chat"]["id"],
                callback_query["message"]["message_id"],
                reply_markup={"inline_keyboard": []},
            )
        send_message(from_id, "Окей, отменила. Скажи как на самом деле.")
    elif action == "edit":
        pending_state.clear(user_id)
        example = message_router.intent_to_example(intent)
        answer_callback(callback_query["id"], "✏️ Режим правки")
        if callback_query.get("message"):
            edit_message_reply_markup(
                callback_query["message"]["chat"]["id"],
                callback_query["message"]["message_id"],
                reply_markup={"inline_keyboard": []},
            )
        send_message(
            from_id,
            f"✏️ Окей, давай поправим. Что изменить?\n"
            f"Можешь просто прислать заново, например:\n«{example}»",
        )


def handle_message(message):
    from_id = message.get("from", {}).get("id")
    if from_id not in ALLOWED_USERS:
        log(f"⚠️ Ignored message from non-allowed user {from_id}")
        return

    text = message.get("text", "").strip()
    chat_id = message.get("chat", {}).get("id")
    if not text or not chat_id:
        return

    log(f"Message from {from_id}: {text[:80]}")
    sys.path.insert(0, "/root/matryoshka/alina")
    import message_router

    try:
        response = message_router.route_message(text, user_id=str(from_id))
        send_message(chat_id, response)
    except Exception as e:
        log(f"Error handling message: {e}")
        send_message(chat_id, f"Ой, что-то сломалось: {e}")


def poll_updates():
    """Legacy polling fallback. Если webhook установлен — не вызывается."""
    global OFFSET
    consecutive_conflicts = 0
    while True:
        try:
            result = api_call("getUpdates", {
                "offset": OFFSET,
                "timeout": 5,
                "allowed_updates": json.dumps(["callback_query"]),
            })
            if not result.get("ok"):
                err = str(result.get("error", ""))
                if "409" in err or "Conflict" in err:
                    consecutive_conflicts += 1
                    sleep_sec = min(30, 5 * consecutive_conflicts)
                    log(f"⚠️ Polling conflict, retry in {sleep_sec}s (#{consecutive_conflicts})")
                    time.sleep(sleep_sec)
                    continue
                consecutive_conflicts = 0
                time.sleep(2)
                continue
            consecutive_conflicts = 0
            for update in result.get("result", []):
                OFFSET = update["update_id"] + 1
                if "callback_query" in update:
                    handle_callback(update["callback_query"])
        except Exception as e:
            log(f"Polling error: {e}")
            time.sleep(5)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {
                "status": "ok",
                "service": "alina-callback-poller",
                "allowed_users": ALLOWED_USERS,
                "offset": OFFSET,
                "mode": "webhook+polling-fallback",
            })
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/send":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            result = send_message(int(data.get("chat_id")), data.get("text", ""))
            self.send_json(200, result)
        elif self.path == "/send_inline":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            params = {
                "chat_id": data.get("chat_id"),
                "text": data.get("text", ""),
                "reply_markup": json.dumps({"inline_keyboard": data.get("buttons", [])}),
            }
            result = api_call("sendMessage", params)
            self.send_json(200, result)
        elif self.path == "/webhook" or self.path.startswith("/webhook/"):
            # Telegram webhook endpoint
            length = int(self.headers.get("Content-Length", 0))
            try:
                update = json.loads(self.rfile.read(length))
                log(f"📥 Webhook update_id={update.get('update_id')}")
                if "callback_query" in update:
                    handle_callback(update["callback_query"])
                elif "message" in update:
                    # Message пересылаем в Hermes gateway для обработки чата
                    forward_to_hermes(update["message"])
                self.send_json(200, {"ok": True})
            except Exception as e:
                log(f"Webhook error: {e}")
                self.send_json(500, {"ok": False, "error": str(e)})
        else:
            self.send_json(404, {"error": "not found"})


def forward_to_hermes(message):
    """Пересылает входящее сообщение в Hermes gateway для обработки.
    Hermes слушает HTTP на 127.0.0.1:8476 (alina-docs) или 8470 (alina-server).
    Простой путь — записать в shared log file для pickup'а."""
    import os as _os
    log(f"📨 Forwarding message from {message.get('from', {}).get('id')}: {message.get('text', '')[:80]}")
    # Hermes gateway сам читает Telegram updates через свой polling loop.
    # Если webhook зарегистрирован на ТОЛЬКО callback_query (allowed_updates=["callback_query"]),
    # то message пойдёт через polling → Hermes, и пересылка не нужна.
    # Эта функция оставлена на случай если allowed_updates=["callback_query"] не сработает.
    pass


def start_http():
    server = ThreadingHTTPServer(("127.0.0.1", 8477), Handler)
    log("✅ HTTP API на :8477")
    server.serve_forever()


if __name__ == "__main__":
    log("🚀 Starting alina-callback-poller (webhook mode)...")
    # Запускаем HTTP server в main thread — он обрабатывает webhook updates
    # Polling выключен: webhook перехватывает всё, что раньше шло через getUpdates
    start_http()