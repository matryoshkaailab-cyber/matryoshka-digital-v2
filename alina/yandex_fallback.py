"""
yandex_fallback.py — fallback парсер Авито через Yandex XML.

Когда основной Apify парсер получает 429 или fail — Алина переключается на Yandex.
"""
import re
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime


def search_yandex(query: str, max_results: int = 10) -> list:
    """
    Ищет лоты Avito через Yandex HTML.
    Возвращает список dict (title, url, snippet).
    """
    full_query = f"{query} site:avito.ru Краснодар"
    url = f"https://yandex.ru/search/?text={urllib.parse.quote_plus(full_query)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
        "Accept-Language": "ru-RU,ru;q=0.9",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return [{"error": f"Yandex fail: {e}"}]

    # Простой regex — вытаскиваем ссылки avito.ru из результатов
    results = []
    avito_pattern = re.compile(r'href="(https?://[^"]*avito\.ru/[^"]+)"[^>]*>([^<]{10,200})')
    for m in avito_pattern.finditer(html):
        url, title = m.group(1), m.group(2).strip()
        if any(k in title.lower() for k in ['iphone', 'айфон']):
            results.append({"url": url, "title": title})
        if len(results) >= max_results:
            break
    return results


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "iPhone 13 128GB"
    res = search_yandex(q)
    print(json.dumps(res, ensure_ascii=False, indent=2))
