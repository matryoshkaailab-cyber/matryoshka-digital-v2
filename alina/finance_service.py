#!/usr/bin/env python3.12
"""
finance.py — Финансы Николая: покупки, продажи, РАСХОДЫ, реальная прибыль.
- POST /finance/expense — записать расход
- GET /finance/summary — реальная прибыль
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse
import csv

BASE = Path("/root/matryoshka/cases/nikolay/finances")
BASE.mkdir(parents=True, exist_ok=True)
PURCHASES = BASE / "purchases.csv"
SALES = BASE / "sales.csv"
EXPENSES = BASE / "expenses.csv"
LOG = "/var/log/alina_finance.log"

# Создаём файлы с заголовками
for f, headers in [
    (PURCHASES, ["date", "model", "storage", "condition", "price", "imei", "notes"]),
    (SALES, ["date", "model", "storage", "sell_price", "buy_price", "margin", "buyer", "platform"]),
    (EXPENSES, ["date", "category", "amount", "description"]),
]:
    if not f.exists():
        with open(f, "w", newline="") as fh:
            csv.writer(fh).writerow(headers)


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")


def add_expense(category, amount, description=""):
    """Записать расход"""
    with open(EXPENSES, "a", newline="") as f:
        csv.writer(f).writerow([
            datetime.now().strftime("%Y-%m-%d"),
            category,
            float(amount),
            description,
        ])
    log(f"EXPENSE: {category} {amount}₽ {description}")


def get_summary(period="today"):
    """Прибыль: доходы − расходы"""
    now = datetime.now()
    if period == "today":
        date_from = now.strftime("%Y-%m-%d")
        date_to = date_from
    elif period == "week":
        date_from = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        date_to = now.strftime("%Y-%m-%d")
    elif period == "month":
        date_from = (now - timedelta(days=30)).strftime("%Y-%m-%d")
        date_to = now.strftime("%Y-%m-%d")
    else:
        date_from = "1970-01-01"
        date_to = now.strftime("%Y-%m-%d")

    # Доходы
    income = 0
    sales_count = 0
    with open(SALES) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["date"] >= date_from and row["date"] <= date_to:
                income += float(row.get("margin", 0))
                sales_count += 1

    # Расходы
    expenses = 0
    by_cat = {}
    with open(EXPENSES) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["date"] >= date_from and row["date"] <= date_to:
                amount = float(row["amount"])
                expenses += amount
                cat = row["category"]
                by_cat[cat] = by_cat.get(cat, 0) + amount

    profit = income - expenses

    return {
        "period": period,
        "date_from": date_from,
        "date_to": date_to,
        "income": income,
        "expenses": expenses,
        "profit": profit,
        "sales_count": sales_count,
        "expenses_by_category": by_cat,
    }


def format_summary(period="today"):
    s = get_summary(period)
    period_ru = {"today": "сегодня", "week": "за неделю", "month": "за месяц"}.get(period, period)

    lines = [f"💼 ФИНАНСЫ ({period_ru}, {s['date_from']} — {s['date_to']})\n"]
    lines.append(f"💰 Доход (маржа): {s['income']:.0f}₽ ({s['sales_count']} продаж)")
    lines.append(f"💸 Расходы: {s['expenses']:.0f}₽")

    if s["expenses_by_category"]:
        lines.append(f"\n📊 Расходы по категориям:")
        for cat, amt in sorted(s["expenses_by_category"].items(), key=lambda x: -x[1]):
            lines.append(f"   • {cat}: {amt:.0f}₽")

    lines.append(f"\n✨ РЕАЛЬНАЯ ПРИБЫЛЬ: {s['profit']:.0f}₽")
    if s["profit"] < 0:
        lines.append("⚠️ УБЫТОК")
    return "\n".join(lines)


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
                "ok": True, "service": "finance",
                "endpoints": ["/finance/expense", "/finance/summary?period=today|week|month"]
            })
            return
        if self.path.startswith("/finance/summary"):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            period = qs.get("period", ["today"])[0]
            s = get_summary(period)
            self.send_json(200, {"ok": True, "summary": s, "formatted": format_summary(period)})
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

        if self.path == "/finance/expense":
            add_expense(
                data.get("category", "прочее"),
                data.get("amount", 0),
                data.get("description", ""),
            )
            self.send_json(200, {"ok": True})
            return
        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    port = 8473
    log(f"Finance service on :{port}")
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
