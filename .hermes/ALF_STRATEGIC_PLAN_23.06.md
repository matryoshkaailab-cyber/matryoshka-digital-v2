# ALF — РЕАЛИСТИЧНЫЙ ПЛАН (МИНИМУМ, без наворотов)

**Дата:** 2026-06-23 19:50
**Автор:** HERMES (по запросу Олега)
**Статус:** PLAN — реализуем сейчас, после API key Xiaomi
**Файл:** `/root/matryoshka/.hermes/ALF_STRATEGIC_PLAN_23.06.md`
**Принцип:** Quality + Performance + Stability. Реальный стратег, не показной.

> **Контекст:** Олег попросил «более реалистичный и правильный план, без всяких наворотов, но нужно качество, производительность и стабильность. Мы рассчитываем на это — стратег должен действительно помогать, быть производительным, мощным, умным.»

---

## 🎯 ЦЕЛЬ

**ALF — реально работающий стратег.** Не для показухи, не ради модных слов.

**Критерии успеха (Олег):**
1. **Quality** — ответы корректные, не галлюцинирует
2. **Performance** — не тормозит, не обрезает длинные задачи
3. **Stability** — не падает, не теряет состояние

**Не делаем** (отложено = `ALF_ENHANCEMENT_PLAN_23.06.DEFERRED.md`):
- ❌ Embeddings memory (ChromaDB) — UX, не критично
- ❌ Multi-modal ALF (whisper input) — UX, не критично
- ❌ Proactive suggestions — UX, не критично
- ❌ Gemini audit voter — overengineering (M3 + MiMo хватает)
- ❌ 4-way council — overengineering (2-way + опциональный MiMo = правильно)

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ (проверено live 23.06.2026 19:30)

**Что РАБОТАЕТ (не трогаем):**
- ✅ ALF на M3 80K (стратег, VPS, профиль alf)
- ✅ 5 systemd units ALF (gateway, filewatcher, bridge, healthcheck, watchdog)
- ✅ Council 2.0 (ALF + Librarian voters) — 6 успешных тестов
- ✅ SOUL.md v5.0 (после фикса Nemotron hallucination)
- ✅ Telegram @IlonAnalyticBot — polling работает
- ✅ shared_brain (DIGEST.md, WAL) — общая память роя

**Задокументированная боль** (решаем):
- ⚠️ M3 80K обрезает длинные задачи (ALF_DEEP_AUDIT_23.06) — MiMo 1M это фикс

---

## 📋 ЧТО ДЕЛАЕМ (МИНИМУМ)

### Phase 1: MiMo integration на ПК Олега (30 мин после API key)

**Что:**
- Олег передаёт API key Xiaomi
- Аликс настраивает `opencode.json` на ПК (providers.mimo type=acp url=:4197)
- Поднимаем MiMo как ACP сервер на ПК: `opencode --acp --provider mimo:V2.5 --port 4197`
- systemd unit `mimo-acp.service` на ПК

**Acceptance:**
- `curl http://10.8.1.4:4197/api/health` → 200 OK через VPN
- Latency MiMo V2.5 на 50K токенов <60 сек

### Phase 2: Router integration + privacy filter (30 мин)

**Что:**
- Добавить `/api/v1/mimo/proxy` endpoint в `matryoshka_router.py` :8400
- Privacy filter: `domain=personal` / ALINA / sensitive → ALF-M3, иначе → MiMo для context>80K
- mimo_query.py (subprocess) → FALLBACK (если ПК down)

**Acceptance:**
- Тестовый запрос с `domain=personal` / PII / sensitive tags → НЕ доходит до MiMo (privacy filter срабатывает)
- Обычный технический запрос >80K → MiMo
- Обычный короткий запрос → ALF-M3

### Phase 3: Council 2-way + опциональный MiMo audit voter (30 мин)

**Что:**
- Council 2.0 как сейчас (ALF + Librarian voters — ВСЕГДА)
- MiMo подключается как опциональный audit voter ТОЛЬКО для context>80K
- Soft fail: если MiMo timeout → weight=0, Council = 2 voters fallback
- VETO MiMo: только при confidence>0.95 на security_issue/data_leak

**Acceptance:**
- Council принимает решения когда MiMo down (тест с отключённым mimo-acp)
- Audit voter работает для длинных задач (MiMo даёт голос с weight×1.5)
- Privacy: MiMo НИКОГДА не получает sensitive / PII данные (privacy filter на Router)

### Phase 4: WAL + observability (15 мин)

**Что:**
- mimo-agent пишет в shared_brain WAL после каждой задачи
- Council логи показывают `mimo_vote: for/against/skipped`
- Privacy filter события → audit log

**Acceptance:**
- `cat alf.wal` показывает записи MiMo
- Audit log показывает все privacy blocks

### Phase 5: Documentation update (10 мин)

**Что:**
- Обновить `MIMO_INTEGRATION_PLAN.md` (он уже есть, расширю Phase 0.5 секцию)
- Обновить `ALF_CURRENT_STATE_23.06.md` (MiMo audit voter в архитектуре)
- Обновить `SWARM_V4_DECISION.md` (MiMo dual-stack)

**Acceptance:**
- Везде актуальная правда про новую архитектуру

**ИТОГО: ~2 часа** после получения API key от Олега.

---

## ✅ QUALITY / PERFORMANCE / STABILITY критерии (Олег)

### Quality (корректность ответов)

| Проверка | Как меряем | Целевое |
|---|---|---|
| ALF не галлюцинирует модель | Smoke test: «какая у тебя модель?» | Правильный ответ (M3 / MiMo) |
| Council не даёт ложных accepted | 6+ council тестов на разных решениях | 6/6 правильных |
| Quality | Privacy filter не пропускает PII/sensitive | Тест с реальными fixtures (PII, паспорт, медицина, голосовые) | 100% blocked |

### Performance (скорость + контекст)

| Метрика | Как меряем | Целевое |
|---|---|---|
| Короткие задачи latency | `hermes-cli chat` ping | <3 сек |
| Длинные задачи latency | MiMo V2.5 на 50K токенов | <60 сек |
| Council turnaround | Time от /council до decision | <90 сек (ALF async) |

### Stability (надёжность)

| Метрика | Как меряем | Целевое |
|---|---|---|
| ALF uptime | systemd watchdog reports | >99% (down <1% time) |
| MiMo SOFT FAIL работает | Тест с kill mimo-acp | Council = 2 voters, принято решение |
| Privacy filter uptime | `mimo_privacy_blocks_total` логируется | 100% попыток logged (PII, sensitive, personal domain) |
| Rollback время | `systemctl stop mimo-acp` → Council 2 voters | <1 сек |

---

## 🎯 ROLES (кто что делает)

- **HERMES (я):** Phase 1-5 реализация, тесты, документация
- **ALEX (через Аликса):** настройка opencode.json на ПК (Phase 1)
- **Олег:** API key (Phase 0), финальное одобрение

**НЕ делает:**
- HERMES не плодит сущности (без embeddings, multi-modal, proactive — отложено)
- ALEX не ставит MiMo на VPS
- Олег не пишет код

---

## 📂 ЗАТРАГИВАЕМЫЕ ФАЙЛЫ

**Phase 1 (ПК):**
- `~/.opencode/config.json` на ПК (Аликс правит)
- `mimo-acp.service` systemd unit на ПК

**Phase 2-3 (VPS):**
- `/root/matryoshka/bin/matryoshka_router.py` (добавить /api/v1/mimo/proxy)
- `/root/matryoshka/bin/mimo_query.py` (fallback mode)
- `/root/matryoshka/bin/mimo_query_async.py` (serial execution + kill switch — уже готов)
- `/root/matryoshka/bin/mimo_privacy_filter.py` (privacy filter — уже готов)
- `/root/matryoshka/bin/council_v2.py` (3-way voting — уже готов)
- `/root/matryoshka/bin/mimo_context_bootstrap.py` (DIGEST.md injection — уже готов)

**Phase 4 (Observability):**
- `/var/log/matryoshka/mimo/` (audit logs)
- `/root/matryoshka/shared_brain/WAL/mimo.wal` (new)

**Phase 5 (Docs):**
- `/root/matryoshka/.hermes/MIMO_INTEGRATION_PLAN.md` (уже есть, расширю Phase 0.5 секцию)
- `/root/matryoshka/.hermes/ALF_CURRENT_STATE_23.06.md` (обновить)
- `/root/matryoshka/.hermes/SWARM_V4_DECISION.md` (добавить MiMo dual-stack)

**Phase 0.5+ утилиты (готовы ✅):**
- mimo_rate_limiter.py — 4/4 тестов
- mimo_logger.py — 4/4 тестов
- mimo_privacy_filter.py — 7/7 тестов
- mimo_query_async.py — 4/4 тестов
- mimo_cost_ledger.py — 5/5 тестов
- mimo_context_bootstrap.py — 5/5 тестов
- mimo_fallback_integration_test.py — 4/4 тестов
- council_v2.py — 7/7 тестов

**ИТОГО: 40/40 unit-тестов зелёные уже сейчас.**

---

## ⚠️ РИСКИ (минимальные)

| Риск | Серьёзность | Mitigation |
|---|---|---|
| Xiaomi отключит API | HIGH | Если MiMo down → Council 2 voters, всё работает |
| Xiaomi EULA ограничит коммерцию | HIGH | Юрист-проверка (Олег решит — доверять MIT или нет) |
| mimo acp/serve не работают в 0.1.2 | LOW | Workaround: opencode --acp на ПК |
| MiMo privacy (Xiaomi cloud) | HIGH | PRIVACY FILTER на Router: sensitive data / PII / 152-ФЗ → ТОЛЬКО M3 (не MiMo, не Xiaomi cloud) |
| Latency 6-15s MiMo | LOW | Для длинных задач приемлемо |

---

## 📅 TIMELINE

**Сейчас (23.06.2026 19:50):**
- Phase 0.5 готов (40/40 тестов)
- Ждём API key Xiaomi от Олега

**После API key (через 1-2 дня):**
- Phase 1: 30 мин
- Phase 2: 30 мин
- Phase 3: 30 мин
- Phase 4: 15 мин
- Phase 5: 10 мин
- **Total: ~2 часа**

**Потом (через неделю, real usage):**
- Меряем Quality / Performance / Stability по критериям выше
- Если всё OK → MiMo dual-stack в production
- Если проблемы → rollback 0 сек (disable mimo-acp)

---

## 🔗 СВЯЗАННЫЕ ДОКУМЕНТЫ

- **Phase 0.5 готов** → `/root/matryoshka/bin/mimo_*.py` (8 модулей, 40 тестов)
- **MiMo research** → `/root/matryoshka/.hermes/MIMO_FULL_ANALYSIS_23.06.md`
- **Integration plan** → `/root/matryoshka/.hermes/MIMO_INTEGRATION_PLAN.md`
- **ALF state** → `/root/matryoshka/.hermes/ALF_CURRENT_STATE_23.06.md`
- **DEFERRED features** → `/root/matryoshka/.hermes/ALF_ENHANCEMENT_PLAN_23.06.DEFERRED.md` (embeddings/multi-modal/proactive — отложены)
- **AGENTS map** → `/root/.hermes/agents/AGENT_MAP.md`

---

## 📜 ИСТОРИЯ ВЕРСИЙ

- **v1 (23.06.2026 19:50)** — initial realistic plan по запросу Олега. Quality + Performance + Stability. Без наворотов.

---

*Минимальный план. Делаем когда API key придёт. DEFERRED фичи остаются в reference на будущее.*
