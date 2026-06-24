# Avito парсер — обычная задача

## Что нужно
Запусти модуль avito_parser локально на своём ПК (PowerShell + Python), используя свежие cookies.

## Файлы
- Скрипт: `C:\matryoshka\hands\avito_parser.py` (если нет — создай из спецификации ниже)
- Cookies: `C:\matryoshka\alex_tasks\inbox\avito_cookies_20260610.json` (уже лежит)
- Результат должен попасть в: `C:\matryoshka\alex_tasks\outbox\avito_lots_20260610.json`

## Спецификация функции
```python
def parse_avito(query: str, max_price: int, city: str = "krasnodar", limit: int = 10) -> list[dict]:
    pass
```

## Шаги
1. Скопируй cookies из `C:\matryoshka\alex_tasks\inbox\avito_cookies_20260610.json` в `C:\Users\$env:USERNAME\.avito_cookies\cookies.json` (нужен этот путь для auth.py)
2. Проверь что установлен Python 3.11+ с `pip install selenium beautifulsoup4`
3. Если `C:\matryoshka\hands\avito_parser.py` нет — создай по спеке из ТЗ Hermes (inbox/2026-06-09_2335_AVITO_PARSER.md)
4. Запусти: `python C:\matryoshka\hands\avito_parser.py` или `python -m hands.avito_parser`
5. Сохрани результат в `C:\matryoshka\alex_tasks\outbox\avito_lots_20260610.json`
6. Ответь через hermes-respond с кратким summary (сколько лотов, какие категории)

## Что НЕ нужно
- Не нужен SSH-туннель к VPS
- Не нужно использовать SOCKS5 proxy
- Не нужно обходить защиту (cookies Олега валидные)

Просто парсинг по запросам из FILTERS (iPhone 11/12/13, XKIN73/76, чехлы, кабели) в Краснодаре.
