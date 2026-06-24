#!/usr/bin/env python3.12
"""
morning_brief.py — Утренняя сводка для Николая (09:00 daily).

Собирает: остатки на складе, вчерашние продажи, рыночные цены, новые лоты.
Отправляет в Telegram @NikolaAlinaBot.
"""
import os
import sys
import json
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta
from telegram import Bot  # python-telegram-bot


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
NICHOLAS_CHAT_ID = 146881168


def get_inventory_summary() -> str:
    """Склад — сколько iPhone, на какую сумму."""
    inv_file = Path("/root/matryoshka/cases/nikolay/finances/inventory.json")
    if not inv_file.exists():
        return "📦 Склад: данных нет"
    try:
        data = json.loads(inv_file.read_text())
        in_stock = [x for x in data if x.get("status") == "in_stock"]
        n = len(in_stock)
        total_cost = sum(x.get("buy_price", 0) for x in in_stock)
        return f"📦 На складе: {n} шт на {total_cost:,.0f}₽"
    except Exception:
        return "📦 Склад: ошибка чтения"


def get_yesterday_sales() -> str:
    """Продажи вчера."""
    sales_file = Path("/root/matryoshka/cases/nikolay/finances/sales.csv")
    if not sales_file.exists():
        return "💰 Вчера продаж не было"
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        lines = sales_file.read_text().splitlines()[1:]  # skip header
        total = 0
        count = 0
        for line in lines:
            if line.startswith(yesterday):
                parts = line.split(",")
                if len(parts) >= 4:
                    try:
                        total += float(parts[3])
                        count += 1
                    except (ValueError, IndexError):
                        pass
        if count:
            return f"💰 Вчера: {count} продаж на {total:,.0f}₽"
        return "💰 Вчера: продаж не было"
    except Exception:
        return "💰 Ошибка чтения sales.csv"


def get_market_avg() -> str:
    """Средняя цена топ-3 моделей."""
    mp_file = Path("/root/matryoshka/cases/nikolay/market_prices.json")
    if not mp_file.exists():
        return "📊 Цены: нет данных"
    try:
        data = json.loads(mp_file.read_text())
        current = data.get("current", {})
        top_models = ["iPhone 13 128GB", "iPhone 14 128GB", "iPhone 15 128GB"]
        lines = []
        for m in top_models:
            if m in current:
                lines.append(f"  • {m}: {current[m]:,}₽")
        return "📊 Рынок:\n" + "\n".join(lines)
    except Exception:
        return "📊 Ошибка market_prices"


def get_new_lots() -> str:
    """Новые лоты с Avito (последний файл)."""
    avito_dir = Path("/root/matryoshka/cases/nikolay/avito_lots")
    files = sorted(avito_dir.glob("iphone_lots_*.json"))
    if not files:
        return "🔍 Парсер: нет данных"
    try:
        data = json.loads(files[-1].read_text())
        return f"🔍 Лотов на Avito: {len(data)} (топ-3 в Telegram)"
    except Exception:
        return "🔍 Ошибка чтения"


def compose_brief() -> str:
    """Собирает утреннюю сводку."""
    today = datetime.now().strftime("%d.%m.%Y")
    parts = [
        f"☀️ Доброе утро, Коля! {today}",
        "",
        get_inventory_summary(),
        get_yesterday_sales(),
        get_market_avg(),
        get_new_lots(),
        "",
        "💪 Хорошего дня! /help — все команды"
    ]
    return "\n".join(parts)


def send_telegram(text: str) -> bool:
    """Отправляет в Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": NICHOLAS_CHAT_ID, "text": text, "parse_mode": "HTML"}
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"❌ Telegram send fail: {e}")
        return False


if __name__ == "__main__":
    brief = compose_brief()
    print(brief)
    print()
    if "--send" in sys.argv:
        if send_telegram(brief):
            print("✅ Sent to Nicholas")
        else:
            print("❌ Send failed")
