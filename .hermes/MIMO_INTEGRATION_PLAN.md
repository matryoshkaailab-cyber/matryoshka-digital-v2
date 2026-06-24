# ПЛАН ИНТЕГРАЦИИ MIMO CODE В РОЙ MATRYOSHKA

**Дата:** 2026-06-23 (v1) → 2026-06-23 18:05 (v2 после ALEX opinion-audit)
**Автор:** HERMES (по запросу Олега)
**Статус:** v2 — после opinion-аудита Аликса, на утверждении Олегом
**Файл:** `/root/matryoshka/.hermes/MIMO_INTEGRATION_PLAN.md`

---

## 🎯 ЦЕЛЬ (v2)

**DUAL-STACK, не замена.** Добавить MiMo Code (V2.5, 1M контекст) **параллельно** к ALF (M3 80K). Router (:8400) маршрутизирует задачи по контексту и privacy-тегам.

**Бизнес-цель:**
- ALF-MiMo для длинных задач (аудиты, стратегии, большие логи) — где M3 обрезает на 80K
- ALF-M3 для простых/быстрых задач — где M3 80K хватает
- **ALINA остаётся на M3** (Xiaomi cloud = нарушение 152-ФЗ для ПДн клиента Николая)
- Persistent memory между сессиями, Goal verification, Max Mode — для задач ALF-MiMo

**Ключевая фишка MiMo:** 1M контекст + persistent memory + Goal verification + Max Mode (5 кандидатов). Решает проблему M3 обрезки на 80K для длинных задач.

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ (проверено 23.06.2026 15:25-16:00)

| Компонент | Статус | Где |
|---|---|---|
| MiMo CLI 0.1.2 | ✅ установлен (VPS, Python wheel) | `/usr/local/lib/.../node_modules/@mimo-ai/cli/bin/mimo` |
| mimo_query адаптер | ✅ работает (subprocess, VPS) | `:8402` |
| mimo-query.service | ✅ active (VPS, fallback) | systemd |
| MiMo на ПК Олега | ⏳ будет после API key | `10.8.1.4:4197` (ACP через opencode) |
| 6 успешных live-тестов | ✅ сделано | stats: $0, 23.9K токенов |
| MiMo API key | ❌ нет | нужен от Xiaomi (Олег везёт) |
| mimo acp / mimo serve | ❌ не работает (баг 0.1.2) | workaround: opencode --acp на ПК |
| ALF M3 80K | ✅ работает | `:8452 healthcheck` |

---

## 🏗️ ЦЕЛЕВАЯ АРХИТЕКТУРА (v3 — MiMo на ПК Олега)

**Расположение (ALEX opinion-audit 23.06 18:15):** MiMo на ПК Олега, не на VPS.
- **Privacy**: VPS subprocess = ВСЕ данные через Xiaomi cloud (код, секреты, архитектура MATRYOSHKA). На ПК — контроль маршрутизации.
- **Latency**: ACP <100ms vs subprocess 5-15s overhead (50-150x разница).
- **Race conditions**: subprocess не починить asyncio.Lock (fork-exec race в stdin/stdout). ACP решает на уровне протокола.
- **Availability**: ALF уже привязан к ПК через Аликса (:4096). Если ПК выключен — ALF не работает независимо от MiMo.
- **Горячий резерв на VPS не нужен** — graceful degradation (MiMo down → weight=0, Council = 2 voters).

```
ОЛЕГ (Telegram)
    ↓
HERMES (M3, дирижёр, VPS :8400 Router)
    ├→ PRIVACY FILTER (этап 1 — до маршрутизации)
    │    └─ если domain=personal → ALF-M3 (НЕ MiMo, 152-ФЗ)
    ├→ ALF-M3 (MiniMax-M3 80K, @IlonAnalyticBot) — простые задачи, опросы
    ├→ ALF-MiMo (MiMo V2.5, 1M context, ACP через VPN)
    │    └─ 10.8.1.4:4197 на ПК Олега (opencode --acp --provider mimo:V2.5)
    ├→ ALEX (DeepSeek на ПК Олега) — тех. инженер
    └→ ALINA (M3 на отдельном профиле) — клиент Николай, ТОЛЬКО M3
```

**Изменения v3:**
- **MiMo на ПК Олега** через ACP (не VPS subprocess)
- opencode.json на ПК: добавить provider `mimo` (type=acp, url=http://127.0.0.1:4197/api)
- Router :8400 на VPS: добавить provider endpoint `/alf-mimo` → стучится на `10.8.1.4:4197` через VPN
- mimo_query.py на VPS — **FALLBACK** (опционально, для graceful degradation при ПК выключен)
- **ALINA остаётся на M3** (152-ФЗ privacy)
- Council 2.0 → 3-way (ALF-M3 + Библиотекарь + MiMo с soft-fail)

---

## 📋 ШАГИ РЕАЛИЗАЦИИ (v2 — dual-stack)

### Phase 0: Pre-requisites (Олег) — БЕЗ ИЗМЕНЕНИЙ
- [ ] Олег регистрируется на mimo.xiaomi.com
- [ ] Получает API key
- [ ] Передаёт API key (через env var или .env файл)
- **Время:** 10-30 мин (зависит от Xiaomi approval)

### Phase 0.5: CRITICAL PATH (HERMES, БЕЗ API KEY, 60-90 мин) ✅ NEW
> По правкам Аликса 23.06 18:05. Делаем пока Олег едет, чтобы при получении ключа всё подключилось за 5 мин.

- [ ] **mimo_rate_limiter.py** — token bucket, 5 req/min initial, configurable. Защита от бана Xiaomi API.
- [ ] **mimo_logger.py** — `/var/log/matryoshka/mimo/{request,error,audit}.log` + Prometheus метрики (`mimo_requests_total`, `mimo_latency_seconds`, `mimo_errors_total`).
- [ ] **mimo_privacy_filter.py** — middleware в Router: блокирует `domain=personal` / `[PRIVACY]` маркеры ДО отправки в MiMo. Логирует попытки.
- [ ] **asyncio.Lock в mimo_query.py** — один запрос за раз, остальные ждут в очереди. Fix race condition на stdout/stderr.
- [ ] **opencode.json dual provider** — две секции: `alf-m3` (основной) + `alf-mimo` (MiMo V2.5). Backup секция `alf-m3` для rollback.
- [ ] **council_v2.py → 3-way** — voter_config для MiMo: `{"weight": 1.5, "timeout": 60, "soft_fail": true, "veto_on": ["SECURITY_ISSUE", "DATA_LEAK"]}`. weight ×1.5 ТОЛЬКО для context >80K.
- [ ] Тесты Phase 0.5 на моках (без реального API) — все 6 модулей.
- **Acceptance:** 6/6 unit-тестов зелёные. mimo_query.py больше не даёт race conditions.

### Phase 1: Auth + ACP server (HERMES + Аликс на ПК, 30 мин) — ИЗМЕНЕНО v3
- [ ] Олег передаёт API key (через env var на ПК Олега)
- [ ] Аликс обновляет `opencode.json` на ПК — добавляет provider `mimo`:
  ```jsonc
  "providers": {
    "mimo": {
      "type": "acp",
      "url": "http://127.0.0.1:4197/api"
    }
  }
  ```
- [ ] Аликс поднимает MiMo ACP server на ПК: `opencode --acp --provider mimo:V2.5 --port 4197`
- [ ] systemd unit `mimo-acp.service` на ПК (Windows: NSSM wrapper или Task Scheduler)
- [ ] VPS тест: `curl http://10.8.1.4:4197/api/health` → 200 OK
- [ ] Тест: latency MiMo V2.5 vs M3 на одинаковом промпте 50K токенов
- **Acceptance:** mimo-acp отвечает на ПК за <60s, ping проходит через VPN
- **ROLLBACK:** `systemctl stop mimo-acp` на ПК (0 сек, Council возвращается к 2-voter)

### Phase 2: Router integration через VPN (HERMES на VPS, 30 мин) — ИЗМЕНЕНО v3
- [ ] Добавить в `matryoshka_router.py` provider `alf-mimo` → ACP на `10.8.1.4:4197` через VPN
- [ ] Privacy filter: `domain=personal` → ALF-M3, иначе → ALF-MiMo для context >80K
- [ ] mimo_query.py на VPS переводится в режим **FALLBACK** (только если ПК down)
- [ ] Обновить `/health` (aggregated) — добавить mimo-acp статус (probe 10.8.1.4:4197)
- [ ] Обновить `/docs` — добавить нового voter'а
- **Acceptance:** Router /alf-mimo работает через VPN, /health показывает mimo-acp:ok, privacy filter ловит тестовые sensitive/PII запросы

### Phase 3: Council 2-way + ALF-MiMo audit voter (HERMES + Аликс review, 30 мин) — переименовано по ALF review
> ALF заметил: "Council 3-way" misleading — MiMo weight ×1.5 только при ctx>80K = audit mode, не равноправный voter. Переименовано: **Council 2 voters (ALF-M3 + Библиотекарь) + ALF-MiMo audit voter для длинных задач**.

- [ ] Расширить `council_cycle()` в Router — MiMo подключается как **audit voter** (опциональный)
- [ ] Логика: 2 voters всегда работают (ALF-M3 + Библиотекарь). MiMo подключается ТОЛЬКО при `context_length > 80_000` и `task_type == "audit"` (по ALF routing: вход>40K ИЛИ выход>400 строк)
- [ ] SOFT FAIL: если MiMo timeout (>60s) или 5xx → weight=0, audit voter пропускается, 2 voters решают
- [ ] VETO: MiMo может veto только при `confidence > 0.95` и `category ∈ [SECURITY_ISSUE, DATA_LEAK]`
- [ ] При veto — финальный статус "rejected", 2 voters не могут override
- [ ] **Без MiMo Council = 2 voters (стабильно, как сейчас)** — MiMo не ломает работающее
- [ ] mimo_context_bootstrap.py injects shared_brain/DIGEST.md в MiMo prompt ПЕРЕД голосованием (ALF: "иначе голосует blind")
- **Acceptance:** Council #7+ показывает audit voter в логах (MiMo skipped для коротких, active для длинных), SOFT FAIL работает (test с отключённым mimo-acp → 2 voters OK)

### Phase 4: WAL integration (HERMES, 15 мин)
- [ ] `mimo-agent` пишет в shared_brain WAL после каждой задачи
- [ ] В Council 2.0 logs видно `mimo vote: for/against/skipped`
- **Acceptance:** `alf.wal` содержит записи mimo голосов

### Phase 5: Документация + AGENT_MAP (HERMES, 10 мин)
- [ ] Обновить `AGENT_MAP.md` — добавить ALF-MiMo как параллельного voter'а
- [ ] Обновить `ALF_CURRENT_STATE_23.06.md` — dual-stack MiMo интеграция
- [ ] Обновить `SWARM_V4_DECISION.md` — Phase 3 (MiMo dual-stack)
- [ ] Обновить `fact_store` — 4 новых факта про MiMo (dual-stack, privacy filter, rate limiter, EULA)
- **Acceptance:** везде актуальная правда про новую архитектуру

**ИТОГО:** Phase 0.5 (60-90 мин без API key) + Phase 1-5 (1.5-2 часа после получения API key).

**Phase 0.5+ расширения (по ALF review v3):**
- `mimo_cost_ledger.py` — трекинг usage Xiaomi (защита от paid tier trap)
- `mimo_context_bootstrap.py` — MiMo тянет shared_brain/DIGEST.md перед голосованием
- `MIMO_DISABLED=1` env — kill switch в mimo_query_async без systemctl restart
- Real fixtures для privacy_filter (PII / sensitive теги из реальных потоков: /start, voice transcripts, bookings)
- Co-ownership opencode.json с Аликсом (ALF замечание: ALEX bottleneck)

---

## ⚠️ РИСКИ (v2)

| Риск | Серьёзность | Mitigation |
|---|---|---|
| Xiaomi отключит API | HIGH | Готовим fallback на DeepSeek V3 через opencode |
| Xiaomi EULA ограничит коммерцию | **HIGH ✅ NEW** | **Юрист-проверка Xiaomi EULA ДО Phase 1.** Если запрещает — стоп |
| mimo acp / mimo serve не работает (0.1.2) | LOW v2 | Поднимаем MiMo как `opencode --acp --provider mimo` через бинарник MiMo |
| Xiaomi cloud privacy (152-ФЗ) | **HIGH ✅ NEW** | **PRIVACY FILTER на Router**: `domain=personal` / PII / sensitive → ALF-M3 (НЕ MiMo) |
| Rate limit Xiaomi API | **MEDIUM ✅ NEW** | `mimo_rate_limiter.py` 5 req/min + Prometheus метрики |
| Subprocess race conditions | **MEDIUM ✅ NEW** | `asyncio.Lock` в mimo_query.py (Phase 0.5) |
| M3 80K всё ещё нужен для простых задач | LOW v2 | Dual-stack: ALF-MiMo для длинных, ALF-M3 для быстрых (ОБА в рое) |
| Latency MiMo (cloud) | MEDIUM | Subprocess adapter был 5-15s overhead, ACP v2 — меньше |
| MiMo 0.1.2 баги (свежий релиз) | LOW | Мониторинг через mimo_logger.py + Prometheus. Готовы к rollback 0 сек |
| **MiMo down → Council deadlock** | LOW v2 | SOFT FAIL: weight=0 если MiMo timeout. Council = 2 voters fallback |

---

## ✅ ACCEPTANCE CRITERIA (v2)

**Готово когда:**

**Phase 0.5 (без API key):**
1. 6/6 модулей Phase 0.5 имеют unit-тесты (зелёные)
2. `mimo_rate_limiter.py` отклоняет 6-й запрос за минуту (тест)
3. `mimo_privacy_filter.py` блокирует `domain=personal` (тест)
4. `mimo_query.py` с asyncio.Lock — race condition тест зелёный
5. `mimo_logger.py` пишет в `/var/log/matryoshka/mimo/`
6. Council 3-way с MiMo soft-fail — Council принимает решения при MiMo down

**Phase 1-5 (после API key):**
7. `mimo-agent.service` active, ACP на :4197 отвечает ping за <60s
8. Router `POST :8400/alf-mimo` работает через ACP (НЕ subprocess)
9. Privacy filter: тестовый sensitive/PII запрос (`domain=personal`) НЕ доходит до MiMo
10. Council #7+ показывает 3 голоса в логах (ALF-M3 + Librarian + MiMo)
11. shared_brain WAL содержит записи mimo голосов
12. AGENT_MAP + ALF_CURRENT_STATE обновлены под dual-stack
13. 2-3 council теста с разными типами решений (MiMo up / MiMo down) прошли успешно
14. **Rollback test:** `systemctl disable mimo-agent.service --now` → Council возвращается к 2-voter за 0 сек

**Не входит в scope (отложено):**
- Self-hosting MiMo на GPU VPS (~$50-100/мес)
- MiMo V2.5-Pro (платный tier)
- Voice input
- Полная автомаршрутизация через MiMo (Phase 3 в ALF_ROLE_PROPOSAL)
- Xiaomi EULA юрист-проверка (Олег решит — делать или доверять MIT)

---

## 📂 ЗАТРАГИВАЕМЫЕ ФАЙЛЫ

- `/root/matryoshka/bin/mimo_query.py` — добавить auth (Phase 1)
- `/etc/systemd/system/mimo-query.service` — Environment=MIMO_API_KEY
- `/root/matryoshka/bin/matryoshka_router.py` — добавить /mimo/query + обновить /health + /docs (Phase 2)
- `/root/.hermes/agents/AGENT_MAP.md` — обновить (Phase 5)
- `/root/matryoshka/.hermes/ALF_CURRENT_STATE_23.06.md` — обновить (Phase 5)
- `/root/matryoshka/.hermes/SWARM_V4_DECISION.md` — обновить (Phase 5)
- `fact_store` — 3 новых факта (Phase 5)
- `shared_brain/WAL/hermes.wal` — авто-обновления

---

## 🎯 ROLES (кто что делает)

- **HERMES (я):** Phase 1, 2, 4, 5 — реализация, тесты, документация
- **ALEX:** review плана (control check по skill `hermes-alex-protocol`), контрольная проверка кода
- **Олег:** Phase 0 (регистрация, API key), финальное одобрение

**НЕ делает:**
- HERMES не регистрируется на Xiaomi (задача Олега)
- ALEX не ставит MiMo на VPS (задача HERMES)
- Олег не пишет код (задача HERMES)

---

## 📅 TIMELINE

**Сейчас (23.06.2026 16:00 CEST):**
- Phase 0: Олег регистрируется (в дороге)
- Phase 1-5: ждут API key

**Когда Олег пришлёт API key:**
- Phase 1: 15 мин
- Phase 2: 20 мин
- Phase 3: 30 мин (с review Аликса)
- Phase 4: 15 мин
- Phase 5: 10 мин
- **Total:** ~1.5-2 часа от получения API key

---

## ❓→✅ ВОПРОСЫ К АЛИКСУ / ОТВЕТЫ (23.06.2026 18:05)

**Отправлено:** 23.06.2026 17:58 — opinion-аудит промпт Аликсу (deepseek-v4-flash-free, ~2300 chars)
**Получено:** 23.06.2026 18:05 — ответ 1700+ токен за 30 сек, completed=true

### 1. ЗАМЕНА vs ДОПОЛНЕНИЕ — DUAL-STACK
**Вопрос:** MiMo ЗАМЕНЯЕТ ALF или дополняет?
**Ответ Аликса:** **Dual-stack.** ALF-M3 для простых/быстрых задач (опросы, /hermes), ALF-MiMo для аудитов/1M ctx. Менять целиком = риск сломать production.
**Sensitive / PII данные → ТОЛЬКО M3** (Xiaomi cloud = 152-ФЗ privacy нарушение). MiMo только для технических/кодовых запросов без PII.

### 2. SUBPROCESS vs ACP — ИСПОЛЬЗОВАТЬ ACP
**Вопрос:** MiMo acp/serve не работают (0.1.2). Альтернативы?
**Ответ Аликса:** MiMo V2.5 = opencode-форк → может быть ACP-сервером. Команда: `opencode --acp --provider mimo:V2.5 --port 4197`. Router подключается как к обычному provider. **Subprocess adapter — fallback только Phase 0.5.**

### 3. COUNCIL 3-WAY — SOFT FAIL
**Вопрос:** MiMo down — fallback?
**Ответ Аликса:** **SOFT FAIL (weight=0), НЕ veto.** Если MiMo timeout (>60s) или 5xx → weight=0, голос игнорируется. Council = 2 voters fallback.
Veto только при `confidence > 0.95` и `category ∈ [SECURITY_ISSUE, DATA_LEAK]`.

### 4. RISK/ROLLBACK — 0 СЕКУНД
**Вопрос:** Risk сломать работающее? Rollback?
**Ответ Аликса:** MiMo в отдельном `mimo-agent.service`. Router добавляет MiMo как **опционального** voter'а. opencode.json — backup секция `alf-m3`. **Rollback: `systemctl disable mimo-agent --now` → Council возвращается к 2-voter за 0 секунд.**

### 5. КРИТИЧНЫЕ УПУЩЕНИЯ В ПЛАНЕ (5 пунктов)
1. **Rate limiter** — Xiaomi API limit неизвестен. `mimo_rate_limiter.py` (5 req/min initial).
2. **Privacy compliance (152-ФЗ)** — `mimo_privacy_filter.py` блокирует `domain=personal` на Router ДО MiMo.
3. **Race conditions** — `asyncio.Lock` в mimo_query.py.
4. **License** — Xiaomi EULA проверить юристом (форк opencode MIT, но Xiaomi мог добавить terms).
5. **No monitoring** — `mimo_logger.py` + Prometheus метрики.

### БОНУС: PHASE 0.5 — CRITICAL PATH без API key
6 файлов которые можно сделать прямо сейчас (пока Олег едет):
1. `mimo_rate_limiter.py`
2. `mimo_logger.py`
3. `mimo_privacy_filter.py`
4. `asyncio.Lock` в `mimo_query.py`
5. `opencode.json` dual provider config
6. `council_v2.py` для 3-way voting

**Когда Олег привезёт API key → подключение MiMo займёт 5 минут.**

---

*История версий:*
- *v2 (23.06 18:05) — opinion-audit Аликса. Dual-stack, Phase 0.5 CRITICAL PATH, Council SOFT FAIL, rollback 0 sec, 5 рисков добавлены (EULA/privacy/rate/race/monitoring).*
- *v1 (23.06 16:00) — initial DRAFT (замена ALF на MiMo).*
