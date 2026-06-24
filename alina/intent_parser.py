#!/usr/bin/env python3.12
"""
intent_parser.py — Парсер намерений из свободной речи Николая.

Гибридный подход:
1. Сначала rule-based (regex + словари) — быстро, дёшево, для простых фраз
2. Если не сработало — LLM (через alina_server) для сложных случаев

Возвращает JSON:
{
  "intent": "inventory.add" | "inventory.sell" | ...,
  "entities": {...},
  "confidence": 0.0-1.0,
  "missing": ["model", "price"],  # что не хватает для действия
  "source": "rules" | "llm"
}
"""

import re
import json
import urllib.request
import base64
from pathlib import Path
from typing import Optional

# === СЛОВАРИ СИНОНИМОВ ===

INTENT_KEYWORDS = {
    "inventory.add": [
        r"\b(купил|купить|взял|приобрёл|приобрёл|затарился)\b",
    ],
    "inventory.sell": [
        r"\b(продал|продать|отдал|уш[её]л|реализовал)\b",
    ],
    "inventory.writeoff": [
        r"\b(списал|убил|утопил|разбил|треснул)\b",
    ],
    "inventory.show": [
        r"\b(что (у меня )?на складе|сколько (на складе|айфонов)|остаток|инвентарь|в наличии|покажи склад|что есть)\b",
        r"^\s*(склад|остатки?)\s*$",
    ],
    "finance.expense": [
        r"\b(потратил|истратил|у?шло|оплатил|заправился|пообедал|заплатил|сходил в)\b",
    ],
    "finance.profit": [
        r"\b(сколько заработал|прибыл|маржа|чистыми|в плюс|что по прибыли|по деньгам)\b",
    ],
    "finance.report": [
        r"\b(от[чё]?[её]т|отчёт|сводк[аи]|итог[иа])\b",
    ],
    "market.price": [
        r"\b(сколько стоит|по[ -]?ч[её]м|рыночн[ая]? цена|средн[яя] цена|почём)\b",
    ],
    "market.parse": [
        r"\b(найди|поищи|спарси|парс[а-я]*|что есть на авито)\b",
    ],
    "docs.receipt": [
        r"\b(расписк[аиу]|напиши расписку)\b",
    ],
    "docs.contract": [
        r"\b(договор[ау]?|оформи договор)\b",
    ],
    "help": [
        r"\b(не понимаю|что делать|помоги|команды|как пользоваться)\b",
    ],
}

CONDITION_WORDS = {
    "идеал": "идеал", "новый": "идеал", "запечатан": "идеал", "в плёнке": "идеал",
    "отличное": "хорошее", "отличн": "хорошее", "хорошее": "хорошее", "хорош": "хорошее",
    "норм": "хорошее", "нормальное": "хорошее",
    "б/у": "б/у", "бу": "б/у", "поношенн": "б/у", "царапины": "б/у",
    "следы": "б/у", "потерт": "б/у",
    "убит": "ремонт", "убитый": "ремонт", "ремонт": "ремонт", "требует ремонта": "ремонт",
}

EXPENSE_CATEGORIES = {
    "бензин": ["бензин", "заправ", "азс", "топлив", "залить"],
    "еда": ["обед", "пообедал", "кафе", "ресторан", "кофе", "покушал", "еда", "продукт", "магазин"],
    "аренда": ["аренда", "квартир", "коммунал", "свет", "газ", "ипотек"],
    "реклама": ["реклам", "авито", "продвижен", "промо"],
    "телефон": ["телефон", "связь", "мобильн", "сим", "тариф"],
    "транспорт": ["такси", "метро", "автобус", "маршрутк", "бензин", "поездк"],
}

PERIOD_WORDS = {
    "today": ["сегодня", "за день", "за сегодня"],
    "yesterday": ["вчера"],
    "week": ["недел", "на неделе", "за неделю", "эт[аой] недел"],
    "month": ["месяц", "в месяце", "за месяц", "эт[оа]т месяц"],
    "year": ["год", "за год"],
    "all": ["вс[её]", "итого", "всего"],
}

ID_WORDS = {
    "first": "1", "перв": "1", "первый": "1",
    "second": "2", "втор": "2",
    "third": "3", "трет": "3",
    "fourth": "4", "четвёрт": "4", "четверт": "4",
    "fifth": "5", "пят": "5",
    "sixth": "6", "шест": "6",
    "seventh": "7", "седьм": "7",
    "eighth": "8", "восьм": "8",
    "ninth": "9", "девят": "9",
    "tenth": "10", "десят": "10",
    "last": "last", "последн": "last",
}


# === RULE-BASED PARSER ===

def extract_model(text: str) -> Optional[str]:
    """Извлекает модель iPhone: 'iPhone 13', '13 Pro Max', 'айфон 14 плюс', '12-ый', '13 айфон'."""
    # Полная форма: iPhone 13 Pro Max
    m = re.search(r"\b(iPhone|айфон|айф|iphone)\s*(\d{1,2})\s*(Pro\s*Max|Pro|Plus|mini)?\b", text, re.I)
    if m:
        prefix = "iPhone"
        num = m.group(2)
        suffix = m.group(3) or ""
        return f"{prefix} {num} {suffix}".strip()
    # Сокращённая с суффиксом: '13 Pro', '14 плюс'
    m = re.search(r"\b(\d{1,2})\s*(Pro\s*Max|Pro Max|Pro|Plus|плюс|мини)\b", text, re.I)
    if m:
        num = m.group(1)
        suffix = m.group(2).replace("плюс", "Plus").replace("мини", "mini").replace(" ", " ")
        return f"iPhone {num} {suffix}".strip()
    # Просто число с окончанием: '12-ый', '13-й', '14ая', '13 айфон'
    m = re.search(r"\b(\d{1,2})[\s-]*(ый|ой|ая|я|ая|й)\s*(айфон|iphone|iPhone)?\b", text, re.I)
    if m:
        num = m.group(1)
        return f"iPhone {num}"
    # 'айфон 14' / 'айфон 13'
    m = re.search(r"\b(айфон)\s*(\d{1,2})\b", text, re.I)
    if m:
        return f"iPhone {m.group(2)}"
    return None


def extract_storage(text: str) -> Optional[str]:
    """Извлекает память: 128GB, 256 ГБ, 512 гб."""
    m = re.search(r"(\d{2,4})\s*(ГБ|Гб|гб|GB|Gb|gb)", text)
    if m:
        return f"{m.group(1)}GB"
    # Число перед "память"
    m = re.search(r"(\d{2,4})\s*(памят)", text, re.I)
    if m:
        return f"{m.group(1)}GB"
    return None


def extract_price(text: str) -> Optional[float]:
    """Извлекает цену: 'за 13 500', 'за 13,500', 'за 13500', 'на 600', 'по 600', '13к', '18к руб'."""
    # '13к' / '13к руб' = 13000
    m = re.search(r"\b(\d{1,3})\s*[кkKК]\b", text)
    if m:
        return float(m.group(1)) * 1000
    # 'за 13 500' / 'за 13,500' / 'за 13.500' / 'за 13500' / 'за 13тыс'
    m = re.search(
        r"(?:за|на|по)\s+(\d{1,3}(?:[\s\u00a0.,]\d{3}){1,3}|\d{4,7})(?:\s*тыс|\s*т\.|тысяч)?",
        text, re.I
    )
    if m:
        price_str = m.group(1).replace(" ", "").replace("\u00a0", "").replace(".", "").replace(",", "")
        try:
            return float(price_str)
        except ValueError:
            pass
    # Просто большие числа 4+ знаков (fallback для контекста без предлога)
    nums = re.findall(r"\b(\d{4,7})\b", text)
    if nums:
        return float(nums[0])
    # 'на 600' / 'по 600' как последний шанс (3-значные)
    m = re.search(r"(?:на|по)\s+(\d{2,3})\b", text)
    if m:
        return float(m.group(1))
    return None


def extract_condition(text: str) -> Optional[str]:
    """Извлекает состояние."""
    lower = text.lower()
    for word, norm in CONDITION_WORDS.items():
        if word in lower:
            return norm
    return None


def extract_expense_category(text: str) -> Optional[str]:
    """Извлекает категорию расхода."""
    lower = text.lower()
    for category, keywords in EXPENSE_CATEGORIES.items():
        for kw in keywords:
            if kw in lower:
                return category
    return None


def extract_period(text: str) -> str:
    """Извлекает период (today/week/month/...)."""
    lower = text.lower()
    for period, keywords in PERIOD_WORDS.items():
        for kw in keywords:
            if kw in lower:
                return period
    return "today"


def extract_id(text: str) -> Optional[str]:
    """Извлекает ID лота: 'пятый', '5', '#5'."""
    # '#5', 'id 5'
    m = re.search(r"(?:#|id)\s*(\d{1,3})", text, re.I)
    if m:
        return m.group(1)
    # Число после "продал/списал"
    m = re.search(r"(?:продал|списал)\s*(\d{1,3})", text, re.I)
    if m:
        return m.group(1)
    # Порядковое числительное
    lower = text.lower()
    for word, num in ID_WORDS.items():
        if re.search(rf"\b{word}\w*\b", lower):
            return num
    return None


def extract_buyer(text: str) -> str:
    """Извлекает имя покупателя (после 'Ивану', 'Сергею' и т.д.)."""
    # 'Ивану', 'Сергею', 'Иваном'
    m = re.search(r"(?:продал|отдал)\s+(?:\d+\s+)?([А-ЯЁ][а-яё]{2,}(?:у|ом|ой|е)?)", text)
    if m:
        return m.group(1).rstrip("уомей")
    return ""


def detect_intent(text: str) -> Optional[str]:
    """Определяет intent по ключевым словам. Возвращает None если неясно."""
    lower = text.lower()
    # Приоритет: более специфичные сначала
    priority = [
        "help", "docs.receipt", "docs.contract",
        "market.parse", "market.price",
        "finance.report", "finance.profit",
        "inventory.show", "inventory.writeoff",
        "inventory.sell", "inventory.add",
        "finance.expense",
    ]
    for intent in priority:
        patterns = INTENT_KEYWORDS.get(intent, [])
        for pat in patterns:
            if re.search(pat, lower):
                return intent
    return None


def parse_by_rules(text: str) -> Optional[dict]:
    """Парсит через правила. Возвращает dict или None."""
    intent = detect_intent(text)
    if not intent:
        return None

    entities = {}
    confidence = 0.7  # базовая уверенность для rule-based

    if intent == "inventory.add":
        entities["model"] = extract_model(text)
        entities["storage"] = extract_storage(text)
        entities["buy_price"] = extract_price(text)
        entities["condition"] = extract_condition(text) or "б/у"

        # Уточняем confidence по полноте
        if entities["model"] and entities["storage"] and entities["buy_price"]:
            confidence = 0.95
        elif entities["model"] and entities["buy_price"]:
            confidence = 0.8

    elif intent == "inventory.sell":
        entities["id"] = extract_id(text)
        entities["sell_price"] = extract_price(text)
        entities["buyer"] = extract_buyer(text)

        if entities["id"] and entities["sell_price"]:
            confidence = 0.95
        elif entities["sell_price"]:
            confidence = 0.75

    elif intent == "inventory.writeoff":
        entities["id"] = extract_id(text)
        entities["reason"] = re.sub(r"^(списал|убил|утопил|разбил|треснул)\s*\d*\s*", "", text, flags=re.I).strip()
        if entities["id"]:
            confidence = 0.9

    elif intent == "inventory.show":
        confidence = 0.95

    elif intent == "finance.expense":
        entities["amount"] = extract_price(text)
        entities["category"] = extract_expense_category(text) or "прочее"
        entities["description"] = text.strip()

        if entities["amount"]:
            confidence = 0.9

    elif intent == "finance.profit":
        entities["period"] = extract_period(text)
        confidence = 0.95

    elif intent == "finance.report":
        entities["period"] = extract_period(text)
        confidence = 0.95

    elif intent == "market.price":
        entities["model"] = extract_model(text)
        entities["storage"] = extract_storage(text)
        if entities["model"] and entities["storage"]:
            confidence = 0.9
        elif entities["model"]:
            confidence = 0.7

    elif intent == "market.parse":
        entities["query"] = extract_model(text) or text
        confidence = 0.8

    elif intent == "docs.receipt":
        entities["model"] = extract_model(text)
        entities["storage"] = extract_storage(text)
        entities["price"] = extract_price(text)
        if entities["model"] and entities["storage"] and entities["price"]:
            confidence = 0.9

    elif intent == "docs.contract":
        entities["model"] = extract_model(text)
        entities["storage"] = extract_storage(text)
        entities["price"] = extract_price(text)
        if entities["model"] and entities["storage"] and entities["price"]:
            confidence = 0.9

    elif intent == "help":
        confidence = 0.95

    # Считаем missing entities
    required = {
        "inventory.add": ["model", "storage", "buy_price"],
        "inventory.sell": ["id", "sell_price"],
        "inventory.writeoff": ["id"],
        "inventory.show": [],
        "finance.expense": ["amount", "category"],
        "finance.profit": ["period"],
        "finance.report": ["period"],
        "market.price": ["model", "storage"],
        "market.parse": ["query"],
        "docs.receipt": ["model", "storage", "price"],
        "docs.contract": ["model", "storage", "price"],
        "help": [],
    }.get(intent, [])

    missing = [k for k in required if not entities.get(k)]

    return {
        "intent": intent,
        "entities": entities,
        "confidence": confidence,
        "missing": missing,
        "source": "rules",
    }


# === LLM FALLBACK ===

SYSTEM_PROMPT = """Ты — парсер намерений для Telegram-бота Алины (напарник Николая, бизнес iPhone в Краснодаре).

Твоя задача: получить фразу Николая на русском → вернуть JSON с intent и entities.

Допустимые intent:
- inventory.add: Николай КУПИЛ iPhone/XKIN (купил/взял/приобрёл/затарился)
- inventory.sell: Николай ПРОДАЛ iPhone (продал/отдал/ушёл)
- inventory.writeoff: списал/сломал/утопил
- inventory.show: что на складе/остаток
- finance.expense: расход (потратил/заправился/пообедал)
- finance.profit: сколько заработал/прибыль
- finance.report: отчёт/сводка
- market.price: сколько стоит/рыночная цена
- market.parse: найди лоты/спарси
- docs.receipt: расписка
- docs.contract: договор
- chat: всё остальное (просто общение)

Entities для inventory.add: {model: "iPhone 13 Pro Max", storage: "256GB", buy_price: 13500, condition: "идеал"|"хорошее"|"б/у"|"ремонт"}
Entities для inventory.sell: {id: 5, sell_price: 17500, buyer: "Иван"}
Entities для finance.expense: {amount: 500, category: "бензин"|"еда"|"аренда"|"реклама"|"телефон"|"транспорт"|"прочее", description: "заправка"}
Entities для finance.profit: {period: "today"|"week"|"month"}
Entities для market.price: {model: "iPhone 13", storage: "128GB"}

ПРАВИЛА:
1. Если не понял — верни intent="chat", confidence=0.3
2. Если понял intent но данных мало — confidence=0.6, missing перечисли
3. Если всё ясно — confidence=0.95
4. Цена — всегда число в рублях (без пробелов, "к" = *1000)
5. Память — формат "128GB"

Верни ТОЛЬКО валидный JSON, без пояснений. Пример:
{"intent":"inventory.add","entities":{"model":"iPhone 13","storage":"128GB","buy_price":13500,"condition":"б/у"},"confidence":0.95,"missing":[]}
"""


def parse_by_llm(text: str, alina_api_url: str = "http://localhost:8470") -> Optional[dict]:
    """Парсит через LLM. Возвращает dict или None."""
    prompt = f'Фраза Николая: "{text}"\n\nВерни JSON с intent, entities, confidence, missing.'
    # Читаем auth из .env (Basic auth: alina:UUID)
    import base64
    auth_header = None
    env_file = Path("/root/.hermes/profiles/alina/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("ALINA_API_UUID="):
                uuid_val = line.split("=", 1)[1].strip()
                token = base64.b64encode(f"alina:{uuid_val}".encode()).decode()
                auth_header = f"Basic {token}"
                break
    try:
        headers = {"Content-Type": "application/json"}
        if auth_header:
            headers["Authorization"] = auth_header
        req = urllib.request.Request(
            f"{alina_api_url}/think",
            data=json.dumps({"prompt": prompt, "system": SYSTEM_PROMPT, "max_tokens": 400, "temperature": 0.1}).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
            raw = resp.get("text") or resp.get("response") or ""
            # Ищем JSON в ответе
            json_match = re.search(r"\{[\s\S]*\}", raw)
            if json_match:
                result = json.loads(json_match.group(0))
                result["source"] = "llm"
                # Добавляем missing если его нет
                if "missing" not in result:
                    required = {
                        "inventory.add": ["model", "storage", "buy_price"],
                        "inventory.sell": ["id", "sell_price"],
                        "inventory.writeoff": ["id"],
                        "finance.expense": ["amount", "category"],
                        "finance.profit": ["period"],
                        "market.price": ["model", "storage"],
                        "docs.receipt": ["model", "storage", "price"],
                        "docs.contract": ["model", "storage", "price"],
                    }.get(result.get("intent"), [])
                    result["missing"] = [k for k in required if not result.get("entities", {}).get(k)]
                return result
    except Exception as e:
        print(f"LLM parse error: {e}")
    return None


# === MAIN ENTRY ===

def parse_intent(text: str, use_llm: bool = True) -> dict:
    """
    Главная функция. Парсит фразу → intent.

    Returns:
    {
      "intent": str,
      "entities": dict,
      "confidence": float,
      "missing": [str],
      "source": "rules" | "llm"
    }
    """
    text = text.strip()
    if not text:
        return {"intent": "chat", "entities": {}, "confidence": 0.0, "missing": [], "source": "rules"}

    # 1. Правила
    rule_result = parse_by_rules(text)
    if rule_result and rule_result["confidence"] >= 0.85:
        return rule_result

    # 2. LLM fallback
    if use_llm:
        llm_result = parse_by_llm(text)
        if llm_result and llm_result.get("intent") and llm_result["intent"] != "chat":
            return llm_result

    # 3. Fallback: правила с низкой уверенностью или chat
    if rule_result:
        return rule_result
    return {"intent": "chat", "entities": {"text": text}, "confidence": 0.3, "missing": [], "source": "rules"}


if __name__ == "__main__":
    # CLI test
    import sys
    test_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "купил iPhone 13 за 13500"
    result = parse_intent(test_text, use_llm=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))