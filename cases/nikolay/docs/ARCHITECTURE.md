# 🪆 ALINA v2.0 — Архитектура

**Версия:** 2.0 (17.06.2026)
**Статус:** Production-Ready
**Бот:** @NikolaAlinaBot (id 7734670302)
**Владелец:** Николай Варнаков (id 146881168)
**Оператор:** Олег Чут (id 1951845052)

---

## 📐 Общая схема

```
┌──────────────────────────────────────────────────────────┐
│                  ОЛЕГ (директор)                         │
│                  @oleglab22 (1951845052)                 │
└─────────────────────┬────────────────────────────────────┘
                      │ управляет
                      ↓
┌──────────────────────────────────────────────────────────┐
│              🪆 HERMES (дирижёр)                         │
│              VPS 85.137.166.209                          │
│              MiniMax-M3 (тот же)                         │
└─────────────┬──────────────────────────┬─────────────────┘
              │                          │
              │ alina_monitor            │ alina_status.json
              │ (каждые 5 мин)          │ (каждые 5 мин)
              ↓                          ↓
┌──────────────────────────────────────────────────────────┐
│              🪆 ALINA (бот Николая)                      │
│              @NikolaAlinaBot (7734670302)                │
│              MiniMax-M3 (тот же)                         │
│                                                          │
│  ┌─────────────────┐         ┌──────────────────┐       │
│  │ alina-gateway   │◄────────┤ Telegram polling │       │
│  │ (Hermes Agent)  │         │ @NikolaAlinaBot  │       │
│  └─────────────────┘         └──────────────────┘       │
│                                                          │
│  ┌─────────────────┐         ┌──────────────────┐       │
│  │ alina-server    │◄────────┤ HTTP API :8470   │       │
│  │ (Threading)     │         │ (от HERMES)      │       │
│  └─────────────────┘         └──────────────────┘       │
│                                                          │
│  ┌─────────────────┐         ┌──────────────────┐       │
│  │ 9 cron-задач    │         │ 7 skills         │       │
│  │ OS-уровень      │         │ (sales/voice/...)│       │
│  └─────────────────┘         └──────────────────┘       │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │ 3 watchdog (auto-restart)                       │     │
│  │  • alina-gateway  (15 сек)                      │     │
│  │  • alina-server   (10 сек)                      │     │
│  │  • alina-skills-loop (30 сек, 5 мин)            │     │
│  └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
                      │
                      ↓
┌──────────────────────────────────────────────────────────┐
│              НИКОЛАЙ (пользователь)                     │
│              @VarnakovNikolai (146881168)                │
│              Краснодар, продавец iPhone                  │
└──────────────────────────────────────────────────────────┘
```

## 🧩 Компоненты

### 1. Профиль `alina` (`/root/.hermes/profiles/alina/`)

| Файл | Назначение |
|------|-----------|
| `config.yaml` | Hermes Agent (10 toolsets, MiniMax-M3) |
| `SOUL.md` | Душа Алины (12.8 KB, тёплый характер) |
| `.env` | Секреты (API ключи, токены) |
| `memories/MEMORY.md` | Память между сессиями (3.7 KB) |
| `skills/` | 7 symlink-скиллов (только нужные) |
| `cron/` | 9 OS-скриптов (avito, finance, backup...) |

### 2. Системные сервисы (systemd)

| Сервис | Функция | Restart | Время |
|--------|---------|---------|-------|
| `alina-gateway.service` | Telegram polling, Hermes Agent | on-failure | 15 сек |
| `alina-server.service` | HTTP API :8470 | on-failure | 10 сек |
| `alina-skills-loop.service` | Чистка лишних skills (5 мин) | no | one-shot |
| `alina-skills-cleanup.timer` | Триггер каждые 5 мин | — | n/a |

### 3. Cron-задачи (9)

| Cron | Расписание | Скрипт | Назначение |
|------|------------|--------|------------|
| `alina-avito-iphone` | `0 9,15,21 * * *` | avito_monitor.py | Парсинг Авито (Apify) |
| `alina-finance-daily` | `0 21 * * *` | finance_daily.py | Daily отчёт → Telegram |
| `alina-weekly-plan` | `0 9 * * 1` | weekly_plan.py | План на неделю |
| `alina-kb-sync` | `0 3 * * *` | kb_sync.py | Knowledge base обновление |
| `alina-backup` | `0 2 * * *` | backup.py | Бэкап → Яндекс.Диск |
| `alina-bridge-hermes` | `*/2 * * * *` | bridge_to_hermes.py | Мост с HERMES |
| `alina-watchdog` | `*/2 * * * *` | watchdog.sh | Gateway auto-restart |
| `alina-server-watchdog` | `*/2 * * * *` | watchdog_server.sh | Server auto-restart |
| `alina-status` | `*/5 * * * *` | alina_status.sh | JSON для HERMES monitor |

### 4. Skills (7 — очищено с 45)

```
🔗 card-rules                       — Правила карточек
🔗 hermes-image-workflow            — Генерация фото
🔗 matryoshka-connection            — Связь с HERMES
🔗 never-lose-context               — Память
🔗 voice-transcription              — Голосовые (STT)
🔗 xkin-cards                       — Карточки iPhone
🔗 xkin-cards-tested-2026-06-16     — Рабочий pipeline
```

### 5. HTTP API `:8470`

| Endpoint | Auth | Метод | Описание |
|----------|------|-------|----------|
| `/health` | none | GET | Статус + uptime |
| `/chat` | basic | POST | Обычный диалог |
| `/think` | basic | POST | Глубокое мышление |
| `/task` | basic | POST | Задача от HERMES (сохранение в alina_tasks/) |

**Auth:** Basic Auth (ALINA_API_USER + ALINA_API_UUID)
**Primary:** MiniMax-M3 (прямой API, как у HERMES)
**Fallback:** MiniMax-M3 → M2.7 → Gemini Flash → Claude Haiku → Qwen local

### 6. Telegram (@NikolaAlinaBot)

| Параметр | Значение |
|----------|----------|
| Bot ID | 7734670302 |
| Username | @NikolaAlinaBot |
| HOME_CHANNEL | 146881168 (Николай) |
| Allowed users | 1951845052 (Олег), 146881168 (Николай) |
| Режим | Polling (webhook не установлен) |
| Gateway | alina-gateway (Hermes Agent) |

## 🔄 Поток данных

### Входящие сообщения

```
Николай → Telegram → @NikolaAlinaBot → alina-gateway
                                              ↓
                                       Hermes Agent
                                       (MiniMax-M3)
                                              ↓
                                       alina-server
                                       (если через API)
                                              ↓
                                       Ответ → Telegram
```

### Исходящие (от Алины)

```
Алина → Telegram Bot API → Николай
       (sendMessage)
```

### Мост с HERMES

```
HERMES → /root/matryoshka/alina_tasks/TASK_*.md → alina-bridge-hermes (каждые 2 мин)
ALINA → /root/matryoshka/alina_tasks/DONE_*.md  → HERMES мониторит
ALINA → /root/matryoshka/alina_tasks/alina_status.json → HERMES каждые 5 мин
```

## 💾 Хранение данных

| Где | Что |
|-----|-----|
| `/root/matryoshka/cases/nikolay/` | Бизнес-данные Николая |
| `/root/matryoshka/cases/nikolay/avito_lots/` | JSON лотов с Авито |
| `/root/matryoshka/cases/nikolay/finance/` | CSV (покупки, продажи) |
| `/root/matryoshka/cases/nikolay/knowledge/` | База знаний |
| `/root/matryoshka/alina_tasks/` | Мост с HERMES |
| `/root/.hermes/profiles/alina/memories/MEMORY.md` | Память Алины |
| `/var/log/alina_*.log` | Все логи |

## 🔐 Безопасность

- API ключи — в `.env` (chmod 600)
- HTTP API — Basic Auth (ALINA_API_UUID)
- Telegram — whitelist пользователей
- Бэкап — Яндекс.Диск (2:00 daily)
- Логи с персональными данными — НЕ в Telegram

## 📊 Метрики (для тест-драйва 17.06.2026)

| Тест | Результат |
|------|-----------|
| Smoke (5/5) | ✅ 100% |
| Stress (50/50) | ✅ 98% (1/50 fail) |
| Нагрузка (10 параллельно) | ✅ 9/10 (1.81 req/s) |
| Fallback chain | ✅ 4/5 моделей (qwen local пустой) |
| Watchdog gateway | ✅ 15 сек |
| Watchdog server | ✅ 9 сек |
| Watchdog SIGTERM | ✅ 2-3 мин (через cron) |
| Cron (9 задач) | ✅ Все exit=0 |
| Аварии (диск/RAM) | ✅ В пределах нормы |
| Утечки памяти | ✅ Нет (144 MB стабильно) |
