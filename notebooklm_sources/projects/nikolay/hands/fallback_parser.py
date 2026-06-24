# Парсер Avito через DuckDuckGo (FALLBACK когда VPS IP забанен)
# DuckDuckGo не банит, отдаёт результаты по site:avito.ru
#
# Использование:
#   from hands.fallback_parser import parse_avito_fallback
#   results = parse_avito_fallback("iPhone 13 128GB", max_price=25000, city="msk")

import re
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus

CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)
LOG_FILE = "/var/log/alina_fallback_parser.log"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

CITY_MAP = {
    "msk": "Москва",
    "spb": "Санкт-Петербург",
    "krd": "Краснодар",
    "all": ""
}


def log(msg: str):
    line = f"[{datetime.now().isoformat()}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def parse_price(text: str) -> int:
    """Извлекает цену: '24 000 ₽' → 24000"""
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else 0


def parse_avito_fallback(
    query: str,
    max_price: int = 0,
    city: str = "msk",
    limit: int = 10
) -> list[dict]:
    """
    FALLBACK парсер Avito через DuckDuckGo HTML.
    Когда основной Avito-парсер (Selenium) не работает из-за бана IP.

    Args:
        query: что ищем ("iPhone 13 128GB")
        max_price: верхняя граница цены в рублях (0 = без лимита)
        city: msk / spb / krd / all
        limit: максимум результатов (default 10)

    Returns:
        list[dict] — лоты с Avito (title, price, url, id)
    """
    city_name = CITY_MAP.get(city, city)
    full_query = f"{query} {city_name} site:avito.ru".strip()
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(full_query)}"

    cache_key = f"{query}_{max_price}_{city}_{limit}".replace(" ", "_")
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists() and (time.time() - cache_file.stat().st_mtime) < 600:
        log(f"cache hit: {cache_key}")
        return json.loads(cache_file.read_text())

    headers = {"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9"}
    log(f"GET {url[:80]}...")

    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
    except requests.RequestException as e:
        log(f"ERROR: {e}")
        return []

    html = r.text
    results = []

    # Сначала найдём все ссылки на avito.ru в HTML (пропуская обёртку duckduckgo.com)
    avito_pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="[^"]*uddg=([^"&]+)[^"]*"[^>]*>(.*?)</a>',
        re.DOTALL
    )
    tag_pattern = re.compile(r"<[^>]+>")
    price_pattern = re.compile(r"(\d[\d\s\u00a0]*(?:\s?\d{3})*)\s*[₽рР]")
    from urllib.parse import unquote

    for m in avito_pattern.finditer(html):
        encoded_url = m.group(1)
        title = tag_pattern.sub(" ", m.group(2)).strip()[:100]
        if not title or len(title) < 3:
            continue

        real_url = unquote(encoded_url)
        if "avito.ru" not in real_url:
            continue

        # Цена из title (DDG часто показывает цену в title)
        price_match = price_pattern.search(title)
        price = parse_price(price_match.group(1)) if price_match else 0

        if max_price > 0 and price > max_price:
            continue
        if price == 0 and max_price > 0:  # если задан лимит — без цены пропускаем
            continue

        # ID
        id_match = re.search(r"id_(\w+)", real_url)
        lot_id = id_match.group(1) if id_match else real_url.split("/")[-1][:20]

        results.append({
            "id": f"avito_{lot_id}",
            "title": title[:80],
            "price": price,
            "url": real_url,
            "photos": [],
            "seller": "DDG-индекс",
            "city": city,
            "source": "duckduckgo_fallback",
            "posted": "unknown"
        })
        if len(results) >= limit:
            break

    cache_file.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    log(f"OK: {len(results)} results")
    return results


if __name__ == "__main__":
    print("=== Тест Fallback-парсера (Avito через DuckDuckGo) ===\n")
    results = parse_avito_fallback("iPhone 13 128GB", max_price=35000, city="msk", limit=5)
    for r in results:
        print(f"  {r['title'][:50]:50s} | {r['price']:>6}₽ | {r['url'][:60]}")
    print(f"\nВсего: {len(results)}")
