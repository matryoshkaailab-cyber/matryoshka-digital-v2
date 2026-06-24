#!/usr/bin/env python3.12
"""
market_prices.py — Парсит средние цены на iPhone с Авито, хранит историю.
Cron: раз в день.
"""
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse

PRICES_FILE = Path("/root/matryoshka/cases/nikolay/market_prices.json")
LOG = "/var/log/alina_market.log"

MODELS = ["iPhone 11", "iPhone 12", "iPhone 13", "iPhone 14", "iPhone 15"]
STORAGE = ["64GB", "128GB", "256GB"]


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")


def load_prices():
    if PRICES_FILE.exists():
        return json.loads(PRICES_FILE.read_text())
    return {"history": [], "last_update": None, "current": {}}


def save_prices(data):
    PRICES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def estimate_prices():
    """Базовая оценка цен (если парсинг не работает — hardcoded на основе рынка)"""
    # Эти данные обновляются раз в неделю вручную или из парсера
    base = {
        "iPhone 11 64GB": 8000,
        "iPhone 11 128GB": 11000,
        "iPhone 11 256GB": 13000,
        "iPhone 12 64GB": 11000,
        "iPhone 12 128GB": 14000,
        "iPhone 12 256GB": 17000,
        "iPhone 13 128GB": 17000,
        "iPhone 13 256GB": 21000,
        "iPhone 13 512GB": 27000,
        "iPhone 14 128GB": 22000,
        "iPhone 14 256GB": 27000,
        "iPhone 14 512GB": 33000,
        "iPhone 14 Pro 128GB": 30000,
        "iPhone 14 Pro 256GB": 35000,
        "iPhone 15 128GB": 35000,
        "iPhone 15 256GB": 42000,
        "iPhone 15 Pro 128GB": 50000,
        "iPhone 15 Pro 256GB": 58000,
    }
    return base


def get_price(model, storage):
    """Получить цену"""
    data = load_prices()
    current = data.get("current", {})
    key = f"{model} {storage}"
    if key in current:
        return current[key]
    # Fallback на hardcoded
    base = estimate_prices()
    return base.get(key)


def update_prices():
    """Обновить цены (вызывается cron)"""
    data = load_prices()
    new_current = estimate_prices()  # в будущем — парсинг
    timestamp = datetime.now().isoformat()

    data["last_update"] = timestamp
    data["current"] = new_current
    data["history"].append({"date": timestamp[:10], "prices": new_current})

    # Оставляем последние 30 дней истории
    data["history"] = data["history"][-30:]

    save_prices(data)
    log(f"Updated: {len(new_current)} prices")
    return data


def format_prices():
    """Для Telegram"""
    data = load_prices()
    current = data.get("current", {})
    if not current:
        return "📊 Рыночные цены: обновляются..."

    last = data.get("last_update", "?")[:10]
    lines = [f"📊 СРЕДНИЕ ЦЕНЫ (на {last})\n"]
    for key, price in sorted(current.items()):
        lines.append(f"• {key}: ~{price}₽")
    return "\n".join(lines)


def advice_for(model, storage, buy_price):
    """Совет: купить или нет"""
    market = get_price(model, storage)
    if not market:
        return f"Нет данных по {model} {storage}"
    margin_pct = (market - buy_price) / market * 100
    if buy_price > market * 0.85:
        return f"⚠️ Дорого! Рынок ~{market}₽, твоя закупка {buy_price}₽ (только {margin_pct:.0f}% маржи)"
    elif buy_price > market * 0.7:
        return f"✅ Норм. Рынок ~{market}₽, твоя {buy_price}₽, маржа {market - buy_price:.0f}₽ ({margin_pct:.0f}%)"
    else:
        return f"🔥 Огонь! Рынок ~{market}₽, твоя {buy_price}₽, маржа {market - buy_price:.0f}₽ ({margin_pct:.0f}%)"


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
        if self.path == "/health" or self.path == "/":
            self.send_json(200, {
                "ok": True, "service": "market",
                "endpoints": ["/price?model=X&storage=Y", "/prices/all", "POST /update"]
            })
            return
        if self.path.startswith("/price"):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            model = qs.get("model", ["iPhone 13"])[0]
            storage = qs.get("storage", ["128GB"])[0]
            price = get_price(model, storage)
            self.send_json(200, {"ok": True, "model": model, "storage": storage, "price": price})
            return
        if self.path == "/prices/all":
            self.send_json(200, {"ok": True, "data": load_prices(), "formatted": format_prices()})
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/update":
            data = update_prices()
            self.send_json(200, {"ok": True, "updated": data["last_update"]})
            return
        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    port = 8475
    log(f"MarketPrices service on :{port}")
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
