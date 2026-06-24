#!/usr/bin/env python3.12
"""
message_router.py — Диспетчер сообщений для Telegram-бота Алины.

Маршрутизация:
1. Сообщения начинающиеся с / → handle_command() (telegram_commands.py)
2. Свободная речь → parse_intent() → execute_intent() → подтверждение/уточнение
3. Всё остальное → chat (обычное общение с моделью)

Подтверждения:
- Перед записью в склад/финансы показывает summary
- Если entities неполные — задаёт уточняющие вопросы
- Если intent неясен — просит /help
"""

import sys
import json
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import intent_parser
import telegram_commands
import pending_state

ENDPOINTS = telegram_commands.ENDPOINTS


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


# === HANDLERS по intent ===

def handle_inventory_add(entities: dict, state: str = "pending") -> str:
    """Покупка iPhone. State: pending (первый раз), confirm (подтверждение), execute (запись)."""
    if state == "execute":
        r = http_post(f"{ENDPOINTS['inventory']}/inventory/add", {
            "model": entities["model"],
            "storage": entities["storage"],
            "condition": entities.get("condition", "б/у"),
            "buy_price": entities["buy_price"],
        })
        if r.get("ok"):
            item = r["item"]
            return (
                f"✅ Записано в склад:\n"
                f"• #{item['id']} {entities['model']} {entities['storage']}\n"
                f"• Состояние: {entities.get('condition', 'б/у')}\n"
                f"• Цена покупки: {entities['buy_price']}₽\n"
                f"Маржу узнаем при продаже 🙂"
            )
        return f"❌ Ошибка записи: {r.get('error', r)}"

    # pending или confirm → показать summary и попросить подтверждения
    summary = (
        f"📦 Покупка:\n"
        f"• Модель: {entities.get('model', '?')}\n"
        f"• Память: {entities.get('storage', '?')}\n"
        f"• Цена: {entities.get('buy_price', '?')}₽\n"
        f"• Состояние: {entities.get('condition', 'б/у')}\n\n"
        f"Всё верно? Скажи «да» — запишу, или поправь."
    )
    return summary


def handle_inventory_sell(entities: dict, state: str = "pending") -> str:
    if state == "execute":
        r = http_post(f"{ENDPOINTS['inventory']}/inventory/sell", {
            "id": int(entities["id"]) if entities["id"] != "last" else -1,
            "sell_price": entities["sell_price"],
            "buyer": entities.get("buyer", ""),
        })
        if r.get("ok"):
            item = r["item"]
            return (
                f"✅ Продано:\n"
                f"• #{item['id']} {item['model']} {item['storage']}\n"
                f"• Цена: {entities['sell_price']}₽\n"
                f"• Маржа: {item['margin']:.0f}₽\n"
                f"💪 Молодец!"
            )
        return f"❌ {r.get('error', r)}"
    summary = (
        f"💰 Продажа:\n"
        f"• ID лота: {entities.get('id', '?')}\n"
        f"• Цена: {entities.get('sell_price', '?')}₽\n"
        f"• Покупатель: {entities.get('buyer', 'не указан')}\n\n"
        f"Подтверди — запишу."
    )
    return summary


def handle_inventory_writeoff(entities: dict, state: str = "pending") -> str:
    if state == "execute":
        r = http_post(f"{ENDPOINTS['inventory']}/inventory/writeoff", {
            "id": int(entities["id"]),
            "reason": entities.get("reason", "не указана"),
        })
        if r.get("ok"):
            return f"✅ Списано #{entities['id']}: {entities.get('reason', '')}"
        return f"❌ {r.get('error', r)}"
    return (
        f"🗑 Списание:\n"
        f"• ID: {entities.get('id', '?')}\n"
        f"• Причина: {entities.get('reason', 'не указана')}\n\n"
        f"Подтверди."
    )


def handle_inventory_show(entities: dict, state: str = "pending") -> str:
    r = http_get(f"{ENDPOINTS['inventory']}/inventory?status=in_stock")
    return r.get("summary", "Склад пуст или ошибка")


def handle_finance_expense(entities: dict, state: str = "pending") -> str:
    if state == "execute":
        http_post(f"{ENDPOINTS['finance']}/finance/expense", {
            "category": entities.get("category", "прочее"),
            "amount": entities["amount"],
            "description": entities.get("description", ""),
        })
        return f"✅ Расход записан: {entities.get('category')} {entities['amount']}₽"
    return (
        f"💸 Расход:\n"
        f"• Категория: {entities.get('category', 'прочее')}\n"
        f"• Сумма: {entities.get('amount', '?')}₽\n\n"
        f"Верно?"
    )


def handle_finance_profit(entities: dict, state: str = "pending") -> str:
    period = entities.get("period", "today")
    r = http_get(f"{ENDPOINTS['finance']}/finance/summary?period={period}")
    return r.get("formatted", "Ошибка подсчёта прибыли")


def handle_finance_report(entities: dict, state: str = "pending") -> str:
    period = entities.get("period", "today")
    r = http_get(f"{ENDPOINTS['finance']}/finance/summary?period={period}")
    return f"📊 Отчёт ({period}):\n\n{r.get('formatted', 'Ошибка')}"


def handle_market_price(entities: dict, state: str = "pending") -> str:
    from urllib.parse import quote
    model = entities.get("model", "")
    storage = entities.get("storage", "")
    if not model or not storage:
        return "Укажи модель и память. Пример: «по чём iPhone 13 128?»"
    url = f"{ENDPOINTS['market']}/price?model={quote(model)}&storage={quote(storage)}"
    r = http_get(url)
    if r.get("price"):
        return f"📊 {model} {storage}: ~{r['price']}₽ (Краснодар, рыночная)"
    return f"Нет данных по {model} {storage}"


def handle_market_parse(entities: dict, state: str = "pending") -> str:
    """Запускает парсер Avito. Возвращает топ-10."""
    query = entities.get("query", "iPhone")
    # Используем быстрый парсер
    import subprocess
    script = "/tmp/avito_quick.py"
    try:
        # Patch query в скрипте (быстрый способ — subprocess с переменной)
        env_override = f"PARSE_QUERY={query}"
        result = subprocess.run(
            ["python3", script],
            capture_output=True, text=True, timeout=180,
            env={"PARSE_QUERY": query, "PATH": "/usr/bin:/usr/local/bin"}
        )
        # Берём последние 50 строк (там топ-10)
        output = result.stdout.strip().split("\n")
        top10_lines = [l for l in output if l.strip()][:50]
        return "🍎 Топ-10 с Авито (Краснодар):\n\n" + "\n".join(top10_lines)
    except subprocess.TimeoutExpired:
        return "⏱ Парсер долго думает. Попробуй позже."
    except Exception as e:
        return f"❌ Ошибка парсера: {e}"


def handle_docs_receipt(entities: dict, state: str = "pending") -> str:
    if state == "execute":
        r = http_post(f"{ENDPOINTS['docs']}/receipt", {
            "model": entities["model"], "storage": entities["storage"], "price": entities["price"]
        })
        return f"✅ Расписка создана: {r.get('file', '?')}"
    return (
        f"📄 Расписка на:\n"
        f"• {entities.get('model', '?')} {entities.get('storage', '?')}\n"
        f"• Цена: {entities.get('price', '?')}₽\n\n"
        f"Создать?"
    )


def handle_docs_contract(entities: dict, state: str = "pending") -> str:
    if state == "execute":
        r = http_post(f"{ENDPOINTS['docs']}/contract", {
            "model": entities["model"], "storage": entities["storage"], "price": entities["price"]
        })
        return f"✅ Договор создан: {r.get('file', '?')}"
    return (
        f"📄 Договор на:\n"
        f"• {entities.get('model', '?')} {entities.get('storage', '?')}\n"
        f"• Цена: {entities.get('price', '?')}₽\n\n"
        f"Оформить?"
    )


def handle_help(entities: dict, state: str = "pending") -> str:
    return "Пиши как удобно — пойму."


def handle_chat(entities: dict, state: str = "pending") -> str:
    """Обычное общение — вызывает LLM через alina_server."""
    try:
        req = urllib.request.Request(
            "http://localhost:8470/chat",
            data=json.dumps({"message": entities.get("text", ""), "mode": "simple"}).encode(),
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
            return resp.get("text") or resp.get("response") or "Что-то я задумалась 🙂"
    except Exception as e:
        return f"Привет! Извини, кажется у меня связь барахлит. Скажи ещё раз?"


INTENT_HANDLERS = {
    "inventory.add": handle_inventory_add,
    "inventory.sell": handle_inventory_sell,
    "inventory.writeoff": handle_inventory_writeoff,
    "inventory.show": handle_inventory_show,
    "finance.expense": handle_finance_expense,
    "finance.profit": handle_finance_profit,
    "finance.report": handle_finance_report,
    "market.price": handle_market_price,
    "market.parse": handle_market_parse,
    "docs.receipt": handle_docs_receipt,
    "docs.contract": handle_docs_contract,
    "help": handle_help,
    "chat": handle_chat,
}


# === ПОДТВЕРЖДЕНИЯ (state machine) ===
# Импорт из pending_state.py


def intent_to_example(intent: str) -> str:
    """Пример фразы для данного intent."""
    return {
        "inventory.add": "купил iPhone 13 128GB за 13500 идеал",
        "inventory.sell": "продал пятый за 17500",
        "inventory.writeoff": "списал 3 треснул экран",
        "finance.expense": "потратил 500 на бензин",
        "docs.receipt": "расписка iPhone 13 128GB 17500",
        "docs.contract": "договор iPhone 13 128GB 17500",
    }.get(intent, "что нужно сделать")


def build_inline_keyboard(intent: str, user_id: str) -> str:
    """Текстовая имитация inline-кнопок (для будущего расширения)."""
    return (
        "\n\n"
        "[1] ✅ Да, записать\n"
        "[2] ❌ Нет, отменить\n"
        "[3] ✏️ Поправить\n\n"
        "Просто напиши «да», «нет» или «поправить» — или номер."
    )


# === MAIN ROUTER ===

def route_message(text: str, user_id: str = "default") -> str:
    """
    Главная точка входа.

    user_id: ID пользователя Telegram (для pending state).
    """
    text = text.strip()
    if not text:
        return "Скажи что-нибудь 🙂"

    # 1. Проверяем pending state
    pending = pending_state.get(user_id)

    if pending and pending.get("waiting_confirm"):
        if pending_state.is_confirmation(text):
            # Подтверждение → выполняем
            intent = pending["intent"]
            entities = pending["entities"]
            handler = INTENT_HANDLERS.get(intent, handle_chat)
            pending_state.clear(user_id)
            return handler(entities, state="execute")
        elif pending_state.is_cancellation(text):
            # Отмена
            pending_state.clear(user_id)
            return "Окей, отменила. Скажи как на самом деле."
        elif pending_state.is_edit_intent(text):
            # Правка — переходим в режим edit, обнуляем pending
            intent = pending["intent"]
            pending_state.clear(user_id)
            return (
                f"✏️ Окей, давай поправим. Что изменить?\n"
                f"Можешь просто прислать заново, например: "
                f"«{intent_to_example(intent)}»"
            )
        # Если текст содержит новые данные (модель/цена) — обновим pending
        # Например: "нет, iPhone 14 не 13" → можно перепарсить
        # Для простоты: считаем это новой командой (обработаем ниже)

    # 2. /-команды → старая логика
    if text.startswith("/"):
        return telegram_commands.handle_command(text)

    # 3. Парсим свободную речь
    parsed = intent_parser.parse_intent(text, use_llm=True)
    intent = parsed.get("intent")
    entities = parsed.get("entities", {})
    confidence = parsed.get("confidence", 0.0)
    missing = parsed.get("missing", [])

    # 4. Не поняли — chat
    if intent == "chat" or confidence < 0.5:
        return handle_chat(entities)

    handler = INTENT_HANDLERS.get(intent, handle_chat)

    # 5. Не хватает данных — задаём вопросы
    if missing:
        questions = {
            "model": "Какая модель? (например, iPhone 13 Pro Max)",
            "storage": "Сколько памяти? (128GB, 256GB...)",
            "buy_price": "За сколько купил? (например, 13500 или «13 500»)",
            "sell_price": "За сколько продал?",
            "id": "Какой ID лота? (скажи /stock чтобы узнать)",
            "amount": "Сколько потратил? (числом)",
            "category": "На что потратил? (бензин/еда/аренда/реклама...)",
            "period": "За какой период? (сегодня/неделя/месяц)",
            "price": "Укажи цену",
            "query": "Что искать на Авито?",
        }
        q = questions.get(missing[0], f"Уточни {missing[0]}")
        return f"🤔 Почти поняла! {q}"

    # 6. Для записи — показать summary и сохранить pending state
    if intent in ("inventory.add", "inventory.sell", "inventory.writeoff",
                   "finance.expense", "docs.receipt", "docs.contract"):
        pending_state.set_state(user_id, intent, entities)
        summary = handler(entities, state="pending")
        keyboard = build_inline_keyboard(intent, user_id)
        return f"{summary}{keyboard}"

    # 7. Для запросов — сразу выдаём
    return handler(entities, state="execute")


if __name__ == "__main__":
    import sys
    test_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "купил iPhone 13 за 13500"
    result = route_message(test_text)
    print(result)