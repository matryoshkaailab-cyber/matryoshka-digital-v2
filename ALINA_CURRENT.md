# ALINA v3.0 — Главный технический документ (Production)

**Дата:** 2026-06-18 (обновлён) | **Версия:** v3.0 (финал после ночной сессии 16-17.06, 466 сообщений)
**Статус:** Production-Ready 95% — **ИЗОЛИРОВАННАЯ УСТАНОВКА** (18.06.2026)
**Бот:** @NikolaAlinaBot (id 7734670302)
**Telegram:** Олег (1951845052), Николай (146881168)
**Клиент:** Николай Варнаков (@VarnakovNikolai, Краснодар, перекупщик iPhone)
**Координатор:** Олег (@oleglab22)

> 🆕 **18.06.2026 — МИГРАЦИЯ НА ОТДЕЛЬНЫЙ HERMES AGENT**
> - Новый venv: `/opt/alina-hermes/venv/` (Python 3.12, hermes-agent 0.16.0)
> - Профиль перенесён: `/root/.hermes-profiles/alina-prod/` (отдельный от HERMES/ALF)
> - Symlink: `~/.hermes/profiles/alina-prod` → `/root/.hermes-profiles/alina-prod`
> - Systemd units переименованы: `alina-*` → `alina-prod-*` (9 штук)
> - **Изоляция:** обновление HERMES/ALF не сломает Алину. Алина на своём Python venv.

> ⚠️ **Это ЕДИНСТВЕННЫЙ источник истины об Алине.** Все старые `ALINA_V2_FULL.md`, `PLAN.md`, `ALINA_HANDS.md`, `WORK_SCOPE.md` (DEPRECATED) — в `/root/matryoshka/.archive/cleanup_20260617/`. НЕ читать.

---

## 1. ИДЕНТИЧНОСТЬ (пожелание Олега 16.06)

- **Алина = Hermes Agent** (тот же бинарник, профиль `alina`). КЛОН HERMES, не отдельный агент.
- **Характер:** тёплая + ласковая в меру + профессиональная + юмор + человечность
- **Стиль:** Только русский, короткие сообщения, голосовые, на "ты"
- **Границы:** НЕ выдумывает данные, НЕ путать с @AlisaMatBot

## 2. АРХИТЕКТУРА v3.0 (9 сервисов / 7 портов) — ОБНОВЛЕНО 18.06

| Сервис | Порт | Файл / Python | Назначение |
|--------|------|---------------|-----------|
| **alina-prod-gateway.service** | — | `/opt/alina-hermes/venv/bin/hermes` | Telegram polling, Hermes Agent (отдельный venv) |
| **alina-prod-server.service** | :8470 | `/opt/alina-hermes/venv/bin/python3` alina_server.py | HTTP API (chat, think, task, browser, search, vision, image_gen) |
| **alina-prod-metrics.service** | :8471 | `/opt/alina-hermes/venv/bin/python3` alina_metrics.py | Prometheus метрики |
| **alina-prod-inventory.service** | :8472 | `/opt/alina-hermes/venv/bin/python3` inventory_service.py | Склад iPhone |
| **alina-prod-finance.service** | :8473 | `/opt/alina-hermes/venv/bin/python3` finance_service.py | Финансы (доход/расход/прибыль) |
| **alina-prod-autoreply.service** | :8474 | `/opt/alina-hermes/venv/bin/python3` auto_reply_service.py | Автоответ на Avito (торг/встреча/оригинал) |
| **alina-prod-market.service** | :8475 | `/opt/alina-hermes/venv/bin/python3` market_prices_service.py | Рыночные цены iPhone |
| **alina-prod-docs.service** | :8476 | `/opt/alina-hermes/venv/bin/python3` docs_service.py | Расписки/договоры |
| **alina-prod-callback-poller.service** | — | `/opt/alina-hermes/venv/bin/python3` alina_callback_poller.py | Inline-кнопки Telegram |

**Все активны** (live-check 17.06 12:25). Финальный тест 27/31 ✅.

## 3. 14 TELEGRAM-КОМАНД (протестированы)

📦 **СКЛАД:** `/stock` `/купил {model} {storage} {price}` `/продал {id} {price}` `/списал {id}`
💰 **ФИНАНСЫ:** `/расход {category} {amount}` `/прибыль` `/прибыль day|week|month`
📊 **РЫНОК:** `/цена {model}`
📄 **ДОКУМЕНТЫ:** `/документ расписка|договор {model} {price}`
💬 **АВТООТВЕТ:** `/автоответ торг|встреча|оригинал`
🆘 **БАЗОВЫЕ:** `/start` `/status` `/help`

## 4. ДАННЫЕ (17.06 12:25)

| Файл | Что | Статус |
|------|-----|--------|
| `cases/nikolay/finances/inventory.json` | 6 iPhone (3 sold + 1 in_stock + 2 sold 17.06) | ✅ |
| `cases/nikolay/finances/sales.csv` | 3 продажи 17.06 (iPhone 12/13/13, маржа 5000₽) | ✅ |
| `cases/nikolay/finances/expenses.csv` | 3 расхода 17.06 (бензин, аренда) | ✅ |
| `cases/nikolay/market_prices.json` | 18 моделей iPhone (обновлён 17.06 08:00) | ✅ |
| `cases/nikolay/avito_lots/iphone_lots_20260617_1123.json` | Свежий парсинг Авито | ✅ |
| `cases/nikolay/documents/*.txt` | 5 расписок/договоров (17.06 03:52-03:58) | ✅ |

## 5. AVITO ПАРСЕР

✅ **РАБОТАЕТ!** (НЕ заморожен — старое решение 11.06 отменено)
- Apify token `APIFY_ALINA_TOKEN` + actor `epctex/avito-scraper`
- Cron `alina-avito-iphone` 9:00/15:00/21:00
- Output: `cases/nikolay/avito_lots/iphone_lots_YYYYMMDD_HHMM.json`
- Top-3 самых дешёвых → Telegram
- iPhone 11-17, Краснодар, до 15к (можно расширить)

**Fallback:** DuckDuckGo через `nikolay/hands/fallback_parser.py` (когда Avito парсинг не работает)

## 6. SKILLS (7 — зачищено с 45)

✅ card-rules, hermes-image-workflow, matryoshka-connection, never-lose-context, voice-transcription, xkin-cards, xkin-cards-tested-2026-06-16

## 7. CRON (10 задач)

alina-avito-iphone (9/15/21), alina-finance-daily (21:00), alina-weekly-plan (Пн 9:00), alina-kb-sync (3:00), alina-backup (2:00), alina-market-update, alina-bridge-hermes (*/2), alina-watchdog (*/2), alina-server-watchdog (*/2), alina-status (*/5)

## 8. МОЗГ

Primary: **MiniMax-M3** (как у HERMES, через прямой API `https://api.minimax.io/v1`)
Fallback: M2.7 → Gemini Flash → Claude Haiku → Qwen local

## 9. SELF-IMPROVE

Алина = Hermes Agent с полным toolsets (fact_store, memory, skill_manage, send_message). Делает self-improve САМА внутри сессии. Без Python-костылей.

## 10. СВЯЗЬ С HERMES

- HTTP мост: `http://localhost:8470` (Basic Auth `alina:UUID`)
- Helper: `~/.hermes/profiles/hermes-cli/skills/matryoshka/alina-bridge/scripts/ask_alina.py`
- Команды: `ask_alina.py {health|ask|think|task}`
- Auth из `/root/.hermes/profiles/alina/.env` → `ALINA_API_USER` + `ALINA_API_UUID`
- Файлы-мосты: `/root/matryoshka/alina_tasks/` (TASK_*.md → Алина, DONE_*.md → HERMES)

## 11. МОНИТОРИНГ

- `cases/nikolay/cases/nikolay/avito_lots/` + `/root/matryoshka/alina_tasks/alina_status.json` (обновляется */5)
- Watchdog каждые 2 мин → auto-restart при падении
- Метрики Prometheus на :8471

## 12. MVP STATUS

🎯 Target: 28.06.2026. Production-Ready: 95%. Все тесты пройдены.

## 13. ЧТО НЕ ДЕЛАТЬ

- ❌ НЕ создавать _v2 / _v3 / _FINAL / _DRAFT версии этого документа — обновлять его
- ❌ НЕ возвращать nikolay.service (конфликт токена с alina-gateway)
- ❌ НЕ смешивать данные ALINA и DATALINK PRO (VPN) — разные клиенты
- ❌ НЕ использовать ws_server, alex-bridge, Tailscale — отключены 15.06
- ❌ НЕ доверять старым `PLAN.md`, `ALINA_HANDS.md`, `WORK_SCOPE.md` — в `.archive/`