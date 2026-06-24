# Avito парсер — задача для Аликса

## Проблема
VPS IP (85.137.166.209) забанен Avito. Cookies обновлены, но парсинг с VPS невозможен.

## Решение
Парсинг с твоего ПК (домашний IP — не забанен) с авторизацией по cookies Олега.

## Что нужно сделать (по шагам)

### 1. Скопируй cookies в нужное место
Источник: `C:\matryoshka\alex_tasks\inbox\avito_cookies_20260610.json` (уже лежит)
Назначение: `C:\Users\User\.avito_cookies\cookies.json`

### 2. Проверь что скрипты есть
- `C:\matryoshka\hands\avito_parser.py` (если нет — создай по образцу)
- `C:\matryoshka\hands\avito_parser_auth.py` (или auth.py)

### 3. Установи зависимости (если не установлены)
```
pip install selenium beautifulsoup4 lxml requests
```

### 4. Запусти парсер
```
cd C:\matryoshka\hands
python avito_parser.py
```

### 5. Результат положи в
`C:\matryoshka\alex_tasks\outbox\avito_lots_20260610.json`

### 6. Ответь через hermes-respond
Сколько лотов нашлось, по каким категориям, какие первые 3-5.

## Фильтры для парсинга (из FILTERS)
- iPhone 11/12/13 (max 5000₽)
- XKIN73 / XKIN76 (max 1500₽)
- чехол iPhone / кабель Lightning (max 500₽)
- Город: Краснодар (krasnodar)

## Если что-то не получается
Ответь через hermes-respond с описанием проблемы. Не нужно think-only 3000 символов — лучше кратко что сделал и где застрял.
