# ALF (Strategic Analyst) — полный технический документ
**Версия:** 2026-06-15 | **Автор:** Hermes | **Статус:** Active (running 5 дней)

---

## 1. ИДЕНТИЧНОСТЬ

| Параметр | Значение |
|---|---|
| **Имя** | ALF (ранее — АЛАН) |
| **Роль** | Стратег, аналитик |
| **Рой** | ⚪ Белый (Мозг) |
| **Назначение** | Стратегические ответы, аналитика, долгие рассуждения |
| **Пользователь** | OLEG (Telegram ID 1951845052 — `ALF_ALLOWED_USERS`) |
| **Telegram-бот** | `@IlonAnalyticBot` (отдельный бот для ALF) |

---

## 2. ГДЕ ЖИВЁТ

| Компонент | Расположение |
|---|---|
| **VPS** | 85.137.166.209 (root, /root/matryoshka/alf/) |
| **Systemd unit** | `/etc/systemd/system/hermes-alf.service` |
| **HTTP API** | `127.0.0.1:8451` |
| **Код** | `/root/matryoshka/alf/alf_server.py` (11.4 KB) |
| **Telegram bot** | `/root/matryoshka/alf/alf_telegram_bot.py` (17.4 KB) |
| **Env** | `/root/matryoshka/alf/.env` |
| **PID** | 648995 (active since 2026-06-10 13:14:44, 5 дней uptime) |
| **Память** | 5.7 MB (peak 11.3 MB) |

---

## 3. АРХИТЕКТУРА (как работает)

```
┌─────────────────────┐
│  Telegram user      │
│  (OLEG @OLEG_USER)  │
└──────────┬──────────┘
           │ пишет в @IlonAnalyticBot
           ▼
┌──────────────────────────────────┐
│  alf_telegram_bot.py             │
│  - парсит команды                │
│  - rate-limit                    │
│  - пишет логи                    │
└──────────┬───────────────────────┘
           │ HTTP POST /chat
           ▼
┌──────────────────────────────────┐
│  alf_server.py (:8451)           │
│  - ask_brain(prompt)             │
│  - fallback chain                │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│  FALLBACK CHAIN (3 уровня)                              │
│  1️⃣ Qwen 3.7 Max  →  qwen2api прокси (127.0.0.1:8765)   │
│  2️⃣ Qwen 3.7 Plus →  тот же qwen2api                    │
│  3️⃣ MiniMax-M3   →  api.minimax.io/v1                   │
└──────────────────────────────────────────────────────────┘
```

---

## 4. МОЗГ (brain chain)

| # | Провайдер | Endpoint | Модель | Назначение |
|---|---|---|---|---|
| 1 | **Qwen 3.7 Max** | `http://127.0.0.1:8765/v1` | qwen3.7-max | Основной (Qwen через локальный прокси) |
| 2 | **Qwen 3.7 Plus** | `http://127.0.0.1:8765/v1` | qwen3.7-plus | Запасной (если Max не отвечает) |
| 3 | **MiniMax-M3** | `https://api.minimax.io/v1` | MiniMax-M3 | Последний fallback (облако) |

**Health check:** `qwen_healthy=true`, `fallback_enabled=true`, `minimax_configured=true`.

---

## 5. SYSTEMD

```ini
[Service]
Type=simple
User=root
WorkingDirectory=/root/matryoshka/alf
ExecStart=/usr/bin/python3 /root/matryoshka/alf/alf_server.py
Restart=on-failure
RestartSec=15
EnvironmentFile=/root/matryoshka/alf/.env
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=read-only
```

**Зависимости:** `After=qwen2api.service` (ALF стартует ПОСЛЕ прокси).

---

## 6. ENDPOINTS (alf_server.py)

| Метод | Путь | Назначение |
|---|---|---|
| `GET` | `/health` | health-check (agent, brain, qwen, fallback) |
| `POST` | `/chat` | основной вызов (промпт → ответ) |
| `GET` | `/status` | подробный статус агента |

**Параметры `/chat`:** prompt, model (опц.), max_tokens (2500), temperature (0.7).

---

## 7. TELEGRAM-ИНТЕРФЕЙС (alf_telegram_bot.py)

**Бот:** `@IlonAnalyticBot`
**Токен:** `ALF_TG_TOKEN` (в .env)
**Доступ:** `ALF_ALLOWED_USERS=1951845052` (только OLEG)

**Что умеет:**
- Отвечать на вопросы (через fallback chain)
- Команды: `/start`, `/health`, `/brain`, `/status`
- Логирует в `/var/log/hermes-alf.log` (если настроен)

**Hardening:** бот не пускает левых пользователей (whitelist).

---

## 8. ИНТЕГРАЦИИ

| С кем | Как |
|---|---|
| **Hermes (CLI)** | HTTP POST :8451/chat (локально) |
| **Qwen2api** | HTTP :8765/v1 (smanx/qwen2api — guest mode, free) |
| **MiniMax** | HTTPS api.minimax.io (облако, платный) |
| **Telegram** | Long polling через @IlonAnalyticBot |

---

## 9. WATCHDOG

`hermes-watchdog.sh` (каждые 30 сек) проверяет:
- `qwen2api` процесс + endpoint `/v1/models`
- `hermes-alf` активность
- При падении — `systemctl restart` + алерт в Telegram

---

## 10. БЭКАПЫ / ЛОГИ

| Файл | Что |
|---|---|
| `/root/matryoshka/alf/alf_server.py.bak.zaglushka` | backup 06.06 |
| `/root/matryoshka/alf/alf_telegram_bot.py.bak.*` | 3 backup (06-07.06) |
| `/var/log/hermes-alf.log` | runtime лог |
| journald `hermes-alf` | systemd журнал |

---

## 11. ИЗВЕСТНЫЕ ПРОБЛЕМЫ / TODO

- [ ] Нет rate-limit на /chat (можно DDoS-ить MiniMax)
- [ ] qwen2api использует guest mode (без авторизации) — может сломаться
- [ ] Telegram-бот только для OLEGа (не multi-tenant)
- [ ] Health endpoint не показывает uptime/память (только статус)

---

**Итог:** ALF = стратегический агент Белого Роя. Тонкий (5.7 MB), живучий (5 дней без рестарта), 3-уровневый fallback на случай падения основного мозга.
