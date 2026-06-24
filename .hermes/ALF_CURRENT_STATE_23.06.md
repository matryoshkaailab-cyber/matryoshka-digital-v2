---
created: 2026-06-23
updated: 2026-06-23 (v4 — MiMo dual-stack добавлено)
tags: [alf, current-state, definitive, phase-1-done, phase-2-done, phase-0_5, mimo-dual-stack]------
---

# ALF — ТЕКУЩЕЕ СОСТОЯНИЕ (DEFINITIVE 23.06.2026 14:42, обновлено v4)

> ⚠️ **Это ГЛАВНЫЙ источник правды про ALF.** Если завтра спросят «что такое АЛЬФ?» — читай этот файл. Обновляется при каждом изменении АЛЬФ-стека.

---

## 🚀 PHASE 0.5 MIMO INTEGRATION (готов 23.06.2026 20:00)

**ALF получает MiMo dual-stack** — для длинных задач (context>80K) MiMo подключается как audit voter в Council 2.0.

**Что готово (40/40 unit-тестов зелёные):**
- `mimo_rate_limiter.py` (4/4) — token bucket 5 req/min, защита от бана Xiaomi
- `mimo_logger.py` (4/4) — JSONL logs + Prometheus metrics
- `mimo_privacy_filter.py` (7/7) — 25 правил (domain=personal, PII, sensitive теги)
- `mimo_query_async.py` (4/4) — asyncio.Semaphore wrapper + MIMO_DISABLED=1 kill switch
- `mimo_cost_ledger.py` (5/5) — трекинг usage Xiaomi (защита от paid tier)
- `mimo_context_bootstrap.py` (5/5) — inject shared_brain/DIGEST.md перед голосованием
- `mimo_fallback_integration_test.py` (4/4) — CircuitBreaker (3 fails → open → fallback)
- `council_v2.py` (7/7) — Council 2-way + опциональный MiMo audit voter (soft fail)

**Маршрутизация ALF:**
- `alf-fast` (M3, default): короткие задачи, /ask, /notebooklm, Telegram <200 chars
- `alf-deep` (MiMo, audit voter): ctx>80K или выход>400 строк (по ALF routing в ALF_STRATEGIC_PLAN_23.06.md)

**Rollback:** `systemctl stop mimo-acp` → Council = 2 voters, всё работает.

**Phase 1-5 план:** `/root/matryoshka/.hermes/MIMO_INTEGRATION_PLAN.md` (~2 часа после API key от Олега).

**DEFERRED фичи** (отложены в `ALF_ENHANCEMENT_PLAN_23.06.DEFERRED.md`): embeddings ChromaDB, multi-modal ALF, proactive suggestions queue.

---

## 🧠 КТО ТАКОЙ ALF

**ALF** (Analyst, Logician, Forecaster) — стратег и аналитик MATRYOSHKA DIGITAL.
White Swarm (Белый Рой — Мозг). Telegram: @IlonAnalyticBot.
Owner: Олег (@oleglab22, ID: 1951845052).

**Модель:** `minimax/MiniMax-M3` через `https://api.minimax.io/v1` (НЕ Nemotron 550B — это была старая ошибка SOUL.md v4.1, исправлена в v5.0).
**Контекст:** **80 000 токенов** (НЕ снижать до 60K — M3 имеет минимум, иначе "Failed to initialize agent").
**PID текущий:** 3735323 (после SIGKILL+restart 23.06 13:01)
**Memory:** ~307MB стабильно (НЕ 994MB peak — это была проблема до Phase 1)
**Мандат Олега 21.06:** «на опенроут ненадо» — НЕ переключать на OpenRouter/Nemotron.
**Ограничения M3:** плохо тянет длинные structured prompts (>400 chars), отвечает заголовком, теряет контекст. Поэтому все задачи АЛЬФ-у — КОРОТКИЕ (≤400 chars промпта, ≤500 chars ответа).

---

## 📂 ГДЕ ALF ЖИВЁТ

**systemd unit:** `hermes-gateway-alf.service`
**Команда:** `python -m hermes_cli.main --profile alf gateway run` (venv: `/opt/alf-hermes/venv`)
**Профиль:** `/root/.hermes/profiles/alf/`
**Telegram:** @IlonAnalyticBot (polling handler, токен в `.env`)
**Venv:** `/opt/alf-hermes/venv`

**5 процессов ALF:**
1. `hermes-gateway-alf.service` — main gateway (PID 3735323)
2. `alf-filewatcher.service` — FileWatcher v3 (PID 3404236)
3. `swarm-alf-bridge.service` — Bridge v2 → Telegram (PID 3403522)
4. `alf-healthcheck.service` — :8452 HTTP healthcheck (PID 3727729, добавлен 23.06)
5. `alf-watchdog.timer` + `alf-watchdog.service` — каждые 60 сек проверка (создан 23.06)

---

## 🔄 КАК ALF ОБРАБАТЫВАЕТ ЗАДАЧИ (FileWatcher v3)

**Цикл задачи** (НЕ только Telegram — это была ошибка старого SOUL.md):
1. HERMES пишет JSON в `inbox/alf/<task_id>.json` (atomic write)
2. `alf_filewatcher.py` v3 (race-fix): atomic claim через `.processing.PID.TIMESTAMP` → process → move to `.sent/`
3. ALF обрабатывает: `hermes -p alf chat -q "<question>" -Q` (timeout 300 сек)
4. Результат пишется в `outbox/alf/<task_id>.json`
5. `swarm_alf_bridge.py` (Bridge v2) перемещает в `outbox/alf/.notified/<task_id>.json.notified.<ts>`
6. Отправляет NOTIFY Олегу в Telegram @IlonAnalyticBot
7. Файл архивируется в `/root/matryoshka/swarm/archive/<task_id>.json`

**Turnaround:** 21-34 сек (был 22 сек в Phase 1)

---

## 📚 KNOWLEDGE BASE ALF

`/root/matryoshka/alf/knowledge/` — **44 файла** в 17 папках.

**Ключевые:**
- `23.06_AUDIT_AND_FIXES.md` (4.2 KB) — **АКТУАЛЬНАЯ ПРАВДА** (создан 23.06)
- `00_INDEX.md` — общий индекс (обновлён 23.06, ссылка на новый файл)
- `AGENTS/HERMES_SOUL.md` — про меня
- `agents/ALF_IMPROVEMENT_PLAN_2026-06-19.md` — план улучшений (последний от 19.06)
- `PRIORITY_PLAN.md` — устарел (Этап 1 завершён 18.06)

**Не трогал 42 старых файла** — работа на часы. Актуальная правда теперь в `23.06_AUDIT_AND_FIXES.md`.

---

## 🔐 ДОСТУПЫ И РАЗРЕШЕНИЯ ALF

### Что ALF МОЖЕТ
- Принимать задачи через Telegram (от Олега) и через `inbox/alf/*.json` (от HERMES)
- Запускать `hermes_cli.chat` с профилем `alf` (через FileWatcher)
- Использовать toolsets: research, browser, file, terminal, memory, session_search, skills
- Отправлять задачи АЛИКСУ через HERMES (через `.hermes_task_alf.json`)
- Писать в shared_brain WAL (после Phase 1 fix)

### Что ALF НЕ МОЖЕТ
- ❌ Docker, SSH на другие хосты (это АЛИКС)
- ❌ Править код Python в `matryoshka/`
- ❌ Общаться с Олегом напрямую (только через HERMES)
- ❌ Касаться данных ALINA (изоляция v3.2)
- ❌ Управлять ALISA (отложена)
- ❌ HTTP endpoints для внешних (ALF работает только через inbox/outbox + Telegram)
- ❌ Открывать новые порты

### Права доступа
- FileWatcher: read inbox/alf, write outbox/alf
- Bridge: read outbox/alf, write outbox/alf/.notified, send Telegram API
- shared_brain WAL: read shared_brain/DIGEST.md, append to shared_brain/WAL/alf.wal
- KB: read own knowledge/

---

## 🔗 СВЯЗИ С ДРУГИМИ АГЕНТАМИ

| Агент | Канал | Когда |
|---|---|---|
| **HERMES** | inbox/alf/*.json (от HERMES) и Telegram @IlonAnalyticBot (от Олега) | Всегда |
| **ALEX** | через HERMES (через `.hermes_task_alf.json`) | Тех. задачи, код |
| **ALISA** | — | ⏸ Отложена |
| **ALINA** | — | ❌ Не моя зона (изоляция v3.2) |
| **ALF-Библиотекарь** (:8461) | через Router :8400 (Council 2.0) | Для fact-check, veto |
| **MATRYOSHKA Router** (:8400) | через `inbox/alf/` (ALF query) | Council голосования |

---

## 🛡️ PHASE 1 — ЗАВЕРШЕНА (23.06.2026 12:50)

| Компонент | Файл | Статус |
|---|---|---|
| **Watchdog v2** | `/root/matryoshka/bin/alf_watchdog.sh` (5.4 KB) | ✅ active (каждые 60 сек) |
| **Healthcheck endpoint** | `/root/matryoshka/bin/alf_healthcheck.py` + service | ✅ :8452 /health, /metrics |
| **Context 80K** | `/root/.hermes/profiles/alf/config.yaml` | ✅ применён (60K ломает) |
| **Systemd units v2** | Restart=on-failure, EnvFile, PartOf | ✅ |
| **shared_brain WAL** | FileWatcher автоматически пишет в alf.wal | ✅ |
| **Knowledge update** | `/root/matryoshka/alf/knowledge/23.06_AUDIT_AND_FIXES.md` | ✅ |
| **SOUL.md v5.0** | `/root/.hermes/profiles/alf/SOUL.md` (8.4 KB) | ✅ |

---

## 🚀 PHASE 2 — ЗАВЕРШЕНА (23.06.2026 14:14)

| Компонент | Файл | Статус |
|---|---|---|
| **ALF-Библиотекарь** | `/root/matryoshka/bin/alf_librarian.py` (9.8 KB) | ✅ :8461 (Python-агент, не LLM) |
| **Router** | `/root/matryoshka/bin/matryoshka_router.py` v0.3 (18.7 KB) | ✅ :8400 (aiohttp) |
| **Council 2.0** | Router `/council` endpoint | ✅ работает (33-34 сек) |
| **ALF Healthcheck unit** | `alf-healthcheck.service` | ✅ active |
| **systemd unit Библиотекаря** | `alf-librarian.service` | ✅ active |
| **systemd unit Router** | `matryoshka-router.service` | ✅ active |

---

## 🧪 PHASE 2 ВАРИАНТ Б — COUNCIL 2.0 (23.06.2026 14:39)

**Council 2.0 цикл:**
1. HERMES вызывает `POST /council` с `decision`
2. Router генерирует `council_id`
3. Router параллельно: 
   - Отправляет ALF задачу в `inbox/alf/` (short prompt: "ЗА/ПРОТИВ одним предложением")
   - Вызывает Библиотекарь `/veto` (timeout 30s)
4. Polling ALF ответа в `outbox/alf/.notified/` + `archive/` каждые 2 сек
5. Когда ALF ответил (или timeout 90s) — финальный вердикт:
   - `librarian.veto=true` → rejected (Библиотекарь veto)
   - `alf_vote=against` → rejected (ALF против)
   - `alf_vote=for + librarian.ok` → accepted (оба за)
   - `alf null (timeout) + librarian.ok` → accepted (fallback)
6. Persist в `/root/matryoshka/council/logs/{council_id}.json`

**6 council тестов прогнали 23.06.2026 14:25-14:39:**
- #1: timeout fallback → accepted
- #2: ALF ПРОТИВ (Router SPOF) → rejected
- #3-5: timeout fallback → accepted (ALF ЗА с условиями)
- #6: 34.3s успех, ALF ЗА → accepted

**Баг найден и исправлен:** `Path.glob` имел race condition → заменён на `os.listdir`.

---

## 📝 ВЕРСИОННАЯ ИСТОРИЯ

- v1.0 (ALAN): standalone server :8451
- v2.0: telegram bot
- v3.0 (07.06): ECLER → ALINA, 3 РОЯ
- v4.0 (18.06): persona в Hermes (УСТАРЕЛО)
- v4.1 (20.06): **ОШИБКА** — говорил про Nemotron 550B, реально M3
- v5.0 (23.06.2026 ~12:50): **АКТУАЛЕН** — реальный стек (M3, 80K, FileWatcher v3, watchdog+healthcheck, WAL)
- v5.0 + Phase 2 (~14:14): добавлены ALF-Библиотекарь + Router + Council 2.0

---

## 🔧 ЧТО ЛОМАЕТ ALF (исторические баги)

1. **60K context → "Failed to initialize agent"** — не снижать ниже 80K для M3
2. **ALF галлюцинирует собственный стек** — SOUL.md v5.0 это лечит
3. **ALF не писал в shared_brain WAL с 19.06 по 23.06** — FileWatcher v3 fix восстановил
4. **M3 не тянет длинные structured prompts** — все задачи ≤400 chars
5. **Path.glob race condition** — был в Council polling, исправлено на os.listdir

---

## 📂 СВЯЗАННЫЕ ФАЙЛЫ (с актуальным состоянием)

- `SOUL.md` v5.0 (8.4 KB) — `/root/.hermes/profiles/alf/SOUL.md`
- `ALF_DEEP_AUDIT_23.06.md` (4 KB) — `/root/matryoshka/.hermes/`
- `ALF_ROLE_PROPOSAL_23.06.md` (7.2 KB) — `/root/matryoshka/.hermes/`
- `23.06_AUDIT_AND_FIXES.md` (4.2 KB) — `/root/matryoshka/alf/knowledge/`
- `matryoshka_router.py` v0.3 (18.7 KB) — `/root/matryoshka/bin/`
- `alf_librarian.py` (9.8 KB) — `/root/matryoshka/bin/`
- `alf_watchdog.sh` v2 (5.4 KB) — `/root/matryoshka/bin/`
- `alf_healthcheck.py` (6.4 KB) — `/root/matryoshka/bin/`
- `/root/matryoshka/council/logs/` — 6 council решений (23.06)

---

## 🔄 КАК ОБНОВЛЯТЬ ЭТОТ ФАЙЛ

**Триггер:** при ЛЮБОМ изменении ALF-стека (модель, контекст, процессы, endpoints, задачи, KB, SOUL.md)
**Действие:** обновить секцию + дату в `updated:`
**WAL:** после обновления записать в `shared_brain/WAL/hermes.wal` через `append_wal.py`

**Не делать:**
- ❌ Не дублировать в `AGENTS.md` (этот файл — authoritative)
- ❌ Не плодить _v2/_v3/_FINAL
- ❌ Не доверять старым KB файлам до 23.06 без cross-check
