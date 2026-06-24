"""
main.py — парсер Avito
Запускается через cron каждые 30 мин.
Парсит лоты по фильтрам из FILTERS, сохраняет в /root/matryoshka/cases/nikolay/avito_lots/
"""
import sys
import json
import time
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

from auth import create_driver, load_cookies, apply_cookies, verify_auth
from storage import save_lots, filter_new, OUTPUT_DIR

# ============================================================
# КОНФИГУРАЦИЯ
# ============================================================

# Город: Краснодар (можно добавить другие)
CITY = "krasnodar"
AVITO_BASE = "https://www.avito.ru"

# Фильтры (из плана v5)
FILTERS = {
    "iPhone": {
        "queries": ["iPhone 11", "iPhone 12", "iPhone 13"],
        "max_price": 5000,  # только бюджетные
    },
    "XKIN": {
        "queries": ["XKIN73", "XKIN76"],
        "max_price": 1500,
    },
    "accessories": {
        "queries": ["чехол iPhone", "кабель Lightning"],
        "max_price": 500,
    },
}

# Селекторы (могут устареть — Avito меняет вёрстку)
# ИСПОЛЬЗУЕМ BeautifulSoup (не Selenium элементы)
SELECTORS = {
    "lot_card": "div.items-listItem-Qazzp, div.iva-item-body-oMJBI",
    "lot_title": "[data-marker='item-title'], a.styles-module-root-cfrVG",
    "lot_price": "[data-marker='item-price']",
    "lot_link": "a[href*='/krasnodar/']",
    "lot_photo": "img",
}

LOG_FILE = "/var/log/avito_parser.log"


def log(msg: str):
    """Логирование в файл и stdout."""
    line = f"[{datetime.now().isoformat()}] {msg}"
    print(line, file=sys.stdout)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def search_url(query: str, city: str = CITY) -> str:
    """URL поиска на Avito."""
    return f"{AVITO_BASE}/{city}?q={quote(query)}"


def extract_lot_data(card, query: str) -> dict:
    """Извлечь данные из карточки лота. Принимает BeautifulSoup Tag."""
    lot = {
        "title": None,
        "price": None,
        "url": None,
        "photo": None,
        "city": CITY,
        "query": query,
        "found_at": datetime.now().isoformat(),
    }

    # Title — ищем в разных местах
    try:
        # Сначала data-marker="item-title"
        title_elem = card.select_one("[data-marker='item-title']")
        if not title_elem:
            # Или в link
            title_elem = card.select_one("a[href*='/krasnodar/']")
        if title_elem:
            lot["title"] = title_elem.get_text(strip=True) or title_elem.get("title", "")
    except (AttributeError, Exception) as e:
        log(f"    ! Ошибка title: {e}")

    # Price
    try:
        price_elem = card.select_one("[data-marker='item-price']")
        if price_elem:
            price_text = price_elem.get_text()
            price_match = re.search(r"(\d[\d\s]*)\s*₽", price_text)
            if price_match:
                lot["price"] = int(price_match.group(1).replace(" ", "").replace("\u00a0", ""))
    except (AttributeError, ValueError, Exception) as e:
        log(f"    ! Ошибка price: {e}")

    # URL
    try:
        link_elem = card.select_one("a[href*='/krasnodar/']")
        if link_elem and link_elem.get("href"):
            href = link_elem["href"]
            # Пропускаем категории и фильтры
            if any(skip in href for skip in ["?", "#", "/category", "remont_i_stroitelstvo", "/krasnodar/predlozhenie"]):
                lot["url"] = None
            elif href.startswith("/"):
                lot["url"] = AVITO_BASE + href
            else:
                lot["url"] = href
    except (AttributeError, Exception) as e:
        log(f"    ! Ошибка url: {e}")

    # Photo
    try:
        photo_elem = card.select_one("img")
        if photo_elem and photo_elem.get("src"):
            src = photo_elem["src"]
            # Avito изображения
            if "avito" in src or "data:image" not in src:
                lot["photo"] = src
    except (AttributeError, Exception):
        pass

    return lot


def parse_search_page(driver, query: str, max_price: int) -> list:
    """Парсить страницу поиска Avito."""
    url = search_url(query)
    log(f"  → Парсим: {url} (max {max_price}₽)")

    try:
        driver.get(url)
        time.sleep(3)  # Подождём загрузки JS
    except TimeoutException:
        log(f"  ✗ Timeout при загрузке {url}")
        return []

    # Сохраняем HTML для отладки
    html_path = OUTPUT_DIR / f"debug_{query.replace(' ', '_')}.html"
    html_path.write_text(driver.page_source, encoding="utf-8")
    log(f"  → HTML сохранён: {html_path}")

    # Парсим через BeautifulSoup (надёжнее чем Selenium)
    soup = BeautifulSoup(driver.page_source, "lxml")

    # Ищем карточки лотов
    cards = soup.select(SELECTORS["lot_card"])
    if not cards:
        # Попробуем альтернативные селекторы (Avito часто меняет)
        cards = soup.select("[itemtype='http://schema.org/Product']")
        if not cards:
            cards = soup.select("div[data-marker='catalog-serp'] > div")
        if not cards:
            cards = soup.select(".iva-item-content")

    log(f"  → Найдено карточек: {len(cards)}")

    lots = []
    for card in cards:
        lot = extract_lot_data(card, query)
        # Фильтр по цене
        if lot["price"] is None:
            continue
        if lot["price"] > max_price:
            continue
        # Минимальная валидация
        if not lot["title"] or not lot["url"]:
            continue
        lots.append(lot)
        log(f"    ✓ {lot['title'][:50]} — {lot['price']}₽")

    return lots


def main():
    log("=" * 60)
    log("AVITO PARSER START")
    log("=" * 60)

    driver = None
    try:
        # Создаём driver
        driver = create_driver(headless=True)

        # Загружаем и применяем cookies
        cookies = load_cookies()
        log(f"  → Загружено {len(cookies)} cookies")
        apply_cookies(driver, cookies)

        # Проверяем авторизацию
        if not verify_auth(driver):
            log("  ✗ Cookies протухли! Запусти: python3 /opt/avito_parser/auth.py --refresh")
            sys.exit(1)
        log("  ✓ Авторизация подтверждена")

        # Парсим по всем фильтрам
        all_lots = []
        for category, cfg in FILTERS.items():
            log(f"\n  → Категория: {category}")
            for query in cfg["queries"]:
                lots = parse_search_page(driver, query, cfg["max_price"])
                all_lots.extend(lots)
                time.sleep(5)  # Пауза между запросами (не нагружать Avito)

        # Фильтруем уже виденные
        new_lots = filter_new(all_lots)
        log(f"\n  → Найдено: {len(all_lots)}, новых: {len(new_lots)}")

        # Сохраняем новые
        if new_lots:
            output_file = save_lots(new_lots)
            log(f"  ✓ Сохранено {len(new_lots)} новых лотов в {output_file}")
        else:
            log("  → Новых лотов нет (все уже виденные)")

        log("=" * 60)
        log(f"AVITO PARSER END (OK) — {len(new_lots)} новых лотов")
        log("=" * 60)
        return 0
    except Exception as e:
        import traceback
        log(f"  ✗ ОШИБКА: {e}")
        log(traceback.format_exc())
        return 1
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    sys.exit(main())
