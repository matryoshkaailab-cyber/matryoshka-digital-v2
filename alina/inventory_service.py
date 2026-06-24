#!/usr/bin/env python3.12
"""
inventory.py — Учёт iPhone в наличии у Николая.
- Запись: добавить/продать/списать
- Хранение: JSON (просто, надёжно)
- API: GET /api/inventory (список)
- Telegram: /stock /inv /склад
"""
import json
import os
from datetime import datetime
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse

INVENTORY_FILE = Path("/root/matryoshka/cases/nikolay/finances/inventory.json")
INVENTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
SALES_CSV = Path("/root/matryoshka/cases/nikolay/finances/sales.csv")
SALES_CSV.parent.mkdir(parents=True, exist_ok=True)
LOG = "/var/log/alina_inventory.log"

if not INVENTORY_FILE.exists():
    INVENTORY_FILE.write_text("[]")


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[inventory] {msg}", flush=True)


def load_inventory():
    return json.loads(INVENTORY_FILE.read_text())


def save_inventory(items):
    INVENTORY_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2))


def add_item(model, storage, condition, buy_price, imei=None, notes=None):
    """Добавить iPhone на склад"""
    items = load_inventory()
    item = {
        "id": len(items) + 1,
        "model": model,           # "iPhone 13"
        "storage": storage,       # "128GB"
        "condition": condition,   # "новый"/"б/у"/"идеал"/"следы"
        "buy_price": float(buy_price),
        "buy_date": datetime.now().strftime("%Y-%m-%d"),
        "imei": imei or "",
        "notes": notes or "",
        "status": "in_stock",     # in_stock / sold / reserved / broken
    }
    items.append(item)
    save_inventory(items)
    log(f"ADD: {model} {storage} {condition} за {buy_price}₽")
    return item


def sell_item(item_id, sell_price, buyer=None):
    """Продать iPhone — обновляет inventory И sales.csv"""
    items = load_inventory()
    for item in items:
        if item.get("id") == item_id and item.get("status") == "in_stock":
            item["status"] = "sold"
            item["sell_price"] = float(sell_price)
            item["sell_date"] = datetime.now().strftime("%Y-%m-%d")
            item["buyer"] = buyer or ""
            item["margin"] = float(sell_price) - float(item.get("buy_price", 0))
            save_inventory(items)
            log(f"SELL: #{item_id} {item['model']} за {sell_price}₽ (маржа {item['margin']:.0f}₽)")
            # Также пишем в sales.csv для finance
            try:
                import csv
                with open(SALES_CSV, "a", newline="") as f:
                    csv.writer(f).writerow([
                        item["sell_date"],
                        item.get("model", ""),
                        item.get("storage", ""),
                        float(sell_price),
                        float(item.get("buy_price", 0)),
                        item["margin"],
                        buyer or "",
                        "avito",
                    ])
            except Exception as e:
                log(f"ERR write sales.csv: {e}")
            return item
    return None


def writeoff_item(item_id, reason):
    """Списать iPhone (украли, сломался, etc)"""
    items = load_inventory()
    for item in items:
        if item.get("id") == item_id and item.get("status") == "in_stock":
            item["status"] = "written_off"
            item["writeoff_reason"] = reason
            item["writeoff_date"] = datetime.now().strftime("%Y-%m-%d")
            save_inventory(items)
            log(f"WRITEOFF: #{item_id} причина: {reason}")
            return item
    return None


def get_inventory(filter_status="in_stock"):
    """Получить список"""
    items = load_inventory()
    if filter_status == "all":
        return items
    return [i for i in items if i.get("status") == filter_status]


def summarize():
    """Сводка для Telegram"""
    items = get_inventory("in_stock")
    if not items:
        return "📦 Склад пуст 🤷"

    lines = [f"📦 СКЛАД: {len(items)} шт в наличии\n"]
    total_cost = 0
    by_model = {}
    for i in items:
        key = f"{i.get('model', '?')} {i.get('storage', '?')}"
        if key not in by_model:
            by_model[key] = []
        by_model[key].append(i)
        total_cost += i.get("buy_price", 0)

    for model, group in sorted(by_model.items()):
        prices = [g.get("buy_price", 0) for g in group]
        avg = sum(prices) / len(prices)
        lines.append(f"• {model} — {len(group)} шт, средн.закуп {avg:.0f}₽")
    lines.append(f"\n💰 Заморожено: {total_cost:.0f}₽")
    return "\n".join(lines)


# === HTTP API ===

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
        if self.path.startswith("/inventory"):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            status = qs.get("status", ["in_stock"])[0]
            items = get_inventory(status)
            self.send_json(200, {"ok": True, "count": len(items), "items": items, "summary": summarize()})
            return
        if self.path == "/":
            self.send_json(200, {"ok": True, "service": "inventory", "summary": summarize()})
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

        if self.path == "/inventory/add":
            item = add_item(
                data.get("model", "?"),
                data.get("storage", "?"),
                data.get("condition", "б/у"),
                data.get("buy_price", 0),
                data.get("imei"),
                data.get("notes"),
            )
            self.send_json(200, {"ok": True, "item": item})
            return

        if self.path == "/inventory/sell":
            result = sell_item(
                data.get("id", 0),
                data.get("sell_price", 0),
                data.get("buyer"),
            )
            if result:
                self.send_json(200, {"ok": True, "item": result})
            else:
                self.send_json(404, {"ok": False, "error": "item not found or already sold"})
            return

        if self.path == "/inventory/writeoff":
            result = writeoff_item(data.get("id", 0), data.get("reason", ""))
            if result:
                self.send_json(200, {"ok": True, "item": result})
            else:
                self.send_json(404, {"ok": False, "error": "item not found or already written off"})
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    port = 8472
    log(f"Inventory service on :{port}")
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
