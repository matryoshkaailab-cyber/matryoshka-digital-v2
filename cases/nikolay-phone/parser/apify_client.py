"""
Apify Client для парсинга Avito iPhone Краснодар.
Использует Apify MCP server (https://mcp.apify.com/).

Зависимости: pip install apify-client
Токен: APIFY_TOKEN в /root/.hermes/profiles/nikolay/.env

Использование:
    python3 apify_client.py --query "iPhone" --city "Краснодар" --limit 50
"""
import os
import json
import csv
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Загрузка токена
ENV_PATH = Path("/root/.hermes/profiles/nikolay/.env")
APIFY_TOKEN = None
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("APIFY_TOKEN="):
            APIFY_TOKEN = line.split("=", 1)[1].strip()
            break

if not APIFY_TOKEN:
    print("❌ APIFY_TOKEN не найден в /root/.hermes/profiles/nikolay/.env")
    print("Добавь: APIFY_TOKEN=apify_api_xxx...")
    sys.exit(1)

# Конфигурация
ACTOR_ID = "zen-studio/avito-listings-scraper"  # 33K runs, готовый
INPUT_SCHEMA = {
    "queries": ["iPhone"],
    "location": "Краснодар",
    "maxItems": 50,
    "proxyConfiguration": {
        "useApifyProxy": True,
        "apifyProxyGroups": ["RESIDENTIAL"]  # Резидентные прокси (обход блокировки VPS)
    }
}

# Apify REST API
APIFY_API = "https://api.apify.com/v2"


def run_actor(token, actor_id, input_data):
    """Запуск Actor через REST API."""
    import requests
    url = f"{APIFY_API}/acts/{actor_id}/runs"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(url, json=input_data, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()  # {"id": run_id, "status": "RUNNING"}


def wait_for_run(token, run_id, timeout_sec=300):
    """Ожидание завершения run."""
    import requests
    import time
    url = f"{APIFY_API}/actor-runs/{run_id}"
    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()
    while time.time() - start < timeout_sec:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            return data
        time.sleep(5)
    raise TimeoutError(f"Run {run_id} не завершился за {timeout_sec}s")


def get_dataset(token, dataset_id, limit=100):
    """Получение результатов из Dataset."""
    import requests
    url = f"{APIFY_API}/datasets/{dataset_id}/items?limit={limit}"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()  # List[dict]


def save_to_csv(items, output_path):
    """Сохранение в purchases.csv. Заголовки фиксированные."""
    if not items:
        print("⚠️ Нет items для сохранения")
        return

    fieldnames = [
        "id", "title", "price", "city", "seller_name", "seller_id",
        "url", "photos_count", "description_length", "published_at",
        "slop_flags", "alf_verdict", "timestamp"
    ]

    file_exists = output_path.exists()
    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        ts = datetime.now().isoformat()
        for item in items:
            row = {
                "id": item.get("id", ""),
                "title": item.get("title", "").replace("\n", " ")[:200],
                "price": item.get("price", 0),
                "city": item.get("city", ""),
                "seller_name": item.get("seller", {}).get("name", "").replace("\n", " "),
                "seller_id": item.get("seller", {}).get("id", ""),
                "url": item.get("url", ""),
                "photos_count": len(item.get("photos", [])),
                "description_length": len(item.get("description", "")),
                "published_at": item.get("publishedAt", ""),
                "slop_flags": "",  # заполняется slop-detector'ом
                "alf_verdict": "",  # заполняется после ALF
                "timestamp": ts,
            }
            writer.writerow(row)
    print(f"✅ Сохранено {len(items)} items в {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="iPhone")
    parser.add_argument("--city", default="Краснодар")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", default="/root/matryoshka/nikolay/purchases.csv")
    parser.add_argument("--dry-run", action="store_true", help="Только показать, не запускать")
    args = parser.parse_args()

    input_data = {
        "queries": [args.query],
        "location": args.city,
        "maxItems": args.limit,
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        }
    }

    print(f"=== Apify Client: {args.query} в {args.city} (limit {args.limit}) ===")
    print(f"Actor: {ACTOR_ID}")
    print(f"Token: {APIFY_TOKEN[:20]}...")
    print(f"Input: {json.dumps(input_data, indent=2)}")

    if args.dry_run:
        print("\n[DRY-RUN] Не запускаю. Для реального запуска убери --dry-run.")
        return

    # 1. Запуск
    print("\n[1/3] Запуск Actor...")
    run = run_actor(APIFY_TOKEN, ACTOR_ID, input_data)
    run_id = run["id"]
    print(f"  run_id: {run_id}")

    # 2. Ожидание
    print("[2/3] Ожидание завершения...")
    result = wait_for_run(APIFY_TOKEN, run_id)
    print(f"  status: {result['status']}")
    if result["status"] != "SUCCEEDED":
        print(f"❌ Run failed: {result.get('error', {})}")
        sys.exit(1)

    # 3. Получение данных
    print("[3/3] Получение items...")
    dataset_id = result["defaultDatasetId"]
    items = get_dataset(APIFY_TOKEN, dataset_id, limit=args.limit)
    print(f"  Получено: {len(items)} items")

    # 4. Сохранение
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    save_to_csv(items, output)

    print(f"\n✅ Готово. Следующий шаг: skill slop-detector")


if __name__ == "__main__":
    main()
