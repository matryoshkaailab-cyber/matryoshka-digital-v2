#!/usr/bin/env python3.12
"""
inactivity_alert.py — Алерты если Николай не заходил N дней.

Cron: 0 21 * * * (каждый вечер 21:00)
Проверяет last activity Nicholas (последнее сообщение в state.db alina-gateway).
"""
import os
import sqlite3
import time
import urllib.request
import json
from datetime import datetime, timedelta


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
NICHOLAS_CHAT_ID = 146881168
ALINA_PROFILE = "/root/.hermes/profiles/alina/state.db"
INACTIVITY_DAYS = 3


def get_nicholas_last_active() -> int:
    """Возвращает unix timestamp последней активности Николая (таблица sessions, user_id)."""
    if not os.path.exists(ALINA_PROFILE):
        return 0
    try:
        conn = sqlite3.connect(ALINA_PROFILE)
        c = conn.cursor()
        # Nicholas = user_id 146881168 (string)
        c.execute("""SELECT MAX(started_at) FROM sessions
                     WHERE user_id=? AND source='telegram'""", (str(NICHOLAS_CHAT_ID),))
        row = c.fetchone()
        result = row[0] if row else 0
        conn.close()
        return result or 0
    except Exception as e:
        print(f"inactivity query err: {e}")
        return 0


def send_alert(days_inactive: int) -> bool:
    """Отправляет алерт Олегу если Николай молчит."""
    if not TELEGRAM_BOT_TOKEN:
        return False
    text = (
        f"⚠️ Николай не заходил {days_inactive} дней.\n"
        f"Может стоит написать ему проверить Алину?\n"
        f"@NikolaAlinaBot"
    )
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": 1951845052, "text": text}  # Олег
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    last_ts = get_nicholas_last_active()
    if last_ts == 0:
        print("Не удалось получить данные")
        exit(1)

    now = int(time.time())
    days_inactive = (now - last_ts) // 86400
    print(f"Last active: {days_inactive} days ago")

    if days_inactive >= INACTIVITY_DAYS:
        if send_alert(days_inactive):
            print(f"✅ Alert sent ({days_inactive} days)")
        else:
            print("❌ Alert send failed")
    else:
        print("OK — активен")
