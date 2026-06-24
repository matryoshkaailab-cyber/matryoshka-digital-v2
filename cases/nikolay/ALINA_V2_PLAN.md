# АЛИНА v2.0 — План переделки (Production-Ready)

**Дата:** 2026-06-16
**Автор:** HERMES
**Заказчик:** Олег (Директор MATRYOSHKA DIGITAL)
**Цель:** Заменить пустышку на умного бота-напарника для Николая (бизнес iPhone/XKIN)
**Target MVP:** 28.06.2026
**Статус:** План на согласовании (правим вместе)

---

## 1. ТЕКУЩЕЕ СОСТОЯНИЕ

| Проблема | Сейчас | Должно быть |
|----------|--------|-------------|
| Код | Нет `alina_bot.py` (только Hermes gateway) | Отдельный сервис `alina.service` |
| SOUL | Врёт про @AlisaMatBot | @NikolaAlinaBot (id 7734670302) |
| Модель | Через Hermes gateway | Прямое подключение z.ai Coding Plan |
| Парсинг | Папка `avito/` есть, код непонятен | Отдельный модуль |
| Карточки | Не реализовано | xkin-cards + OpenRouter Gemini |
| Голос | "SvetlanaNeural" без ключа | TTS MiniMax-M3 (или Yandex) |
| Cron | 2 задачи | 9 задач |
| MCP | Не подключены | n8n, browser, exa |
| Связь с HERMES | Нет | ACP-style канал + heartbeat |
| Memory | 1.2 GB у Hermes (утечка) | Чистый процесс < 500 MB |

---

## 2. ЦЕЛЕВАЯ АРХИТЕКТУРА

```
VPS 85.137.166.209
├── HERMES (я) — Дирижёр
│   └── ACP-style канал → ALEX (ПК, 10.8.1.4:4096)
│
├── АЛИНА v2.0
│   ├── alina_server.py (HTTP API :8470)
│   ├── alina_telegram_bot.py (Telegram)
│   ├── alina_avito.py (парсер + API)
│   ├── alina_cards.py (генератор карточек)
│   ├── alina_voice.py (TTS/STT)
│   ├── alina_finance.py (учёт)
│   ├── alina_knowledge.py (refresh_context)
│   └── skills/ (symlinks на мои скиллы)
│
└── Telegram @NikolaAlinaBot → Николай @VarnakovNikolai
```

---

## 3. МОДУЛИ (что вшить)

| Модуль | Порт/Файл | Что делает |
|--------|-----------|-----------|
| `alina_server.py` | :8470 | HTTP API для HERMES + health/chat/think/task |
| `alina_telegram_bot.py` | polling | Telegram бот, handlers, команды |
| `alina_avito.py` | — | Парсер (Selenium + API) |
| `alina_cards.py` | — | Генератор карточек через OpenRouter Gemini 2.0 |
| `alina_voice.py` | — | TTS (MiniMax-M3) + STT (Groq Whisper) |
| `alina_finance.py` | — | /куп /прод /отчёт /маржа, CSV, daily_report.md |
| `alina_knowledge.py` | — | refresh_context (мандат v3.3) |

**Fallback chain (мозг):**
1. Qwen 3.7 Max (через qwen2api :8765)
2. Qwen 3.7 Plus
3. **MiniMax-M3** (z.ai coding/paas/v4)
4. DeepSeek-v4-flash-free (opencode-zen)

---

## 4. СКИЛЛЫ (symlinks на мои)

| Скилл | Зачем |
|-------|-------|
| `matryoshka-connection` | Связь с HERMES |
| `alex-connection` | Делегация Аликсу |
| `n8n-task-runners` | n8n workflows |
| `hermes-image-workflow` | Генерация карточек |
| `xkin-cards` | Алгоритм карточек XKIN |
| `product-card-generator` | Общий алгоритм |
| `gemini-image-workflow` | OpenRouter fallback |
| `card-rules` | Инфографика |
| `gateway-orphan-detection` | Самовосстановление |
| `dependency-monitor` | Мониторинг cookies |
| `voice-transcription` | STT |
| `multi-agent-production-ops` | Оркестрация |

---

## 5. CRON ЗАДАЧИ (расписание)

| Cron | Скрипт | Что делает |
|------|--------|-----------|
| `*/5 * * * *` | `alina_heartbeat.sh` | Ping HERMES |
| `*/30 * * * *` | `alina_avito_monitor.sh` | Парсить новые лоты |
| `0 21 * * *` | `alina_daily_report.sh` | Финансы дня → Telegram |
| `0 9 * * 1` | `alina_weekly_plan.sh` | Понедельник: план продаж |
| `0 3 * * *` | `alina_kb_sync.sh` | Обновить research/ |
| `0 0 1 * *` | `alina_monthly_close.sh` | Закрытие месяца |
| `*/15 * * * *` | `alina_429_monitor.sh` | 429 → смена proxy |
| `0 2 * * *` | `alina_backup.sh` | Бэкап CSV/knowledge |
| `0 4 * * 0` | `alina_weekly_audit.sh` | Воскресенье: Олегу отчёт |

---

## 6. MCP СЕРВЕРЫ

| MCP | Зачем |
|-----|-------|
| `n8n` | Workflows (Avito API, finance, knowledge) |
| `browser` | Парсинг Avito fallback |
| `exa-search` | Поиск новинок iPhone/XKIN |
| `notebooklm` | База знаний (если есть OAuth) |
| `nano-pdf` | PDF-отчёты Николаю |

---

## 7. СВЯЗЬ С HERMES

- **Канал**: HTTP API :8470 (Basic Auth как у ACP)
- **Heartbeat**: каждые 5 мин (cron)
- **Файлы-мосты**: `/root/matryoshka/alina_tasks/`
- **Алина может просить у HERMES**: аудит, стратегия (ALF-стиль), делегацию Аликсу

---

## 8. ЭТАПЫ (10 дней, target 28.06)

| День | Дата | Что делаем |
|------|------|-----------|
| 1 | 16.06 (сегодня) | Фундамент: папка, alina_server.py скелет, systemd, тест /health |
| 2 | 17.06 | Telegram бот: handlers, /start /status /help, TTS/STT |
| 3 | 18.06 | Финансы: /куп /прод /отчёт /маржа, CSV |
| 4 | 19.06 | Avito парсер: Selenium + cookies (от Николая) |
| 5 | 20.06 | Карточки: OpenRouter Gemini 2.0 + xkin-cards |
| 6 | 21.06 | Скиллы (symlinks) + 9 cron + MCP |
| 7 | 22.06 | Связь с HERMES: ACP-style :8470 |
| 8-9 | 23-24.06 | E2E тесты, полировка, документация |
| 10 | 25.06 | Сдача MVP (3 дня буфер до 28.06) |

---

## 9. РЕСУРСЫ

| Что | Статус |
|-----|--------|
| VPS | ✅ Уже есть |
| API ключи | ✅ z.ai, MiniMax-M3, Apify, Groq |
| Время | ~10 дней |
| **От Олега** | Решение по TTS (MiniMax-M3 или Yandex) |
| **От Николая** | Avito cookies, тестовые фото iPhone |

---

## 10. РИСКИ

| Риск | Митигация |
|------|-----------|
| Avito блокирует IP | Residential proxy (Apify) |
| z.ai rate limit | Fallback chain |
| Николай не даст cookies | Selenium + ручной вход |
| Карточки плохие | A/B тест + PIL fallback |
| Memory leak | Мониторинг + restart по oom |

---

## ❓ ОТКРЫТЫЕ ВОПРОСЫ (правим вместе)

1. **Голосовое:** MiniMax-M3 (бесплатно) или Yandex SpeechKit (нужен ключ)?
2. **Hermes с 1.2 GB memory:** гасить или оставить?
3. **Avito cookies от Николая:** сначала Selenium без cookies, или ждём?
4. **MCP notebooklm:** есть Google OAuth?
5. **Скилл `voice-transcription` через Groq** — оставить или заменить на локальный Whisper?
6. **Target MVP 28.06 — реалистично?** Или нужен запас 5-7 дней?
7. **Стоимость:** все ключи уже оплачены или нужно докупать?
8. **Backup стратегия:** куда бэкапить (Яндекс.Диск / S3 / локально)?

---

**Согласовано:** ⬜ Олег
**Версия:** v0.1 (черновик)
**Следующий шаг:** Олег правит открытые вопросы, потом День 1
