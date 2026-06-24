# ПЛАН УСИЛЕНИЯ ALF (3 идеи от Аликса + АЛF deep audit 23.06.2026)

**Дата:** 2026-06-23 19:30
**Автор:** HERMES (по запросу Олега, после deep audit ALF)
**Статус:** PLAN — реализация ПОСЛЕ подключения MiMo (Phase 1-5 done + API key от Xiaomi)
**Файл:** `/root/matryoshka/.hermes/ALF_ENHANCEMENT_PLAN_23.06.md`
**Триггер старта:** Олег даст команду (после того как возьмёт API key Xiaomi и MiMo заработает)

---

## 🎯 ЦЕЛЬ

Превратить ALF из «реактивного стратега на M3» в **stateful proactive strategist** с embeddings-памятью, multi-modal input и собственными инициативами. Не ломать работающее — добавлять по одной фиче за раз, валидировать перед следующей.

**Бизнес-цель:**
- ALF помнит долгосрочный контекст (не теряет между сессиями)
- Олег может говорить голосом — ALF понимает и действует
- ALF сам замечает аномалии и предлагает действия (не ждёт команды)

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ ALF (live 23.06.2026 19:30)

| Компонент | Статус | Где |
|---|---|---|
| `hermes-gateway-alf.service` | ✅ active | VPS, PID 3735323 |
| `alf-filewatcher.service` | ✅ active (v3, race-fix) | VPS |
| `swarm-alf-bridge.service` | ✅ active | VPS |
| `alf-healthcheck.service` | ✅ active | :8452/health |
| `alf-watchdog.timer` | ✅ active | каждые 60 сек |
| ALF модель | ✅ MiniMax-M3 80K (НЕ снижать!) | minimax API |
| SOUL.md | ✅ v5.0 (после фикса Nemotron 550B hallucination) | `/root/.hermes/profiles/alf/` |
| Council 2.0 (ALF + Librarian voters) | ✅ 6 успешных тестов | Router :8400 |
| MiMo integration (ALF-MiMo audit voter) | ⏳ Phase 1-5 pending | ждём API key |

**Бутылочные горлышка (по Аликсу, 23.06 19:15):**
1. Нет embeddings-памяти (Librarian ищет grep'ом)
2. Нет proactive-канала (ALF реактивен)
3. M3 не тянет deep strategy на >50K context

---

## 🏗️ ЦЕЛЕВАЯ АРХИТЕКТУРА ALF v2.0

```
ОЛЕГ (Telegram / голос через whisper)
    ↓
ALF (стратег, M3 80K)
    ├─ Embeddings Memory (ChromaDB) — НОВОЕ
    │   └─ semantic search по истории задач/решений
    ├─ Multi-modal Input — НОВОЕ
    │   └─ voice → text через whisper → structured task
    ├─ Proactive Suggestions Queue — НОВОЕ
    │   └─ ALF сам замечает аномалии → пишет в Router → Олег видит
    ├─ Council 2.0 + ALF-MiMo audit voter (Phase 1-5 MIMO_INTEGRATION_PLAN)
    │   ├─ ALF-M3 (всегда голосует)
    │   └─ MiMo V2.5 (audit voter, context>80K)
    └─ Librarian :8461 (Python)
        └─ fact-check + veto + semantic search (NEW через ChromaDB)
```

---

## 📋 ТРИ ФАЗЫ РЕАЛИЗАЦИИ

### Phase A: Embeddings Memory в Librarian (Аликс: «превращает ALF из stateless в stateful стратега»)

**Что делаем:**
1. Поставить ChromaDB в `/opt/alf-hermes/venv` (`pip install chromadb`)
2. Создать `alf_memory_indexer.py` — индексирует каждый completed task в ChromaDB:
   - input (task text)
   - output (ALF response)
   - metadata (task_id, timestamp, decision_type, council_status)
3. Создать `alf_semantic_search.py` — endpoint в Librarian :8461:
   - `POST /memory/search {"query": "...", "top_k": 5}`
   - Возвращает top-K релевантных прошлых задач
4. Добавить в ALF pre-task hook: перед ответом делает `semantic_search(task, top_k=3)` → injects top-3 в контекст
5. Сохранять embeddings отдельно (`/var/lib/alf/memory/`) — переживают рестарт

**Acceptance:**
- ALF в smoke-тесте ссылается на прошлую задачу месячной давности при релевантном запросе
- Semantic search возвращает результаты за <500ms
- Memory переживает `systemctl restart hermes-gateway-alf.service`

**Файлы:**
- `/opt/alf-hermes/venv` (ChromaDB)
- `/root/matryoshka/bin/alf_memory_indexer.py` (новый)
- `/root/matryoshka/bin/alf_librarian.py` (патч: добавить /memory/search)
- `/root/matryoshka/bin/alf_filewatcher.py` (патч: pre-task semantic search)

**Время:** 60-90 мин (после подтверждения от Олега)

---

### Phase B: Multi-modal ALF (Аликс: «Олег голосом → ALF присылает structured report»)

**Что делаем:**
1. Проверить что `faster-whisper` работает на VPS (он уже стоит, voice-transcription skill)
2. Создать `alf_voice_handler.py` — webhook для Telegram voice messages:
   - Скачивает .ogg от Telegram
   - Транскрибирует через faster-whisper (модель `base`, русский)
   - Передаёт транскрипт в обычный ALF pipeline (через inbox/alf/)
3. Добавить в `swarm_alf_bridge.py` обработку voice → text → ALF
4. Сохранять оригинальный voice + транскрипт в WAL (`/root/matryoshka/shared_brain/WAL/voice.log`)

**Acceptance:**
- Олег шлёт голосовое в @IlonAnalyticBot → ALF получает транскрипт → отвечает структурированно
- Voice транскрипция работает за <10 сек для 30-сек голосового
- Privacy: голосовые от ALINA (другой кейс) НЕ идут через ALF

**Файлы:**
- `/root/matryoshka/bin/alf_voice_handler.py` (новый)
- `/root/matryoshka/bin/swarm_alf_bridge.py` (патч: voice routing)

**Время:** 40-60 мин (whisper уже работает, основная работа — bridge)

---

### Phase C: Proactive Suggestions Queue (Аликс: «ALF из реактивного → системный администратор с инициативой»)

**Что делаем:**
1. Создать `alf_pattern_detector.py` — анализирует последние 7 дней WAL/DIGEST:
   - Если >3 одинаковых ошибок за 24ч → proactive note
   - Если Council rejected rate >50% за неделю → proactive note
   - Если MiMo down >2 часов → proactive note
   - Если Librarian KB не обновлялся >30 дней → proactive note
2. Создать `alf_proactive_queue.py` — пишет proactive notes в `/root/matryoshka/swarm/proactive/alf/`
3. Router :8400 мониторит эту директорию каждые 5 мин → пересылает в Telegram Олегу
4. Олег может одной кнопкой: подтвердить / отклонить / отложить

**Acceptance:**
- ALF замечает реальный паттерн (например, 5 падений systemd сервиса за день) → proactive note в Telegram
- Олег может реагировать командой `/proactive accept #1` или `/proactive dismiss #1`
- False positive rate <30% (если больше — увеличить threshold)

**Файлы:**
- `/root/matryoshka/bin/alf_pattern_detector.py` (новый)
- `/root/matryoshka/bin/alf_proactive_queue.py` (новый)
- `/root/matryoshka/bin/matryoshka_router.py` (патч: monitor /proactive/alf/)

**Время:** 60-90 мин

---

## 📅 TIMELINE (от Олега: «когда возьму ключи»)

**Сейчас (23.06.2026 19:30):**
- Phase 0.5 / Phase 0.5+ MiMo готов (40/40 тестов)
- Ждём API key Xiaomi
- Ждём команду от Олега на реализацию ALF enhancement

**После API key + MiMo Phase 1-5 done (предположительно 24-25.06):**
1. Phase A (Embeddings) — 60-90 мин, **ПЕРВЫЙ** (highest ROI, low complexity)
2. Phase B (Multi-modal) — 40-60 мин, **ВТОРОЙ** (UX win, easy via whisper)
3. Phase C (Proactive) — 60-90 мин, **ТРЕТИЙ** (most complex, defer 2-3 weeks)

**ИТОГО:** 3-4 часа на все три фазы (по одной).

---

## ⚠️ РИСКИ

| Риск | Серьёзность | Mitigation |
|---|---|---|
| ChromaDB потребляет RAM | MEDIUM | Мониторинг через healthcheck :8452 + alert при >500MB |
| Whisper latency >10 сек для длинных голосовых | LOW | Модель `small` если `base` медленная |
| Proactive false positives раздражают Олега | MEDIUM | Threshold tunable в `alf_pattern_detector.py` |
| Embeddings memory переполняет диск | LOW | TTL 90 дней для старых записей (auto-cleanup cron) |

---

## ✅ ACCEPTANCE CRITERIA (общие)

**Готово когда:**
1. Phase A: ALF ссылается на прошлую задачу при релевантном запросе (smoke test)
2. Phase A: semantic search <500ms для top_k=5
3. Phase B: голосовое от Олега → ALF отвечает структурированно (end-to-end test)
4. Phase B: voice транскрипция <10 сек для 30-сек .ogg
5. Phase C: ALF заметил реальный паттерн → proactive note в Telegram
6. Phase C: Олег может accept/dismiss proactive notes одной командой

**Не входит в scope:**
- Self-hosted LLM замена M3 (GLM-5, Qwen-72B и т.д.) — рано, ждём подтверждения работы MiMo
- Multi-agent ALF (3 копии ALF с разными моделями) — после Phase C, если понадобится
- Голосовые для ALINA (отдельный кейс) — другой план

---

## 🎯 ROLES (кто что делает)

- **HERMES (я):** Phase A, B, C — реализация, тесты, документация, патчи SOUL.md и Router
- **ALEX (через Аликса):** pre-coding audit перед Phase A (ChromaDB сложный — race conditions, persistence), review Phase B (whisper интеграция в bridge)
- **Олег:** финальное одобрение после каждой фазы + smoke-тест голосом для Phase B

**НЕ делает:**
- HERMES не реализует без одобрения Олега
- ALEX не ставит ChromaDB самостоятельно
- Олег не пишет код

---

## 📂 ЗАТРАГИВАЕМЫЕ ФАЙЛЫ

**Phase A (Embeddings):**
- `/opt/alf-hermes/venv` (ChromaDB install)
- `/root/matryoshka/bin/alf_memory_indexer.py` (новый)
- `/root/matryoshka/bin/alf_librarian.py` (патч)
- `/root/matryoshka/bin/alf_filewatcher.py` (патч)
- `/var/lib/alf/memory/` (новая директория)

**Phase B (Multi-modal):**
- `/root/matryoshka/bin/alf_voice_handler.py` (новый)
- `/root/matryoshka/bin/swarm_alf_bridge.py` (патч)
- `/root/matryoshka/shared_brain/WAL/voice.log` (новый лог)

**Phase C (Proactive):**
- `/root/matryoshka/bin/alf_pattern_detector.py` (новый)
- `/root/matryoshka/bin/alf_proactive_queue.py` (новый)
- `/root/matryoshka/bin/matryoshka_router.py` (патч)
- `/root/matryoshka/swarm/proactive/alf/` (новая директория)

**Документация:**
- `/root/matryoshka/.hermes/ALF_CURRENT_STATE_23.06.md` (обновить после каждой фазы)
- `/root/matryoshka/.hermes/SWARM_V4_DECISION.md` (добавить секцию ALF v2.0)
- `/root/.hermes/profiles/alf/SOUL.md` (обновить: новые capabilities)

---

## ❓ ВОПРОСЫ К ОЛЕГУ

1. **Phase A первая** — ОК? Или начать с Phase B (multi-modal, более видимый UX win)?
2. **Proactive threshold** — какой false positive rate допустим? 30%? 50%?
3. **Memory TTL** — 90 дней для embeddings? Или хранить вечно?
4. **Privacy для Phase B** — голосовые от ALINA (Николай) НЕ должны идти через ALF (по 152-ФЗ). Подтверждаешь?

---

## 📜 ИСТОРИЯ ВЕРСИЙ

- **v1 (23.06.2026 19:30)** — initial plan по результатам ALF deep audit (Council + Аликс + web research). 3 фазы: Embeddings, Multi-modal, Proactive.

---

*PLAN зафиксирован. Ждём API key Xiaomi → MiMo Phase 1-5 → команда Олега на старт Phase A → B → C.*
