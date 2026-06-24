#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
alex_telegram_bot.py — мост Telegram ↔ opencode на ПК Олега
Запускает opencode на каждое сообщение от Олега, шлёт ответ в Telegram.

Зависимости:
  pip install pyTelegramBotAPI

Запуск:
  python alex_telegram_bot.py
  # или через NSSM/Task Scheduler как сервис AlexTelegramBot
"""
import os
import sys
import time
import subprocess
import telebot
from telebot import apihelper

# === КОНФИГУРАЦИЯ ===
TELEGRAM_BOT_TOKEN = os.environ.get("ALEX_TELEGRAM_TOKEN", "PASTE_TOKEN_HERE")
ALLOWED_USER_ID = 1951845052  # Олег
OPENCODE_BIN = os.environ.get("OPENCODE_BIN", "opencode")  # или полный путь
WORK_DIR = os.environ.get("OPENCODE_WORKDIR", r"C:\matryoshka")
TIMEOUT_SEC = 180
LOG_FILE = os.path.join(os.path.dirname(__file__), "alex_telegram_bot.log")


def log(msg: str):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def call_opencode(prompt: str) -> str:
    """Вызывает opencode run с заданным prompt, возвращает stdout/stderr."""
    log(f"opencode run: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    try:
        result = subprocess.run(
            [OPENCODE_BIN, "run", prompt],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SEC,
            encoding="utf-8",
            errors="replace",
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        if result.returncode == 0 and out:
            return out
        if out and err:
            return f"{out}\n\n[stderr]\n{err}"
        return out or err or f"[opencode exited with code {result.returncode}, no output]"
    except subprocess.TimeoutExpired:
        return f"[timeout after {TIMEOUT_SEC}s]"
    except FileNotFoundError:
        return f"[opencode not found at: {OPENCODE_BIN}]"
    except Exception as e:
        return f"[error: {e}]"


# === TELEGRAM BOT ===
if TELEGRAM_BOT_TOKEN == "PASTE_TOKEN_HERE":
    log("❌ Set ALEX_TELEGRAM_TOKEN env var or edit TELEGRAM_BOT_TOKEN")
    sys.exit(1)

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=True)


@bot.message_handler(commands=["start", "help"])
def cmd_start(msg):
    if msg.from_user.id != ALLOWED_USER_ID:
        return
    bot.reply_to(
        msg,
        "✅ Аликс-бот активен. Я — opencode на твоём ПК.\n\n"
        "Пиши задачу текстом, я выполню через `opencode run` и пришлю ответ.\n"
        f"Workdir: {WORK_DIR}\n"
        f"opencode: {OPENCODE_BIN}\n"
        f"Timeout: {TIMEOUT_SEC}s",
    )


@bot.message_handler(func=lambda m: m.from_user.id == ALLOWED_USER_ID, content_types=["text"])
def handle_text(msg):
    prompt = msg.text or ""
    if not prompt.strip():
        return
    log(f"TG <- {msg.from_user.id}: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    try:
        bot.send_chat_action(msg.chat.id, "typing")
    except Exception:
        pass
    response = call_opencode(prompt)
    if len(response) > 4000:
        response = response[:4000] + "\n\n[truncated]"
    try:
        bot.reply_to(msg, response)
        log(f"TG -> {msg.from_user.id}: {len(response)} chars")
    except Exception as e:
        log(f"send error: {e}")


if __name__ == "__main__":
    log(f"=== AlexTelegramBot started ===")
    log(f"Workdir: {WORK_DIR}")
    log(f"opencode: {OPENCODE_BIN}")
    log(f"Allowed user: {ALLOWED_USER_ID}")
    log(f"Polling Telegram...")
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=20)
    except KeyboardInterrupt:
        log("stopped by KeyboardInterrupt")
    except Exception as e:
        log(f"FATAL: {e}")
        sys.exit(1)
