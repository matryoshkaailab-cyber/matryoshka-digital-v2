#!/usr/bin/env python3
"""
slop_detector.py — поиск AI-шлака в JSON-ответах парсеров Avito.

Использование:
    python3 slop_detector.py purchases.csv
    python3 slop_detector.py < /tmp/apify_result.json
"""
import csv
import json
import sys
import re
from collections import Counter


def detect_slop(item, all_items):
    """Возвращает список флагов для одного item."""
    flags = []
    seller = item.get('seller', {}) or {}
    seller_id = seller.get('id', '') or ''
    seller_name = seller.get('name', '') or ''
    price = item.get('price', 0) or 0
    description = item.get('description', '') or ''
    city = item.get('city', '') or ''
    photos = item.get('photos', []) or []
    title = item.get('title', '') or ''
    item_id = item.get('id', '')

    # CRITICAL: дубликаты ID
    same_id = [x for x in all_items if x.get('id') == item_id]
    if len(same_id) > 1:
        flags.append(('CRITICAL', 'duplicate_id', f'{len(same_id)} copies'))

    # CRITICAL: цена подозрительно низкая (< 1000 руб для iPhone)
    if 'iphone' in title.lower() and price > 0 and price < 1000:
        flags.append(('CRITICAL', 'iphone_price_too_low', f'{price}₽'))

    # HIGH: mass-seller (один продавец с 20+ items)
    same_seller = [x for x in all_items if (x.get('seller', {}) or {}).get('id') == seller_id and seller_id]
    if len(same_seller) > 20:
        flags.append(('HIGH', 'mass_seller', f'{len(same_seller)} items'))

    # HIGH: дефолтный seller
    if seller_name.strip() in ('Пользователь', 'User', '', 'None'):
        flags.append(('HIGH', 'default_seller_name', repr(seller_name)))

    # HIGH: не Краснодар
    if city and 'краснодар' not in city.lower():
        flags.append(('HIGH', 'wrong_city', city))

    # MEDIUM: нет фото
    if not photos:
        flags.append(('MEDIUM', 'no_photos', ''))

    # MEDIUM: короткое описание
    if len(description) < 20:
        flags.append(('MEDIUM', 'short_description', f'{len(description)} chars'))

    # MEDIUM: подозрительный паттерн в описании
    if re.search(r'срочн.*торг|торг.*срочн', description, re.IGNORECASE):
        flags.append(('MEDIUM', 'urgency_pattern', ''))

    # LOW: круглая цена
    if price > 0 and price % 1000 == 0:
        flags.append(('LOW', 'round_price', f'{price}₽'))

    # LOW: описание all-lowercase или all-uppercase
    if description and len(description) > 50:
        if description == description.lower() or description == description.upper():
            flags.append(('LOW', 'caps_pattern', ''))

    return flags


def score_flags(flags):
    """Считает score по severity."""
    score = 0
    has_critical = False
    has_high = False
    for severity, _, _ in flags:
        if severity == 'CRITICAL':
            score += 100
            has_critical = True
        elif severity == 'HIGH':
            score += 10
            has_high = True
        elif severity == 'MEDIUM':
            score += 1
        else:
            score += 0.1
    return score, has_critical, has_high


def process_json_data(data):
    """Обработать JSON (может быть dict с 'results' или list)."""
    if isinstance(data, dict):
        items = data.get('results', data.get('items', data.get('data', [])))
        if not isinstance(items, list):
            items = [data]
    elif isinstance(data, list):
        items = data
    else:
        items = []
    return items


def main():
    if len(sys.argv) > 1 and sys.argv[1].endswith('.csv'):
        # Читаем CSV (в формате purchases.csv)
        items = []
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Нормализуем к формату item
                items.append({
                    'id': row.get('id', ''),
                    'title': row.get('title', ''),
                    'price': int(row.get('price', 0)) if row.get('price', '').isdigit() else 0,
                    'city': row.get('city', ''),
                    'seller': {
                        'id': row.get('seller_id', ''),
                        'name': row.get('seller_name', '')
                    },
                    'description': row.get('description_length', ''),
                    'photos': [],  # CSV не хранит
                    'url': row.get('url', ''),
                })
    else:
        # Читаем JSON из stdin
        data = json.loads(sys.stdin.read())
        items = process_json_data(data)

    print(f"📊 Slop-detector: {len(items)} items\n")

    stats = Counter()
    clean_items = []
    flagged_items = []
    blocked_items = []

    for item in items:
        flags = detect_slop(item, items)
        score, critical, high = score_flags(flags)

        for severity, kind, _ in flags:
            stats[severity] += 1

        if critical:
            blocked_items.append((item, flags))
        elif high:
            flagged_items.append((item, flags))
        else:
            clean_items.append((item, flags))

    # Вывод
    print(f"✅ CLEAN: {len(clean_items)}")
    print(f"⚠️ FLAGGED (HIGH): {len(flagged_items)}")
    print(f"🚫 BLOCKED (CRITICAL): {len(blocked_items)}")
    print(f"\n📈 Stats: {dict(stats)}")

    if blocked_items:
        print(f"\n🚫 BLOCKED items:")
        for item, flags in blocked_items[:10]:
            print(f"  - [{item.get('id')}] {item.get('title', '')[:50]}")
            for sev, kind, val in flags:
                print(f"      {sev} {kind}: {val}")

    if flagged_items:
        print(f"\n⚠️ FLAGGED items (first 10):")
        for item, flags in flagged_items[:10]:
            print(f"  - [{item.get('id')}] {item.get('title', '')[:50]}")
            for sev, kind, val in flags:
                print(f"      {sev} {kind}: {val}")

    # JSON output для ALF
    result = {
        'total': len(items),
        'clean': len(clean_items),
        'flagged': len(flagged_items),
        'blocked': len(blocked_items),
        'stats': dict(stats),
        'flagged_items': [
            {'item': item, 'flags': flags} for item, flags in flagged_items
        ],
        'blocked_items': [
            {'item': item, 'flags': flags} for item, flags in blocked_items
        ]
    }
    print(f"\n📤 JSON для ALF:")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])

    # Сохранить в файл для ALF
    with open('/tmp/slop_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Полный результат: /tmp/slop_result.json")


if __name__ == '__main__':
    main()
