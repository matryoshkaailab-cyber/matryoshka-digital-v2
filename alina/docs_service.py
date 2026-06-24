#!/usr/bin/env python3.12
"""
docs.py — Генерация документов (расписка о приёме, договор купли-продажи).
"""
import json
from datetime import datetime
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse

DOCS_DIR = Path("/root/matryoshka/cases/nikolay/documents")
DOCS_DIR.mkdir(parents=True, exist_ok=True)
LOG = "/var/log/alina_docs.log"


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")


def generate_receipt(model, storage, imei, price, seller="Варнаков Н.А.", buyer=""):
    """Расписка о приёме"""
    date = datetime.now().strftime("%d.%m.%Y")
    buyer_name = buyer if buyer else "_______________"
    imei_text = imei if imei else "_______________"
    doc = (
        "РАСПИСКА О ПРИЁМЕ\n"
        f"от {date}\n\n"
        f"Продавец: {seller}\n"
        f"Покупатель: {buyer_name}\n\n"
        f"Товар: {model} {storage}\n"
        f"IMEI: {imei_text}\n"
        f"Сумма: {price} руб.\n\n"
        "Продавец передал, Покупатель принял указанный товар.\n"
        "Товар проверен, претензий нет.\n\n"
        f"Продавец: _______________/{seller}/\n"
        f"Покупатель: _______________/{buyer_name}/\n\n"
        f"Дата: {date}\n"
    )
    fname = DOCS_DIR / f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    fname.write_text(doc, encoding="utf-8")
    log(f"RECEIPT: {fname}")
    return str(fname)


def generate_contract(model, storage, imei, price, seller="Варнаков Н.А.", buyer=""):
    """Договор купли-продажи"""
    date = datetime.now().strftime("%d.%m.%Y")
    buyer_name = buyer if buyer else "_______________"
    imei_text = imei if imei else "_______________"
    doc = (
        "ДОГОВОР КУПЛИ-ПРОДАЖИ\n"
        f"№ {datetime.now().strftime('%Y%m%d%H%M%S')} от {date}\n\n"
        f"Продавец: {seller}, паспорт: _______________\n"
        f"Покупатель: {buyer_name}, паспорт: _______________\n\n"
        f"Предмет: {model} {storage}\n"
        f"IMEI/Серийный номер: {imei_text}\n"
        f"Стоимость: {price} (_______________) руб.\n\n"
        "Условия:\n"
        "1. Продавец гарантирует, что товар не заложен, не в розыске.\n"
        "2. Покупатель проверил товар и согласен с состоянием.\n"
        "3. Гарантия — 7 дней с момента передачи.\n"
        "4. Споры решаются по закону РФ.\n\n"
        f"Продавец: _______________/{seller}/\n"
        f"Покупатель: _______________/{buyer_name}/\n\n"
        f"Дата: {date}\n"
    )
    fname = DOCS_DIR / f"contract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    fname.write_text(doc, encoding="utf-8")
    log(f"CONTRACT: {fname}")
    return str(fname)


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
            self.send_json(200, {"ok": True, "service": "docs", "endpoints": ["/receipt", "/contract"]})
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

        if self.path == "/receipt":
            f = generate_receipt(
                data.get("model", "iPhone"),
                data.get("storage", "128GB"),
                data.get("imei", ""),
                data.get("price", 0),
                data.get("seller", "Варнаков Н.А."),
                data.get("buyer", ""),
            )
            self.send_json(200, {"ok": True, "file": f})
            return
        if self.path == "/contract":
            f = generate_contract(
                data.get("model", "iPhone"),
                data.get("storage", "128GB"),
                data.get("imei", ""),
                data.get("price", 0),
                data.get("seller", "Варнаков Н.А."),
                data.get("buyer", ""),
            )
            self.send_json(200, {"ok": True, "file": f})
            return
        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    port = 8476
    log(f"Docs service on :{port}")
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
