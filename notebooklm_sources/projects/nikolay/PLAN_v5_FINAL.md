# ПЛАН НАСТРОЙКИ АЛИНЫ — PRODUCTION READY (v5 FINAL)

**Цель:** Алина готова к работе для Николая (iPhone-перепродажа + электроника)
**Срок:** 2-3 недели (Stage 1+2)
**Только VPS** (без ПК)
**Пишет:** HERMES (я)

---

## СВОДКА РЕШЕНИЙ

| Параметр | Решение |
|---|---|
| Бот | @AlisaMatryBot (id 8960236150) |
| Модель | MiniMax/MiniMax-M3 (OAuth) |
| Vision | gemini-2.5-flash-image |
| Image Gen | MiniMax image-01 |
| Fallback | Qwen 3.7 Max (через hermes-alf :8451) |
| Ассортимент | Электроника (iPhone, XKIN, аксессуары, телефоны) |
| Площадки | Авито (Selenium+API), VK (Stage 2), Telegram (основной) |
| CRM | Отдельный @NikolaCrmBot (сбор заявок + авто-ответчик) |
| Сайт | Лендинг Flask на VPS |
| Бюджет | ~3000₽/мес |

---

## STAGE 1: MVP (5-7 дней)

### 1.1 Лечение багов (1-2 часа) — HERMES

| # | Баг | Команда |
|---|---|---|
| 1 | AGENTS.md U+FEFF | `sed -i 's/\\xEF\\xBB\\xBF//' /root/.hermes/profiles/nikolay/AGENTS.md` |
| 2 | Memory limit 2200→4000 | `sed -i 's/max_tokens=2200/max_tokens=4000/' /root/.hermes/profiles/nikolay/config.yaml` |
| 3 | Background review bypass | patch config.yaml → `background_review: disabled` |
| 4 | Метрики (cron скрипт) | исправить `/usr/local/bin/nikolay_metrics.sh` (подсчёт сообщений) |
| 5 | HTTP 429 fallback | добавить в SOUL retry logic + cron monitor |

**Результат:** `journalctl -u nikolay --since "1 min ago"` без ERROR/CRITICAL

### 1.2 Новый SOUL.md (2-3 часа) — HERMES

**Файл:** `/root/.hermes/profiles/nikolay/SOUL.md` (16K → ~12K после переделки)

**Структура:**
- IDENTITY: Алина, напарник Николая, тёплая, "на ты"
- MODEL: MiniMax-M3 (MiniMax OAuth), Vision gemini-2.5-flash-image, Image Gen MiniMax image-01, Fallback Qwen 3.7 Max
- HTTP 429: retry 2/4/8/16s, fallback после 3 попыток
- BUSINESS: Ассортимент (iPhone, XKIN, аксессуары), Алгоритм карточек (3-4 фото ОДНОГО товара с разных углов, ВИД НЕ МЕНЯЕТСЯ), Финансы, Площадки
- STYLE: тёплый, "на ты", короткие, голосовые, SvetlanaNeural
- MEMORY: лимит 4000, cron prune до 100, НЕ выдумывай данные
- COMPLIANCE: Background review DISABLED, AGENTS.md БЕЗ U+FEFF, cron monitor

### 1.3 Финансы (1 час) — HERMES

**Создать:**
- `/root/matryoshka/cases/nikolay/finances/purchases.csv`
  ```
  date,item,buy_price,condition,photo,notes
  2026-06-09,iPhone 13 128GB,15000,good,photos/iphone13.jpg,батерея 84%
  ```
- `/root/matryoshka/cases/nikolay/finances/sales.csv`
  ```
  date,item,sell_price,buy_price,margin,buyer,phone
  2026-06-09,iPhone 13 128GB,22000,15000,7000,+792****5000,
  ```
- `/root/matryoshka/cases/nikolay/finances/daily_report.md` (шаблон)

**Алина обучена:** команды `/куп {item} {price}`, `/прод {item} {price}`, `/отчёт`

### 1.4 Парсер Авито на VPS (2-3 дня) — HERMES

**Структура:**
```
/opt/avito_parser/
├── main.py           # главный цикл (cron каждые 30 мин)
├── auth.py           # cookies + Selenium auth
├── filter.py         # фильтры (iPhone до 5000₽, XKIN, и др.)
├── storage.py        # сохранение в /root/matryoshka/cases/nikolay/avito_lots/
├── cookies/          # /root/.avito_cookies/ (chmod 600)
├── requirements.txt  # selenium, beautifulsoup4, requests
└── logs/             # /var/log/avito_parser.log
```

**Cron:**
```bash
*/30 * * * * cd /opt/avito_parser && python3 main.py >> /var/log/avito_parser.log 2>&1
0 * * * * cd /opt/avito_parser && python3 auth.py --refresh >> /var/log/avito_parser_refresh.log 2>&1
```

**Selenium setup:**
```bash
apt install -y chromium-browser chromium-driver
pip install selenium beautifulsoup4
```

**Файлы результатов:**
- `/root/matryoshka/cases/nikolay/avito_lots/lots_<timestamp>.json`
  ```json
  {"title":"iPhone 13 128GB","price":4000,"url":"...","city":"CITY_KRD","margin_potential":14000}
  ```

**Мониторинг:** Telegram alert если cookies протухли / Selenium crashed

### 1.5 Шаблоны электроники (30 мин) — HERMES

**iPhone:**
```
📱 {Модель} {Память}GB
✅ Батарея: {здоровье}%
💰 Цена: {цена}₽
📍 CITY_KRD | 📦 Отправка по РФ | +7 (9XX) XXX-XX-XX
```

**XKIN наушники:**
```
🎧 {Модель} наушники
🔋 Батарея: {мАч}
🎵 Шумоподавление: {есть/нет}
🔌 Зарядка: {Lightning/Type-C}
💰 Цена: {цена}₽
```

**Аксессуары:**
```
📱 {Тип} для {модель}
✅ Состояние: {новый}
💰 Цена: {цена}₽
```

### 1.6 Тест Алины (1 час) — HERMES + OLEG

- Перезапуск `systemctl restart nikolay`
- Отправить фото iPhone → Алина делает карточку
- `/куп iPhone 13 15000` → Алина в purchases.csv
- `/прод iPhone 13 22000` → Алина в sales.csv
- `/отчёт` → daily_report.md

**Результат:** Алина работает, шаблоны применяются, финансы пишутся

---

## STAGE 2: PRODUCTION (5-7 дней)

### 2.1 Сайт-лендинг Flask (1-2 дня) — HERMES

**Структура:**
```
/var/www/matryoshka/landing/
├── app.py              # Flask app
├── templates/index.html
├── static/css/style.css, js/main.js, images/
└── requirements.txt     # flask, gunicorn
```

**Nginx:**
```nginx
location /landing/ {
    proxy_pass http://127.0.0.1:8080/;
    proxy_set_header Host $host;
}
```

**Контент лендинга:**
- Заголовок: "Продаём электронику | CITY_KRD"
- О нас, каталог (3-5 примеров), преимущества
- CTA: "Написать в Telegram" → @AlisaMatryBot

**АПИ для Алины (обновлять каталог):**
- POST /api/catalog/add
- GET /api/catalog/list
- DELETE /api/catalog/<id>

### 2.2 API Avito (1-2 недели) — OLEG + CLIENT_001

- OLEG регистрирует Николая как партнёра Avito
- Получает API токен → `SECRETS/.env` → `AVITO_API_TOKEN=***`
- HERMES обновляет `auth.py` — сначала API, fallback Selenium

### 2.3 VK интеграция (2-3 дня) — HERMES

- OLEG получает VK API токен
- `SECRETS/.env` → `VK_API_TOKEN=***`
- `/opt/vk_poster/`
  - main.py (постинг), cross_post.py (с Авито), metrics.py

**Cron:** `0 */6 * * * cd /opt/vk_poster && python3 main.py >> /var/log/vk_poster.log 2>&1`

### 2.4 Управление и планирование (1 день) — HERMES

- Cron на утренний/вечерний отчёт Алины
- Шаблон в SOUL.md

---

## STAGE 3: EXTENSION (3-5 дней)

### 3.1 CRM Bot @NikolaCrmBot (2-3 дня) — HERMES

**Отдельный бот (OLEG получает токен через @BotFather):**
```
/opt/crm_bot/
├── main.py
├── requests_handler.py    # сбор заявок
├── auto_reply.py           # типовые ответы
└── database.py             # SQLite
```

**Функции:** сбор заявок + авто-ответчик по каталогу `/root/matryoshka/cases/nikolay/catalog.json`

### 3.2 Мультиканал (1-2 дня) — HERMES

- Единый дашборд Flask на 8082
- Агрегация Авито + VK + Telegram + CRM
- Метрики real-time

---

## ЧЕКЛИСТ PRODUCTION READY

| # | Проверка | Как |
|---|---|---|
| 1 | Алина запускается без ошибок | `systemctl status nikolay` |
| 2 | SOUL.md актуальный | `head -50 SOUL.md` |
| 3 | Memory не переполняется | `journalctl -u nikolay | grep memory` |
| 4 | Нет 429 на miniMax | `journalctl -u nikolay --since "1h" | grep 429` |
| 5 | Парсер Авито работает | `tail -20 /var/log/avito_parser.log` |
| 6 | Финансы пишутся | `cat .../finances/purchases.csv` |
| 7 | Шаблоны применяются | отправить фото Алине |
| 8 | Баги исправлены | `grep -r U+FEFF` пусто |
| 9 | Лендинг открывается (Stage 2) | `curl http://localhost/landing/` |
| 10 | CRM бот отвечает (Stage 3) | написать @NikolaCrmBot |

---

## ТАЙМЛАЙН

| Дата | Что | Кто |
|---|---|---|
| 09.06 | Лечу баги + пишу SOUL.md | HERMES |
| 10-11.06 | Создаю finances/ + шаблоны | HERMES |
| 12-14.06 | Парсер Selenium | HERMES |
| 15.06 | Тест Алины с Николаем | HERMES + OLEG + CLIENT_001 |
| 16-17.06 | Сайт-лендинг Flask | HERMES |
| 18-20.06 | VK интеграция | HERMES (ждём токен) |
| 21-22.06 | Планирование (cron) | HERMES |
| 23-25.06 | CRM Bot | HERMES (ждём токен) |
| 26-27.06 | Мультиканал | HERMES |
| 28.06 | Финальный тест + передача | Все |

**ИТОГО:** ~3 недели (09.06 → 28.06)

---

## БЮДЖЕТ

| Статья | Стоимость |
|---|---|
| VPS | 2000₽/мес |
| miniMax API (M3) | ~800₽/мес |
| gemini-2.5-flash-image | ~200₽/мес |
| MiniMax image-01 | ~300₽/мес |
| Qwen 3.7 Max (fallback) | 0₽ (локально) |
| **ИТОГО** | **~3300₽/мес** |

Для Николая: бесплатно в тест, потом 3000₽/мес.

---

## ЗАПУСК

**OLEG, когда скажешь "начинай Stage 1" — сразу делаю:**

1. **Час 1-2:** Лечу баги (5 пунктов)
2. **Час 3-5:** Пишу новый SOUL.md
3. **Час 6:** Создаю finances/ с шаблонами
4. **День 2-4:** Парсер Авито (Selenium)
5. **День 5:** Тест с Николаем
