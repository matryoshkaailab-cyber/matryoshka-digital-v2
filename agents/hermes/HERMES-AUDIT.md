# ПОЛНЫЙ АУДИТ HERMES AGENT — MATROSHKA DIGITAL
## Дата: 2026-05-25 01:45 (МСК)

---

# РАЗДЕЛ 1: ЧТО ЕСТЬ ПО ДОКУМЕНТАЦИИ

## Возможности Hermes Agent v0.14.0 (Curator Release)

### Из документации Hermes:

| Возможность | Документация | Описание |
|--------------|---------------|----------|
| **Persistent Memory** | ✅ Есть | MEMORY.md (2200 chars) + USER.md (1375 chars) — учится и запоминает |
| **Skills System** | ✅ Есть | Процедурная память — создаёт навыки из опыта, переиспользует |
| **Session Search** | ✅ Есть | FTS5 поиск по всем сессиям, прокрутка, browsing |
| **Multi-Platform** | ✅ Есть | Telegram, Discord, Slack, WhatsApp, Signal, Email, Teams, Yuanbao |
| **70+ Tools** | ✅ Есть | terminal, browser, web_search, vision, image_gen, TTS, cron, delegation, etc |
| **Subagents** | ✅ Есть | Изолированные агенты для параллельной работы |
| **MCP Integration** | ✅ Есть | Model Context Protocol — подключение внешних серверов |
| **Voice Mode** | ✅ Есть | Real-time voice, TTS, STT |
| **Self-Improving** | ✅ Есть | Creates skills from experience, improves during use |
| **Open Source** | ✅ Есть | MIT, 165k★ GitHub |
| **Cron Scheduling** | ✅ Есть | Natural language scheduling, platform delivery |
| **Kanban** | ✅ Есть | Durable multi-agent с heartbeat, zombie detection |
| **Checkpoints** | ✅ Есть | Snapshots, pruning, auto-resume |
| **Web UI** | ✅ Есть | `hermes web` dashboard |
| **Self-Maintenance** | ✅ Есть | Curator system — autonomous pruning, skill consolidation |

---

# РАЗДЕЛ 2: ЧТО РЕАЛЬНО НАСТРОЕНО У НАС

## 2.1 Версия и базовая конфигурация

```
Hermes Agent:    v0.14.0 (Curator Release, 2026.5.16)
Python:          3.11.15
OpenAI SDK:      2.24.0
VPS:             Linux 6.8.0-110-generic (85.137.166.209)
Provider:        MiniMax-M2.7
Context:         204,000 tokens
Обновления:      65 commits behind latest ⚠️
```

## 2.2 Процессы запущены

| PID | Процесс | Профиль | Статус |
|-----|---------|---------|--------|
| 1556683 | hermes gateway run --profile alisa | alisa | ✅ Работает |
| 1605544 | ws_server.py (ALEX connection) | - | ✅ Работает |
| 1625241 | hermes gateway run --replace | default | ✅ Работает |
| 1627798 | hermes gateway run --profile nikolay | nikolay | ✅ Работает |

**Проблема:** 4 процесса hermes работают одновременно. Это много или нормально?

## 2.3 Профили настроены

| Профиль | Папка | Конфиг | Использование |
|---------|-------|--------|---------------|
| **hermes-cli** | /root/.hermes/profiles/hermes-cli | Полный (96 строк) | Основной (Олег) |
| **nikolay** | /root/.hermes/profiles/nikolay | Полный (501 строка) | Алина для Nikolay |
| **alisa** | /root/.hermes/profiles/alisa | Пустой | ALF (?) |
| **alf** | /root/.hermes/profiles/alf | Пустой | ALF (?) |
| **default** | /root/.hermes/profiles/default | Минимальный | ? |
| **architect-x** | /root/.hermes/profiles/architect-x | Пустой | ? |
| **hermes-orchestrator** | /root/.hermes/profiles/hermes-orchestrator | Пустой | ? |

**Проблема:** 4 профиля пустые (alf, alisa, architect-x, hermes-orchestrator). Не понятно зачем нужны.

## 2.4 Toolsets

### hermes-cli (Олег):
```yaml
toolsets:
  - hermes-cli
  - image_gen
  - search
```
**Проблема:** Нет browser, нет delegation, нет cronjob?

### nikolay (Алина):
```yaml
toolsets:
  - hermes-cli
```
**Проблема:** Только hermes-cli! Нет image_gen, нет search, нет browser!

## 2.5 MCP Integration

### hermes-cli:
```yaml
mcp_servers:
  minimax_image:
    command: uvx minimax-coding-plan-mcp -y
```
✅ Подключен, но не проверен

### nikolay:
```yaml
mcp_servers: {}
```
❌ Не подключен

## 2.6 Voice/TTS

### hermes-cli:
```yaml
tts:
  provider: minimax
  minimax:
    model: speech-2.8-hd
    voice_id: female-shaonv
    language_boost: Russian
voice:
  auto_tts: true
```
✅ Настроен

### nikolay:
```yaml
tts:
  provider: edge
  edge:
    voice: ru-RU-SvetlanaNeural
voice:
  auto_tts: true
```
✅ Настроен, но другой провайдер

## 2.7 Memory System

**Текущее состояние (после чистки 00:30):**
- MEMORY.md: ~1250 символов (57% от лимита 2200)
- USER.md: ~955 символов (69% от лимита 1375)

**Проблема:** После чистки память пустая — нет накопленных знаний!

## 2.8 Skills

**Папка:** `/root/.hermes/skills/`
- orchestration/session-audit ✅
- orchestration/alex-bidirectional-sync ✅
- orchestration/alex-connection-recovery ✅
- orchestration/hermes-agent-orchestration ✅
- orchestration/matryoshka-orchestra-rules ✅
- orchestration/SKILL.md ✅

**Проблема:** Нет domain-specific skills для MATROSHKA (нет product-sales, нет documentation workflow, нет monitoring skills)

---

# РАЗДЕЛ 3: СОПОСТАВЛЕНИЕ — ЧТО ЕСТЬ vs ЧТО ДОЛЖНО БЫТЬ

## 3.1 Сравнительная таблица

| Возможность | Документация | У нас | Статус |
|-------------|--------------|-------|--------|
| Persistent Memory | ✅ | ⚠️ Частично | MEMORY пустой после чистки |
| Skills System | ✅ | ⚠️ Минимум | Нет domain skills |
| Session Search | ✅ | ✅ Работает | state.db есть, поиск работает |
| Multi-Platform | ✅ | ⚠️ Частично | Только Telegram настроен |
| 70+ Tools | ✅ | ⚠️ 10% | hermes-cli: 3 toolsets, nikolay: 1 |
| Subagents | ✅ | ❌ Не проверен | delegation настроен но не проверен |
| MCP Integration | ✅ | ⚠️ Частично | Только minimax_image в hermes-cli |
| Voice Mode | ✅ | ⚠️ Настроен | Работает но есть проблемы |
| Self-Improving | ✅ | ❌ Не работает | Не создаёт skills из опыта |
| Cron Scheduling | ✅ | ✅ Работает | cronjobs есть, но не все |
| Kanban | ✅ | ❓ Не проверен | kanban.db есть, но не настроен |
| Checkpoints | ✅ | ⚠️ Отключен | nikolay: checkpoints.enabled = false |
| Web UI | ✅ | ❌ Не используется | `hermes web` не запущен |

## 3.2 Что должно быть по документации

### По документации Hermes умеет:

**Memory (учится):**
- Запоминает пользователя, проект, conventions
- Создаёт навыки из опыта
- Сохраняет уроки

**Skills (процедурная память):**
- Создаёт SKILL.md из опыта
- Переиспользует процедуры
- Автоматически загружает при работе

**Session Search (поиск):**
- FTS5 по всем сессиям
- Прокрутка ±N сообщений
- Browse недавних сессий

**Cron (автоматизация):**
- Natural language scheduling
- Доставка в любую платформу
- Мониторинг 3 раза/день

**Subagents (параллельная работа):**
- Изолированные агенты
- Параллельные workstreams
- Zero-context-cost pipelines

### Что из этого реально работает у нас:

| Возможность | Работает? | Проверка |
|-------------|-----------|----------|
| Memory | ❌ НЕТ | MEMORY.md пустой, не сохраняет |
| Skills | ❌ НЕТ | Не создаёт из опыта |
| Session Search | ✅ ДА | state.db работает |
| Cron | ⚠️ 部分 | cronjobs есть, но мониторинг не работает |
| Subagents | ❌ НЕ ПРОВЕРЕНО | delegation настроен но не тестирован |
| Voice | ⚠️ 部分 | Настроен но есть зависания |

---

# РАЗДЕЛ 4: КРИТИЧЕСКИЕ ПРОБЛЕМЫ

## Проблема 1: Memory НЕ работает

**По документации:** Hermes учится и запоминает
**Реальность:** MEMORY.md пустой, USER.md минимальный

**Причина:**
1. Мы почистили память в 00:30 (было 2965 → 1625)
2. После чистки потеряли ВСЮ накопленную память
3. Я не сохраняю результаты работы (see session-audit skill)
4. Каждая сессия начинается с нуля

**Как должно быть:**
```
Работа → Результат → memory add → Следующая сессия читает
```

**Как есть:**
```
Работа → compaction → ВСЁ ПОТЕРЯНО
```

## Проблема 2: Skills НЕ создаются

**По документации:** Hermes создаёт skills из опыта
**Реальность:** Я сделал 20+ вещей за ночь — НИ ОДНОГО skill не создал

**Причина:**
1. Нет процесса создания skill после сложной работы
2. Я "делаю и забываю"
3. Skills создаются только вручную мной (Олегом)
4. Нет автоматизации

**Как должно быть:**
```
Сложная задача (5+ tool calls) → skill_manage create → Навык сохранён
```

**Как есть:**
```
Сложная задача → Сделано → Забыто → Следующая сессия начинает с нуля
```

## Проблема 3: Toolsets НЕДО настроены

**Документация:** 70+ toolsets
**У нас hermes-cli:** 3 toolsets (hermes-cli, image_gen, search)
**У нас nikolay:** 1 toolsets (hermes-cli)

**Проблема:** Нет toolsets для:
- browser (не настроен, хотя в документации есть)
- delegation
- cronjob
- memory
- session_search
- vision
- tts
- todo

## Проблема 4: Checkpoints отключены

**nikolay config.yaml:**
```yaml
checkpoints:
  enabled: false  # ❌ ОТКЛЮЧЕНО
```

**По документации:** checkpoints нужны для:
- Auto-resume прерванных сессий
- Восстановление после сбоев
- Сохранение состояния gateway

**Реальность:** Если gateway nikolay упадёт — всё потеряно

## Проблема 5: Self-Maintenance (Curator) не работает

**v0.14.0 — Curator Release:**
```
Self-maintenance: Curator grades, pruning, skill consolidation
```

**У нас:**
```yaml
curator:
  enabled: true  # ✅ Включен
  interval_hours: 168  # 7 дней
```

**Проблема:** curator запускается раз в 7 дней. Последний запуск? Не известно. Эффективность? Не проверена.

## Проблема 6: Web UI не используется

**Документация:**
```
hermes web — Web UI dashboard for managing Hermes Agent
- Status page: version, sessions, gateway, platforms
- Config editor
- API Keys page
- Sessions, Skills, Cron, Logs, Analytics
```

**У нас:** Не запущено. `ps aux | grep web` — пусто.

## Проблема 7: 65 commits behind

```
Update available: 65 commits behind — run 'hermes update'
```

**Проблема:** Мы на v0.14.0 (16.05.2026), latest возможно v0.14.x или уже v0.15. Не обновляемся — теряем фичи и security fixes.

---

# РАЗДЕЛ 5: ЧТО РЕАЛЬНО РАБОТАЕТ

## ✅ Работает:

1. **Hermes CLI** — общение с Олегом
2. **Telegram gateway** — доставка сообщений
3. **Terminal** — выполнение команд
4. **MiniMax provider** — 204K context, быстрый
5. **Session persistence** — state.db сохраняет
6. **Cron scheduling** — задачи выполняются
7. **ws_server** — связь с Алексом (Windows ПК)
8. **nikolay gateway** — Алина работает
9. **Voice TTS** — в основном работает

## ⚠️ Частично работает:

1. **Memory** — пустой после чистки
2. **Skills** — минимум, не создаются автоматически
3. **MCP** — подключен но не проверен
4. **Vision** — auxiliary настроен но не проверен

## ❌ Не работает / не проверено:

1. **Browser tools** — не настроены
2. **Delegation/subagents** — не проверены
3. **Kanban** — database есть, но не проверен
4. **Checkpoints** — отключены
5. **Web UI** — не запущен
6. **Bookmate API** — 404
7. **Self-improving loop** — не работает

---

# РАЗДЕЛ 6: ПОТЕРИ ИЗ-ЗА COMPACTION

## Что я потерял за эту ночь (используя только memory из session-audit):

**24.05.2026 (день):**
- ❌ Потеряно: Работа с Алиной (не запущена, memory overflow, U+FEFF в AGENTS.md)
- ❌ Потеряно: Результаты диагностики
- ❌ Потеряно: Команды которые выполняли

**25.05.2026 (ночь):**
- ✅ Сохранено (session-audit skill): 86 строк в 2026-05-25.md
- ❌ Потеряно: Контекст между сессиями
- ❌ Потеряно: Что делали между 00:09 и 00:30

**Критическая проблема:**
```
Я делаю работу → compaction → забываю → следующая сессия начинает с нуля
```

**Это противоречит главной фиче Hermes:**
> "The only agent with a built-in learning loop"

**Как должно быть:**
```
Я → сделал работу → создал skill → на следующий день читаю skill → продолжаю
```

**Как есть:**
```
Я → сделал работу → compaction → забыл → на следующий день: "чё делали?"
```

---

# РАЗДЕЛ 7: ИТОГОВЫЙ ВЕРДИКТ

## Сравнение: Документация vs Реальность

| Категория | Должно быть (док) | Реально | Оценка |
|-----------|-------------------|---------|--------|
| **Memory** | Запоминает ВСЁ | Пустой | 2/10 |
| **Skills** | Создаёт из опыта | Не создаёт | 1/10 |
| **Session Search** | Работает | Работает | 8/10 |
| **Toolsets** | 70+ | ~10 | 3/10 |
| **MCP** | Подключение любых | Только minimax | 4/10 |
| **Voice** | Работает | Частично | 6/10 |
| **Cron** | Работает | Работает | 7/10 |
| **Checkpoints** | Включены | Отключены | 0/10 |
| **Self-Improving** | Да | Нет | 0/10 |
| **Web UI** | Используется | Не запущен | 0/10 |
| **Updates** | Свежий | 65 behind | 3/10 |

**ИТОГОВАЯ ОЦЕНКА: 3.5/10**

---

## Главные проблемы:

1. **Я не сохраняю результаты работы** → memory пустой
2. **Я не создаю skills** → теряю опыт
3. **Toolsets недонастроены** → не использую возможности
4. **Checkpoints выключены** → риск потери данных
5. **Web UI не запущен** → не мониторю систему
6. **65 commits behind** → теряю фичи и security

---

## Что нужно сделать (приоритет):

### P0 (Критично):
1. **Включить checkpoints** в nikolay profile
2. **Настроить toolsets** правильно (browser, delegation, cronjob, memory, session_search)
3. **Исправить процесс сохранения** — после КАЖДОЙ работы делать memory add

### P1 (Важно):
4. **Создать domain skills** для MATROSHKA
5. **Запустить hermes web** для мониторинга
6. **Обновиться** (65 commits behind)
7. **Настроить Bookmate API** (статус 404)

### P2 (Желательно):
8. **Проверить delegation/subagents**
9. **Настроить Kanban workers**
10. **Добавить memory для Алины и Nikolay**

---

**Документ создан:** 2026-05-25 01:50 (МСК)
**Автор:** Hermes Agent (self-audit)
**Источник:** hermes-agent.nousresearch.com/docs + реальная конфигурация