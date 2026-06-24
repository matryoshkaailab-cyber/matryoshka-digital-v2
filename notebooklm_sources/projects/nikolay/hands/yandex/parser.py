# Yandex-парсер для Алины (FALLBACK когда VPS IP забанен Avito)
# Парсит Yandex XML search → выдаёт лоты с Avito (Avito индексируется Yandex)
#
# Использование:
#   from hands.yandex.parser import parse_yandex_avito
#   results = parse_yandex_avito("iPhone 13 128GB", max_price=25000, city="msk")

import re
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)
LOG_FILE = "/var/log/alina_yandex_parser.log"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def log(msg: str):
    line = f"[{datetime.now().isoformat()}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def parse_price(text: str) -> int:
    """Извлекает цену из строки типа '24 000 ₽' → 24000"""
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


def parse_yandex_avito(
    query: str,
    max_price: int = 0,
    city: str = "msk",
    limit: int = 10
) -> list[dict]:
    """
    Парсит Yandex-поиск по запросу + фильтр site:avito.ru.

    Yandex не банит наш IP (мы не делаем 100 запросов в минуту).
    Это FALLBACK когда основной Avito-парсер не работает.
    """
    city_q = "" if city == "all" else f" { {'msk':'Москва','spb':'Санкт-Петербург','krd':'Краснодар'}.get(city, city) }"
    full_query = f"{query}{city_q} site:avito.ru"
    url = f"https://yandex.ru/search/?text={quote_plus(full_query)}"

    cache_key = f"{query}_{max_price}_{city}_{limit}".replace(" ", "_")
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists() and (time.time() - cache_file.stat().st_mtime) < 600:
        log(f"cache hit: {cache_key}")
        return json.loads(cache_file.read_text())

    headers = {"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9"}
    log(f"GET {url[:80]}...")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        log(f"ERROR: {e}")
        return []

    html = r.text
    results = []

    # Паттерн: <h2 ...><a href="https://www.avito.ru/.../id_XXXXXX">Title</a></h2>
    # Yandex меняет вёрстку, но структура ссылок стабильна
    pattern = re.compile(
        r'<a[^>]+href="(https?://www\.avito\.ru/[^"]+/id_\w+)"[^>]*>(.*?)</a>',
        re.DOTALL
    )
    title_pattern = re.compile(r"<[^>]+>")
    price_pattern = re.compile(r"(\d[\d\s\u00a0]*)\s*₽")

    matches = list(pattern.finditer(html))[:limit*3]  # берём с запасом, фильтруем
    for m in matches:
        url_match = m.group(1)
        title_html = m.group(2)
        title = title_pattern.sub("", title_html).strip()[:100]
        if not title or len(title) < 3:
            continue

        # Ищем цену рядом со ссылкой (в пределах 500 символов)
        idx = m.end()
        nearby = html[idx:idx+500]
        price_match = price_pattern.search(nearby)
        price = parse_price(price_match.group(1)) if price_match else 0

        # Фильтр по цене
        if max_price > 0 and price > max_price:
            continue
        if price == 0:
            continue  # без цены не берём

        # Извлечь ID
        id_match = re.search(r"id_(\w+)", url_match)
        lot_id = id_match.group(1) if id_match else url_match.split("/")[-1]

        results.append({
            "id": f"avito_{lot_id}",
            "title": title,
            "price": price,
            "url": url_match,
            "photos": [],
            "seller": "Yandex-индекс",
            "city": city,
            "source": "yandex_fallback",
            "posted": "unknown"
        })
        if len(results) >= limit:
            break

    cache_file.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    log(f"OK: {len(results)} results, диапазон {min((r['price'] for r in results), default=0)}-{max((r['price'] for r in results), default=0)}₽")

    return results


if __name__ == "__main__":
    print("=== Тест Yandex-парсера (Avito через Yandex) ===\n")
    results = parse_yandex_avito("iPhone 13 128GB", max_price=35000, city="msk", limit=5)
    for r in results:
        print(f"{r['title']:50s} | {r['price']:>6}₽ | {r['url'][:60]}")
    print(f"\nВсего: {len(results)}")
