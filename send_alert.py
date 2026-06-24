#!/usr/bin/env python3
"""Отправляет алерт Олегу через Telegram bot API. Используется мониторами."""
import os
import sys
import urllib.request
import urllib.parse

# Берём токен из env
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

if not TOKEN:
    # Пробуем .env от hermes-cli и от hermes
    for env_path in ("/root/.hermes/profiles/hermes-cli/.env", "/root/.hermes/.env"):
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TELEGRAM_BOT_TOKEN="):
                        TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
            if TOKEN:
                break

OLEG_CHAT_ID = "1951845052"

if not TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN not set", file=sys.stderr)
    sys.exit(2)

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <message>", file=sys.stderr)
    sys.exit(1)

msg = " ".join(sys.argv[1:])
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = urllib.parse.urlencode({"chat_id": OLEG_CHAT_ID, "text": msg}).encode()
try:
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode()
        if '"ok":true' in body:
            print("sent")
            sys.exit(0)
        else:
            print(f"tg error: {body[:200]}", file=sys.stderr)
            sys.exit(1)
except Exception as e:
    print(f"network error: {e}", file=sys.stderr)
    sys.exit(1)
