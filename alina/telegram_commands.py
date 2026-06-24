#!/usr/bin/env python3.12
"""
telegram_commands.py — Обработчик команд Telegram для Алины.
Запускается как subprocess от gateway когда Николай шлёт команду.

Команды:
  /stock /inv /склад — показать склад
  /купить {model} {storage} {price} — добавить на склад
  /продал {id} {sell_price} — продать со склада
  /списать {id} {причина} — списать
  /расход {category} {amount} [description] — записать расход
  /прибыль [today/week/month] — реальная прибыль
  /цена {model} {storage} — рыночная цена
  /документ расписка|договор {model} {storage} {price} — сгенерить
  /автоответ {text} — проверить автоответ
"""
import sys
import json
import urllib.request
from pathlib import Path
from datetime import datetime

# Endpoints
ENDPOINTS = {
    "inventory": "http://localhost:8472",
    "finance": "http://localhost:8473",
    "autoreply": "http://localhost:8474",
    "market": "http://localhost:8475",
    "docs": "http://localhost:8476",
}


def http_post(url, data):
    req = urllib.request.Request(
        url, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def http_get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read())


def handle_command(text):
    """Обработать команду, вернуть текст ответа"""
    parts = text.strip().split()
    if not parts:
        return "Пустая команда"

    cmd = parts[0].lower().lstrip("/")

    # === СКЛАД ===
    if cmd in ("stock", "inv", "склад", "наличие"):
        r = http_get(f"{ENDPOINTS['inventory']}/inventory?status=in_stock")
        return r.get("summary", "Ошибка склада")

    if cmd in ("купил", "купить", "add"):
        # /купил {модель с пробелами} {память} {цена} [состояние]
        # Последние 1-2 слова — цена и опционально состояние
        if len(parts) < 3:
            return "❓ Использование: /купил iPhone 13 128GB 13500 [состояние]"
        # Проверяем: последнее = состояние?
        condition_words = ("идеал", "новый", "б/у", "хорошее", "следы", "убит")
        if parts[-1] in condition_words and len(parts) >= 4:
            condition = parts[-1]
            price_str = parts[-2]
            model_parts = parts[1:-2]
        else:
            condition = "б/у"
            price_str = parts[-1]
            model_parts = parts[1:-1]
        try:
            price = float(price_str)
        except:
            return f"❓ Цена '{price_str}' должна быть числом"
        if len(model_parts) < 2:
            return "❓ Укажи модель и память: /купил iPhone 13 128GB 13500"
        storage = model_parts[-1]
        model = " ".join(model_parts[:-1])
        r = http_post(f"{ENDPOINTS['inventory']}/inventory/add", {
            "model": model, "storage": storage, "condition": condition, "buy_price": price
        })
        if r.get("ok"):
            item = r["item"]
            return f"✅ Добавлено: #{item['id']} {model} {storage} {condition} за {price}₽"
        return f"❌ Ошибка: {r}"

    if cmd in ("продал", "sell"):
        if len(parts) < 3:
            return "❓ Использование: /продал 5 17500 [buyer]"
        try:
            item_id = int(parts[1])
            price = float(parts[2])
        except:
            return "❓ id и цена — числа"
        buyer = " ".join(parts[3:]) if len(parts) > 3 else ""
        r = http_post(f"{ENDPOINTS['inventory']}/inventory/sell", {
            "id": item_id, "sell_price": price, "buyer": buyer
        })
        if r.get("ok"):
            item = r["item"]
            return f"✅ Продано: #{item_id} {item['model']} {item['storage']} за {price}₽ (маржа {item['margin']:.0f}₽)"
        return f"❌ {r.get('error', 'Ошибка')}"

    if cmd in ("списал", "списать", "writeoff"):
        if len(parts) < 2:
            return "❓ Использование: /списал 5 причина"
        try:
            item_id = int(parts[1])
        except:
            return "❓ id — число"
        reason = " ".join(parts[2:]) or "не указана"
        r = http_post(f"{ENDPOINTS['inventory']}/inventory/writeoff", {
            "id": item_id, "reason": reason
        })
        if r.get("ok"):
            return f"✅ Списано: #{item_id} ({reason})"
        return f"❌ {r.get('error', 'Ошибка')}"

    # === ФИНАНСЫ ===
    if cmd in ("расход", "expense"):
        if len(parts) < 3:
            return "❓ Использование: /расход бензин 500 заправка"
        category = parts[1]
        try:
            amount = float(parts[2])
        except:
            return "❓ Сумма — число"
        desc = " ".join(parts[3:])
        http_post(f"{ENDPOINTS['finance']}/finance/expense", {
            "category": category, "amount": amount, "description": desc
        })
        return f"✅ Расход: {category} {amount}₽ {desc}"

    if cmd in ("прибыль", "profit", "отчёт"):
        period = parts[1] if len(parts) > 1 and parts[1] in ("today", "week", "month") else "today"
        r = http_get(f"{ENDPOINTS['finance']}/finance/summary?period={period}")
        return r.get("formatted", "Ошибка")

    # === РЫНОК ===
    if cmd in ("цена", "price", "market"):
        if len(parts) < 3:
            return "❓ Использование: /цена iPhone 13 128GB"
        storage = parts[-1]
        model = " ".join(parts[1:-1])
        # URL-encode
        from urllib.parse import quote
        url = f"{ENDPOINTS['market']}/price?model={quote(model)}&storage={quote(storage)}"
        r = http_get(url)
        if r.get("price"):
            return f"📊 {model} {storage}: ~{r['price']}₽ (рынок Краснодар)"
        return f"Нет данных по {model} {storage}"

    # === ДОКУМЕНТЫ ===
    if cmd in ("документ", "doc", "док"):
        if len(parts) < 4:
            return "❓ Использование: /документ расписка iPhone 13 128GB 17500"
        doc_type = parts[1]
        try:
            price = float(parts[-1])
        except:
            return "❓ Цена — число (последний аргумент)"
        # Модель и память — между типом и ценой
        model_parts = parts[2:-1]
        if len(model_parts) < 2:
            return "❓ Нужна модель и память"
        storage = model_parts[-1]
        model = " ".join(model_parts[:-1])

        if doc_type in ("расписка", "receipt"):
            endpoint = "/receipt"
        elif doc_type in ("договор", "contract"):
            endpoint = "/contract"
        else:
            return f"❓ Тип: расписка или договор"

        r = http_post(f"{ENDPOINTS['docs']}{endpoint}", {
            "model": model, "storage": storage, "price": price
        })
        if r.get("ok"):
            return f"✅ Документ создан: {r['file']}"
        return f"❌ {r}"

    # === АВТООТВЕТ ===
    if cmd in ("автоответ", "autoreply", "testreply"):
        text = " ".join(parts[1:])
        r = http_post(f"{ENDPOINTS['autoreply']}/autoreply", {"text": text})
        if r.get("ok"):
            m = r["match"]
            return f"✅ Категория: {m['category']}\n💬 Ответ: {m['reply']}"
        return "❌ Нет шаблона — ответь сам"

    return "Пиши как удобно — пойму."


if __name__ == "__main__":
    # Режимы:
    #  python3.12 telegram_commands.py "купил iPhone 13 за 13500"     → /-команда или свободная речь (auto-detect)
    #  python3.12 telegram_commands.py --free "купил iPhone 13 за 13500" → принудительно свободная речь (через NLU)
    #  python3.12 telegram_commands.py --confirm "да" --user-id 123     → подтверждение pending action для user_id
    #  python3.12 telegram_commands.py --pending-show                  → показать все pending state (debug)
    #  python3.12 telegram_commands.py --pending-clear 123             → очистить pending для user_id
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--free", action="store_true", help="Принудительно режим свободной речи (NLU)")
    parser.add_argument("--confirm", action="store_true", help="Подтверждение pending action")
    parser.add_argument("--user-id", default="default", help="Telegram user_id для pending state")
    parser.add_argument("--pending-show", action="store_true", help="Показать все pending states (debug)")
    parser.add_argument("--pending-clear", metavar="USER_ID", help="Очистить pending для user_id")
    parser.add_argument("text", nargs="*", help="Текст сообщения")
    args = parser.parse_args()

    # Debug команды для pending state
    if args.pending_show:
        from pending_state import _load
        import json as _json
        print(_json.dumps(_load(), ensure_ascii=False, indent=2))
        sys.exit(0)
    if args.pending_clear:
        from pending_state import clear
        clear(args.pending_clear)
        print(f"✅ Cleared pending for {args.pending_clear}")
        sys.exit(0)

    if args.text:
        text = " ".join(args.text)
    else:
        text = sys.stdin.read().strip()

    if args.confirm:
        # Подтверждение pending state для конкретного user_id
        from message_router import route_message
        print(route_message(text, user_id=args.user_id))
    elif args.free or not text.startswith("/"):
        # Свободная речь → NLU
        from message_router import route_message
        print(route_message(text, user_id=args.user_id))
    else:
        # /-команда → старая логика
        print(handle_command(text))
