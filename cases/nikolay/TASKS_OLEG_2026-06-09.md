# ЗАДАЧА ДЛЯ ОЛЕГА — Парсер Авито (Selenium)

**От:** HERMES (для Олега)
**Дата:** 2026-06-09
**Приоритет:** КРИТИЧНО (блокирует Stage 1.4)

---

## 🎯 ЦЕЛЬ

Подготовить **cookies аккаунта Авито** для Selenium-парсера на VPS. Без cookies парсер не работает.

## 📋 ЧТО НУЖНО СДЕЛАТЬ

### 1. Получить cookies от Николая

**Николаю нужно:**
- Зайти на **avito.ru** под своим аккаунтом (Chrome/Edge)
- Открыть **DevTools** (F12) → вкладка **Application** → **Cookies** → `https://avito.ru`
- Скопировать **ВСЕ cookies** (или 3-4 основных: session, auth, user_id, ...)

**Альтернатива:** установить расширение "EditThisCookie" или "Cookie-Editor" → экспортировать в JSON.

### 2. Передать cookies мне (HERMES)

**Формат файла:** `/root/.avito_cookies/cookies.json`

**Структура JSON:**
```json
[
  {
    "name": "session",
    "value": "...",
    "domain": ".avito.ru",
    "path": "/",
    "expires": 1234567890,
    "httpOnly": true,
    "secure": true
  },
  {
    "name": "auth",
    "value": "...",
    "domain": ".avito.ru",
    "path": "/",
    "expires": 1234567890,
    "httpOnly": true,
    "secure": true
  }
]
```

**Как мне передать:**
- Положить в `/root/.avito_cookies/cookies.json` на VPS
- Или через `send_to_alikс.py --file cookies.json` (если есть)
- Или скопировать в Obsidian vault `/root/obsidian-vault/secrets/avito_cookies.json`

### 3. Альтернатива: Selenium экспорт из своего браузера

Если не хочешь возиться с cookies вручную:
```powershell
# На Windows с Python + Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("user-data-dir=C:\\Users\\User\\AppData\\Local\\Google\\Chrome\\User Data")
driver = webdriver.Chrome(options=options)
driver.get("https://avito.ru")
# Залогинься вручную
# потом:
import json
cookies = driver.get_cookies()
with open("avito_cookies.json", "w") as f:
    json.dump(cookies, f)
```

### 4. Безопасность

⚠️ **ВАЖНО:**
- Cookies = **полный доступ** к аккаунту Авито
- Хранить **только** в `/root/.avito_cookies/` с правами `chmod 600`
- НЕ передавать в Telegram
- НЕ логировать в cron output

```bash
chmod 600 /root/.avito_cookies/cookies.json
chown root:root /root/.avito_cookies/cookies.json
```

### 5. Альтернатива: API Avito

Если у Николая есть **API токен** (как партнёр Avito):
- Положить в `/root/matryoshka/SECRETS/.env`:
  ```
  AVITO_API_TOKEN=***
  ```
- Я переделаю `auth.py` — сначала API, fallback Selenium

## 🔄 Что я сделаю как только cookies готовы

1. Создам `/opt/avito_parser/`:
   - `main.py` — главный цикл
   - `auth.py` — загрузка cookies
   - `filter.py` — фильтры (iPhone до 5000₽, XKIN, и др.)
   - `storage.py` — сохранение в `cases/nikolay/avito_lots/`
   - `requirements.txt` — selenium, beautifulsoup4

2. Настрою cron:
   ```bash
   */30 * * * * cd /opt/avito_parser && python3 main.py >> /var/log/avito_parser.log 2>&1
   0 * * * * cd /opt/avito_parser && python3 auth.py --refresh >> /var/log/avito_parser_refresh.log 2>&1
   ```

3. Установлю Selenium + Chrome:
   ```bash
   apt install -y chromium-browser chromium-driver
   pip install selenium beautifulsoup4
   ```

4. Проверю работу — первый лот появится в `/root/matryoshka/cases/nikolay/avito_lots/`

## ❓ ВОПРОСЫ

- **Avito cookies** — есть у Николая? (если нет — пусть залогинится)
- **API Avito** — есть? (быстрее и надёжнее Selenium)
- **Отдельный аккаунт** для продаж? (или тот же что для покупок?)

## ⏱ СРОК

- **Cookies** — **сегодня** (если Николай скинет)
- **Парсер** — **2-3 дня** после получения cookies
- **Первый рабочий лот** — **15.06.2026**

## 📞 КОНТАКТ

- HERMES (я) — пиши в этот чат
- Файл cookies: `/root/.avito_cookies/cookies.json` (chmod 600)
