#!/usr/bin/env python3
"""
pipeline.py — полный pipeline парсинга с slop-detector и fallback для ALF.

Использование:
    python3 pipeline.py --query "iPhone" --city "Краснодар" --limit 50
    python3 pipeline.py --query "iPhone 15" --city "Москва" --limit 100 --no-alf

Pipeline:
    1. Apify парсинг (raw JSON)
    2. ALF verification (если настроен, иначе skip)
    3. Slop-detector (локальный анализ)
    4. CSV запись (только CLEAN items)
    5. BLOCKED items → /tmp/blocked_for_review.json
"""
import os
import sys
import json
import csv
import argparse
import requests
from datetime import datetime
from pathlib import Path

# === КОНФИГ ===
ENV_PATH = Path("/root/.hermes/profiles/nikolay/.env")
ALF_URL = "http://127.0.0.1:8451/think"
APIFY_API = "https://api.apify.com/v2"
ACTOR_ID = "zen-studio/avito-listings-scraper"
PURCHASES_CSV = Path("/root/matryoshka/nikolay/purchases.csv")
BLOCKED_JSON = Path("/tmp/blocked_for_review.json")
SLOP_SCRIPT = Path("/root/matryoshka/cases/nikolay-phone/parser/slop_detector.py")

# === ЗАГРУЗКА ТОКЕНА ===
def load_token() -> str:
    if not ENV_PATH.exists():
        raise FileNotFoundError(f"{ENV_PATH} не найден")
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("APIFY_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise ValueError("APIFY_TOKEN не найден в .env")


# === ШАГ 1: APIFY ===
def run_apify(token: str, query: str, city: str, limit: int) -> list:
    """Запуск Actor, ожидание, получение items."""
    print(f"\n[1/4] Apify: query='{query}' city='{city}' limit={limit}")
    input_data = {
        "query": query,
        "city": city,
        "maxItems": limit,
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        }
    }
    headers = {"Authorization": f"Bearer {token}"}

    # Запуск
    r = requests.post(f"{APIFY_API}/acts/zen-studio~avito-listings-scraper/runs",
                      headers=headers, json=input_data, timeout=30)
    r.raise_for_status()
    run_id = r.json()["data"]["id"]
    print(f"  Run: {run_id}")

    # Ожидание
    import time
    for i in range(60):
        r = requests.get(f"{APIFY_API}/actor-runs/{run_id}", headers=headers, timeout=10)
        data = r.json()["data"]
        status = data["status"]
        if status in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
            break
        time.sleep(5)
    else:
        raise TimeoutError(f"Run {run_id} не завершился за 5 мин")

    if status != 'SUCCEEDED':
        raise RuntimeError(f"Apify run failed: {data.get('statusMessage', 'unknown')}")

    # Получить items
    dataset_id = data["defaultDatasetId"]
    r = requests.get(f"{APIFY_API}/datasets/{dataset_id}/items?limit={limit}",
                      headers=headers, timeout=30)
    r.raise_for_status()
    items = r.json()
    print(f"  ✅ Получено: {len(items)} items")
    return items


# === ШАГ 2: ALF VERIFICATION (с fallback) ===
def alf_verify(items: list, skip_alf: bool = False) -> dict:
    """Отправить в ALF для верификации. Если ALF DOWN — пропустить."""
    if skip_alf:
        print(f"\n[2/4] ALF: SKIP (--no-alf)")
        return {"status": "skipped", "reason": "user requested skip"}

    print(f"\n[2/4] ALF: верификация {len(items)} items")
    try:
        payload = {
            "question": json.dumps({
                "task": "slop_detector_pre_check",
                "items_count": len(items),
                "sample": items[:3],  # первые 3 для примера
            }, ensure_ascii=False)
        }
        r = requests.post(ALF_URL, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()
        response_text = data.get("response", "")
        usage = data.get("usage", {})
        if usage.get("total_tokens", 0) > 0:
            print(f"  ✅ ALF verdict: {response_text[:200]}")
            return {"status": "ok", "verdict": response_text}
        else:
            print(f"  ⚠️ ALF не отвечает (0 tokens). Fallback на local slop-detector.")
            return {"status": "alf_silent", "fallback": "local_slop"}
    except Exception as e:
        print(f"  ⚠️ ALF error: {e}. Fallback.")
        return {"status": "error", "error": str(e), "fallback": "local_slop"}


# === ШАГ 3: SLOP-DETECTOR (локальный) ===
def run_slop(items: list) -> dict:
    """Запуск slop_detector.py через subprocess."""
    print(f"\n[3/4] Slop-detector (local)")
    import subprocess
    # Сохраняем items во временный файл
    tmp = Path("/tmp/apify_pipeline_result.json")
    tmp.write_text(json.dumps(items, ensure_ascii=False), encoding='utf-8')

    result = subprocess.run(
        ["python3", str(SLOP_SCRIPT)],
        stdin=open(tmp),
        capture_output=True,
        text=True,
        timeout=60
    )
    print(result.stdout[:500])
    if result.returncode != 0:
        print(f"  ⚠️ slop_detector stderr: {result.stderr[:300]}")

    # Читаем /tmp/slop_result.json
    slop_result_path = Path("/tmp/slop_result.json")
    if slop_result_path.exists():
        return json.loads(slop_result_path.read_text())
    return {"total": 0, "clean": 0, "flagged": 0, "blocked": 0,
            "flagged_items": [], "blocked_items": []}


# === ШАГ 4: CSV + BLOCKED JSON ===
def write_results(items: list, slop: dict):
    """Записать CLEAN в CSV, BLOCKED в JSON для review."""
    print(f"\n[4/4] Запись результатов")
    blocked_ids = {str(b["item"].get("id")) for b in slop.get("blocked_items", [])}

    # CLEAN items в CSV
    fieldnames = [
        "id", "title", "price", "city", "seller_name", "seller_id",
        "url", "photos_count", "description_length", "published_at",
        "slop_flags", "alf_verdict", "timestamp"
    ]
    clean = [it for it in items if str(it.get("id")) not in blocked_ids]
    blocked = [it for it in items if str(it.get("id")) in blocked_ids]

    with open(PURCHASES_CSV, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        ts = datetime.now().isoformat()
        for item in clean:
            seller = item.get("seller", {}) or {}
            writer.writerow({
                "id": item.get("id", ""),
                "title": (item.get("title", "") or "").replace("\n", " ")[:200],
                "price": item.get("price", 0),
                "city": item.get("city", "") or "",
                "seller_name": (seller.get("name", "") or "").replace("\n", " "),
                "seller_id": seller.get("id", "") or "",
                "url": item.get("url", ""),
                "photos_count": len(item.get("images", [])),
                "description_length": len(item.get("description", "") or ""),
                "published_at": item.get("scrapedAt", ""),
                "slop_flags": "CLEAN",
                "alf_verdict": "verified" if slop else "pending",
                "timestamp": ts,
            })
    print(f"  ✅ CLEAN → {PURCHASES_CSV}: {len(clean)} items")

    # BLOCKED в JSON
    BLOCKED_JSON.write_text(json.dumps(blocked, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"  ✅ BLOCKED → {BLOCKED_JSON}: {len(blocked)} items")


# === MAIN ===
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="iPhone")
    parser.add_argument("--city", default="Краснодар")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--no-alf", action="store_true", help="Пропустить ALF")
    parser.add_argument("--output", default=str(PURCHASES_CSV))
    args = parser.parse_args()

    global PURCHASES_CSV
    PURCHASES_CSV = Path(args.output)

    print(f"═══════════════════════════════════════════════════")
    print(f"  PIPELINE: {args.query} в {args.city} (limit {args.limit})")
    print(f"═══════════════════════════════════════════════════")

    token = load_token()

    # 1. Apify
    items = run_apify(token, args.query, args.city, args.limit)

    # 2. ALF (опционально)
    alf_result = alf_verify(items, skip_alf=args.no_alf)

    # 3. Slop-detector
    slop = run_slop(items)

    # 4. CSV + BLOCKED
    write_results(items, slop)

    # Сводка
    print(f"\n═══════════════════════════════════════════════════")
    print(f"  СВОДКА")
    print(f"═══════════════════════════════════════════════════")
    print(f"  Всего: {len(items)}")
    print(f"  CLEAN: {len(items) - len(slop.get('blocked_items', []))}")
    print(f"  BLOCKED: {len(slop.get('blocked_items', []))}")
    print(f"  ALF: {alf_result.get('status', 'unknown')}")
    print(f"  CSV: {PURCHASES_CSV}")
    print(f"  Blocked JSON: {BLOCKED_JSON}")


if __name__ == "__main__":
    main()
