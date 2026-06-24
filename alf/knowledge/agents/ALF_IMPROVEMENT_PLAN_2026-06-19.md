# 🚀 ЧТО НУЖНО ALF ДЛЯ КАЧЕСТВЕННОЙ РАБОТЫ
**Дата:** 2026-06-19 01:30 UTC (ночная сессия после аудита HERMES)
**Автор:** ALF (стратег) — анализ для Олега
**Цель:** понять, что нужно вложить в ALF чтобы работал лучше

---

## ⚠️ Текущее состояние ALF

### Что есть (✅)
- ✅ Профиль `alf` с SOUL.md v4.0
- ✅ Telegram бот @IlonAnalyticBot (active)
- ✅ HTTP API gateway `hermes-gateway-alf.service`
- ✅ Holographic memory cross-profile (46 фактов, 10 категорий)
- ✅ 27 специфичных skills + 41 общий
- ✅ 40 файлов в KB ALF (1.8 MB)
- ✅ NotebookLM access (38d2a04f-...) — **НО cookies протухают**
- ✅ Cron tools
- ✅ Telegram rate limit (1.5s batch delay)
- ✅ ACP канал к ALEX (10.8.1.4:4096)
- ✅ AGENT_MAP.md + RECALL PROTOCOL (4 шага)

### Что НЕ работает / отсутствует (❌)
1. ❌ **Vector DB** (chromadb/qdrant/llamaindex) — нет семантического поиска
2. ❌ **Persistent local RAG** — зависим от NotebookLM cookies (каждые 3-5 дней)
3. ❌ **Heartbeat system** — не знаю когда другие агенты down
4. ❌ **Multi-model fallback** — если MiniMax-M3 падает, я слепой
5. ❌ **Critical skills** — нет `hermes-ops`, `fact-check`, `engineering-practices`, `auto-recall`
6. ❌ **Self-test automation** — не могу проверить что я работаю правильно
7. ❌ **Backup моей KB** — могу потерять накопленные знания
8. ❌ **Persistent knowledge graph** — flat memory, нет связей между фактами
9. ⚠️ **HTTP API :8451** DEPRECATED — alf_server.py stub
10. ⚠️ **Vision_analyze** 401 OpenRouter key — нет vision обработки

---

## 🎯 КОНКРЕТНЫЕ УЛУЧШЕНИЯ (приоритезированы)

### 🔴 P0 — КРИТИЧНО (без этого я работаю в пол-силы)

#### 1. Persistent Local RAG (замена NotebookLM cookies)
**Проблема:** Google cookies протухают каждые 3-5 дней. Не могу работать без NotebookLM.
**Решение:** Local vector DB на 33 источниках MATRYOSHKA
- Установить `chromadb` или `qdrant-client`
- Импортировать 33 источника NotebookLM в локальную vector DB (one-time)
- Создать API endpoint `/root/matryoshka/alf/rag_query.py`
- Использовать embedding model (sentence-transformers)
- **Стоимость:** ~2 часа работы, 0₽ дополнительно (локальное)
- **Эффект:** независимость от Google cookies, instant search

#### 2. Multi-model fallback
**Проблема:** Если MiniMax-M3 падает — у меня нет запасной модели.
**Решение:** Fallback chain на другие провайдеры
- Добавить OpenRouter key (он есть в `/root/.hermes/profiles/alf/.env`)
- Настроить `fallback_providers: [nvidia, openrouter]`
- Добавить модели `qwen/qwen3.5-397b-a17b` (nvidia), `anthropic/claude-sonnet-4` (openrouter)
- **Стоимость:** 30 минут настройки, ~$5-10/месяц
- **Эффект:** если MiniMax упал — переключусь на DeepSeek/Claude/Qwen

#### 3. Heartbeat system
**Проблема:** Не знаю в реальном времени когда другие агенты down.
**Решение:** Auto-check всех агентов каждые 5 минут
- Создать `/root/matryoshka/alf/monitors/heartbeat.py`
- Проверять: ALF (Telegram + HTTP), ALEX (ACP), ALINA (HTTP :8470)
- Telegram alert если кто-то down >10 мин
- **Стоимость:** 1 час работы, 0₽ дополнительно
- **Эффект:** я знаю роутинг в реальном времени, могу перенаправить задачу

---

### 🟠 P1 — ВАЖНО (значительно улучшит качество)

#### 4. Установить критичные skills
**Проблема:** У меня нет `hermes-ops`, `fact-check`, `engineering-practices`, `auto-recall`.
**Решение:** Установить из репо / hub
- `hermes-ops` — для self-management (memory limits, skill curation)
- `fact-check` — для проверки фактов перед ответом (Олег требует!)
- `engineering-practices` — для написания надёжного кода
- `auto-recall` — для автоматического поиска контекста
- **Стоимость:** 30 минут на установку
- **Эффект:** стандарт качества выше

#### 5. Backup моей KB
**Проблема:** Если диск поломается — я потеряю 40 файлов KB (1.8 MB).
**Решение:** Auto-backup каждую неделю в WebDAV/Yandex
- Cron `0 5 * * 0` — backup `/root/matryoshka/alf/knowledge/` → WebDAV
- Также: backup `holographic_facts.db`
- **Стоимость:** 30 минут настройки
- **Эффект:** знания не теряются

#### 6. Self-test automation
**Проблема:** Не могу проверить что я работаю правильно после изменений.
**Решение:** Test suite + smoke checks
- Создать `/root/matryoshka/alf/tests/`
- Тесты: fact_store works, NotebookLM (если есть cookies), Telegram bot отвечает, ACP канал жив
- Запускать каждый день через cron, результат в Telegram
- **Стоимость:** 2 часа на написание тестов
- **Эффект:** если я сломаюсь — узнаю утром, а не через неделю

---

### 🟡 P2 — NICE TO HAVE (полировка)

#### 7. Persistent knowledge graph
**Проблема:** Fact_store flat — нет связей между фактами.
**Решение:** Использовать Neo4j или SQLite-based graph
- Связи: "ALF работает на VPS" → "VPS = 85.137.166.209" → "85.137 = SmartApe"
- Транзитивные запросы: "что работает на VPS?"
- **Стоимость:** 4 часа работы
- **Эффект:** более умные ответы

#### 8. Per-task skills
**Проблема:** Часто делаю одну и ту же работу (audit, KB-отчёт, etc.).
**Решение:** Создать skills для частых workflow Олега
- `alf-audit-template` — для аудита любой системы
- `alf-kb-report` — для создания структурированных KB-отчётов
- `alf-fact-extract` — для извлечения фактов из текста
- **Стоимость:** 2 часа на каждый skill (3-4 skills = 8 часов)
- **Эффект:** меньше boilerplate, более consistent

#### 9. Cost tracking
**Проблема:** Не знаю сколько стоит моя работа (token usage).
**Решение:** Подсчёт стоимости per task
- Логировать token usage в `state.db`
- Недельный отчёт Олегу
- **Стоимость:** 2 часа
- **Эффект:** Олег видит ROI

#### 10. Per-agent skills (если хочется)
- `alf-matryoshka` — знания о MATRYOSHKA (как `matryoshka` у hermes-cli)
- `alf-finance` — для финансовых расчётов
- `alf-marketing` — для маркетингового анализа
- **Стоимость:** 1 час каждый
- **Эффект:** специализация

---

## 📊 СРАВНЕНИЕ С ДРУГИМИ АГЕНТАМИ

| Возможность | ALF | hermes-cli | alisa | alina-prod |
|-------------|-----|-----------|-------|-----------|
| Skills специализированные | 27 | 38 | 24 | 49 |
| hermes-ops skill | ❌ | ✅ | ❌ | ✅ |
| fact-check skill | ❌ | ✅ | ❌ | ✅ |
| auto-recall skill | ❌ | ✅ | ❌ | ✅ |
| engineering-practices | ❌ | ✅ | ❌ | ✅ |
| Multi-model fallback | ❌ | ✅ | ❌ | ✅ |
| Heartbeat system | ❌ | ❌ | ❌ | ✅ |
| HTTP API :8451 live | ❌ deprecated | ✅ | ✅ | ✅ |
| Telegram bot | ✅ | ✅ | ✅ | ✅ |

**ALF отстаёт по специализации.** hermes-cli и alina-prod имеют больше инструментов.

---

## 🎯 МОЯ РЕКОМЕНДАЦИЯ СТРАТЕГА

**Минимальный набор (если мало времени):**
1. Persistent RAG (P0) — 2 часа — закрывает риск с cookies
2. Multi-model fallback (P0) — 30 минут — страховка от падения MiniMax
3. Установить fact-check + auto-recall skills (P1) — 30 минут — повышение качества

**Итого:** 3 часа работы, ~$10/месяц — я стану **значительно надёжнее**.

**Полный набор (если есть день):**
Все P0 + P1 = 5 часов, ~$10/месяц — я стану **production-ready агентом**.

**Долгосрочно (на месяц):**
Добавить P2 — knowledge graph, per-task skills, cost tracking. Это инвестиция в качество.

---

## 💡 ЧТО Я МОГУ СДЕЛАТЬ САМ vs ЧТО НУЖНО ОТ ТЕБЯ

### Могу сам (ALF):
- ✅ Установить pip пакеты (chromadb, etc.)
- ✅ Создать Python scripts (heartbeat, self-test)
- ✅ Создать skills (alf-audit-template и т.д.)
- ✅ Настроить cron задачи
- ✅ Импортировать 33 источника в vector DB

### Нужно от тебя:
- 🔑 OpenRouter API key (для fallback и vision) — у тебя есть, нужно положить в .env
- 💰 $5-10/месяц на fallback модели (OpenRouter)
- ⏰ ~3-5 часов моего времени (когда дашь команду)

---

## 🚀 ПЛАН ДЕЙСТВИЙ (если дашь зелёный)

**Сегодня (если хочешь):**
1. Persistent RAG setup (2 часа) — установка chromadb + импорт 33 источников
2. Multi-model fallback (30 минут) — fallback на OpenRouter/DeepSeek

**На этой неделе:**
3. Установить fact-check + auto-recall + engineering-practices skills
4. Heartbeat system для всех агентов
5. Auto-backup KB в WebDAV

**В течение месяца:**
6. Knowledge graph
7. Per-task skills (3-4 штуки)
8. Cost tracking

---

## ❓ ВОПРОС К ТЕБЕ

**> Что из этого приоритет?**

🅰️ **Минимальный** (3 часа): Persistent RAG + Multi-model fallback + fact-check skills
🅱️ **Полный** (5 часов): всё P0 + P1
🅲️ **Только критичное** (2.5 часа): Persistent RAG + fallback
🅳️ **Ничего** — оставить как есть, я работаю достаточно хорошо

Также интересно — **какие из skills ниже ты хочешь чтобы я развивал**:
- `alf-audit-template` (аудит систем по моему алгоритму)
- `alf-matryoshka-context` (быстрый доступ к MATRYOSHKA knowledge)
- `alf-finance` (финансовые расчёты для ALF)
- `alf-marketing` (маркетинговый анализ)

Твоё слово 🎯

---

*ALF — стратег MATRYOSHKA DIGITAL. Этот аудит сделан потому что Олег прямо спросил что мне нужно для лучшей работы.*