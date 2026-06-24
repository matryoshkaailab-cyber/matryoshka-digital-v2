#!/usr/bin/env python3.12
"""
auto_reply.py — Автоответ на типовые вопросы покупателей Авито.
Шаблоны + ключевые слова.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse

TEMPLATES_FILE = Path("/root/matryoshka/cases/nikolay/avito_templates.json")
LOG = "/var/log/alina_autoreply.log"

DEFAULT_TEMPLATES = {
    "торг": [
        r"торг", r"сбросишь", r"дешевле", r"последняя цена", r"за сколько отдашь",
        r"за 10к возьм[её]шь", r"за \d+ ?(к|тысяч|т\.р\.)",
    ],
    "встреча": [
        r"где встреча", r"когда можно", r"самовывоз", r"встретимся",
        r"встреча", r"где посмотреть", r"можно посмотреть", r"в какое время",
    ],
    "состояние": [
        r"состояние", r"батарея", r"скрины", r"царапины", r"сколы",
        r"комплект", r"что в комплекте", r"зарядк",
    ],
    "доставка": [
        r"доставк", r"отправк", r"сдэк", r"boxberry", r"почт",
        r"в другой город", r"отправишь",
    ],
    "оригинал": [
        r"оригинал", r"не восстанов", r"не китай", r"refurbished",
        r"восстановленн", r"китайск",
    ],
    "актуальность": [
        r"актуальн", r"прода[её]тся\?", r"ещё прода", r"в наличии\?",
    ],
    "фото": [
        r"доп\.? фото", r"дополнительн.+ фото", r"скинь фото", r"пришли фото",
        r"фоток", r"есть фото", r"реальн.+ фото",
    ],
    "гарантия": [
        r"гарантия", r"проверк", r"возврат", r"если что-то не так",
    ],
    "комплектация": [
        r"комплект", r"что в коробке", r"зарядка в комплекте", r"коробк",
    ],
    "цена_итог": [
        r"итого", r"в итоге", r"всего", r"за всё",
    ],
}

REPLIES = {
    "торг": "Привет! Цена уже минимальная, но готова обсудить при встрече 🙂 Какая сумма устроит?",
    "встреча": "Привет! Могу сегодня/завтра в Краснодаре. Удобное время/место? 📍 Территориально: [район/ТЦ]",
    "состояние": "Привет! Батарея 89%, экран/корпус идеал, всё оригинал. Могу скинуть доп. фото/скрины из настроек 🔋",
    "доставка": "Привет! Отправлю СДЭК/Boxberry за твой счёт (~300₽), наложка. Авито Доставка тоже работает 📦",
    "оригинал": "Привет! 100% оригинал, не восстанов/не Китай. Проверка IMEI/серийник при встрече. Гарантия — 7 дней ✅",
    "актуальность": "Да, объявление актуально! Готов(а) к сделке 🙂",
    "фото": "Привет! Скину доп. фото сегодня вечером 📸",
    "гарантия": "Гарантия 7 дней на проверку. Если что-то не так — возврат 💯",
    "комплектация": "В комплекте: телефон + коробка + зарядка + скрепка. Без наушников (если не указано иное) 📦",
    "цена_итог": "Итоговая цена = цена в объявлении. Доставка отдельно если нужна.",
}


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")


def match_template(text):
    """Определяем категорию и возвращаем ответ"""
    text_lower = text.lower()
    matches = []
    for category, patterns in DEFAULT_TEMPLATES.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                matches.append((category, REPLIES[category]))
                break
    return matches


def get_reply(text):
    """Получить автоответ на сообщение покупателя"""
    matches = match_template(text)
    if not matches:
        return None  # не типовой — пусть Николай ответит сам

    # Если несколько категорий — берём первую
    category, reply = matches[0]
    log(f"MATCH: '{text[:50]}' → {category}")
    return {
        "category": category,
        "reply": reply,
        "all_matches": [m[0] for m in matches],
    }


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
        if self.path == "/":
            self.send_json(200, {"ok": True, "service": "auto_reply", "categories": list(REPLIES.keys())})
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else "{}"
        try:
            data = json.loads(body)
        except:
            self.send_json(400, {"error": "invalid JSON"})
            return

        if self.path == "/autoreply":
            text = data.get("text", "")
            result = get_reply(text)
            if result:
                self.send_json(200, {"ok": True, "match": result})
            else:
                self.send_json(200, {"ok": False, "reason": "no template match"})
            return
        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    port = 8474
    log(f"AutoReply service on :{port}")
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
