# MiMo Code — ПОЛНЫЙ АНАЛИЗ (по запросу Олега 23.06.2026 15:55)

**Источники:** README с github.com/XiaomiMiMo/MiMo-Code, mimo.xiaomi.com/blog/mimo-code-long-horizon, видео Сухов:Live transcript, live-тесты на нашем VPS (23.06.2026 15:25).

---

## 📦 ЧТО ТАКОЕ MIMO CODE (коробка)

**MiMo Code** — это **терминальный coding agent** (как Claude Code, как наш Hermes-cli gateway). Не desktop приложение. Не IDE плагин. Это **CLI** который:

- Читает и пишет код
- Запускает команды в shell
- Управляет Git
- Имеет **persistent memory** (проект + сессия)
- Самосовершенствуется через `/dream` и `/distill`
- Поддерживает **несколько агентов**: `build` (default, development), `plan` (read-only), `compose` (orchestration)

**Open source:** MIT license, `github.com/XiaomiMiMo/MiMo-Code`  
**Install:** `curl -fsSL mimo.xiaomi.com/install | bash` или `npm install -g @mimo-ai/cli`  
**Версия:** 0.1.2 (12 Jun 2026)

---

## 🧠 ЧТО ВНУТРИ (3 time scales — это и есть главное отличие)

Из README и блога Xiaomi:

| Time scale | Bottleneck | MiMo решает через | У нас |
|---|---|---|---|
| **Within single turn** | Single-step decision quality | **Max Mode** (5 параллельных кандидатов + judge) | 1 модель, 1 ответ |
| **Multi-turn within session** | State continuity | **Cycle/checkpoint** (cycle = checkpoint → rebuild в новом окне) | Контекст теряется |
| **Across sessions** | Experience distillation | **/dream + /distill** (агент сам пакует опыт в skills) | Никакой |

Это **масштабное** отличие от Hermes-cli. У нас сейчас:
- M3 с контекстом 80K, обрезается
- FileWatcher v3 пишет в WAL — это **наш** ответ на cross-session
- НО: у нас нет Goal verification, нет Max Mode, нет /dream, нет auto-rebuild

---

## 🤖 МОДЕЛЬ (что за мозги)

**MiMo V2.5 (по умолчанию) + другие модели в списке:**

| Модель | Описание |
|---|---|
| `mimo/mimo-auto` | **Free for a limited time** (Xiaomi hosted) — работало 1 час назад, сейчас требует auth |
| `xiaomi/mimo-v2-flash` | V2 Flash (быстрая) |
| `xiaomi/mimo-v2-omni` | V2 Omni (мультимодальная) |
| `xiaomi/mimo-v2-pro` | V2 Pro |
| `xiaomi/mimo-v2.5` | **V2.5 (1M контекст)** — основная |
| `xiaomi/mimo-v2.5-pro` | V2.5 Pro (продвинутая) |
| `xiaomi/mimo-v2.5-pro-ultraspeed` | V2.5 Pro быстрая |

**Benchmarks (по заявлениям Xiaomi):** MiMo Code + V2.5-Pro = 62% SWE-bench Pro vs Claude Code 57% (MiMo лучше на 5%).

**Бесплатность:** **КОД** (MIT) бесплатный ВСЕГДА. **Cloud hosted MiMo V2.5** бесплатно **ВРЕМЕННО** (надпись "free for a limited time" прямо в UI MiMo Code).

---

## ⚡ КЛЮЧЕВЫЕ ФИЧИ (что умеет, чего у нас нет)

### 1. **Max Mode** (параллельные кандидаты с judge)
- Генерирует 5 решений параллельно
- Judge модель выбирает лучшее
- Temperature=1 (кандидаты разные)
- +10-20% на SWE-bench Pro
- Стоимость: ×4-5 токенов

**Что это даёт:** для сложных задач — diversity, не compounding errors.

### 2. **Goal / Stop Condition** (независимый verifier)
- `/goal "все тесты пройдены и код закоммичен"`
- Когда агент хочет остановиться, **отдельный verifier** проверяет реальное состояние
- False blocking <0.5%
- Решает проблему "premature optimistic stop" — когда агент говорит "готово" а на самом деле нет

**Что это даёт:** safety net для критических задач.

### 3. **Persistent Memory** (4 типа файлов)
- `MEMORY.md` — проект, архитектурные решения
- `checkpoint.md` — снапшоты состояния сессии
- `notes.md` — черновики
- `tasks/<id>/progress.md` — лог задач

**Backend:** SQLite FTS5 для поиска.

**Что это даёт:** агент помнит проект между сессиями. У нас была проблема 19-23.06 когда ALF забывал контекст.

### 4. **Cycle / Checkpoint** (Long-horizon context)
- Runtime сам решает когда сохранить state
- Если контекст близок к лимиту — rebuild из checkpoint + memory + recent messages
- Агент "просыпается" в новом окне с полным контекстом
- "From model's perspective, the conversation has never been interrupted"

**Что это даёт:** решает нашу главную проблему с M3 80K. Бесконечные длинные задачи.

### 5. **Subagent System**
- Primary agent создаёт subagents on demand
- Subagents делят контекст primary
- Parallel execution + cancellation + background
- Иерархия: T1 → T1.1, T1.2

**Что это даёт:** параллелизм задач, дерево задач.

### 6. **Compose Mode** (specs-driven)
- Structured workflow: plan → execution → code review → TDD → debug → verification → merge
- Skills-based orchestration

**Что это даёт:** формализованный пайплайн для типовых задач.

### 7. **Voice Input** (опционально)
- MiMo-V2.5-ASR модель
- Говоришь → текст → промпт

**Что это даёт:** hands-free coding.

### 8. **Custom Providers**
- Поддерживает любой OpenAI-compatible API
- Можно подключить наш Router :8400 как "провайдер" — MiMo будет ходить через нас

**Что это даёт:** гибкость.

### 9. **Import from Claude Code**
- `/mimo import` подтягивает настройки + MCP + skills из Claude Code
- One-step migration

**Что это даёт:** если у Олега есть Claude Code настройки, можно перенести.

### 10. **/dream и /distill** (Self-Evolving)
- `/dream` — агент сам копит знания
- `/distill` — пакует рутину в skills
- Каждая сессия автоматически reviews

**Что это даёт:** агент улучшается сам со временем.

---

## 🔄 СРАВНЕНИЕ С HERMES-CLI (наша текущая коробка)

| Ось | Hermes-cli (ALF) | MiMo Code |
|---|---|---|
| **Модель** | M3 (minimax) | MiMo V2.5 (xiaomi) |
| **Контекст** | 80K (обрезка на длинных) | 1M |
| **Memory** | FileWatcher WAL + manual | SQLite FTS5, auto-checkpoint, /dream |
| **Cross-session** | Восстановлено сегодня (alf.wal) | Встроено + cycle/checkpoint |
| **Telegram** | @IlonAnalyticBot polling | НЕТ (только CLI) |
| **HTTP API** | :8461 (Библиотекарь), :8452 (healthcheck) | :8401 (mimo acp) — НЕ работает в 0.1.2 |
| **Subagents** | НЕТ (ALF = одна роль) | ДА (primary → subagents, parallel) |
| **Goal verification** | НЕТ | ДА (independent judge) |
| **Max Mode (5 кандидатов)** | НЕТ | ДА |
| **Self-evolution** | НЕТ (только через manual update) | ДА (/dream, /distill) |
| **Compose mode** | НЕТ | ДА (plan → code review → TDD → merge) |
| **Voice input** | НЕТ | ДА |
| **Custom providers** | OpenAI-compatible в Hermes | OpenAI-compatible в MiMo |
| **Pricing** | $0 (M3 free) | $0 код, API временно $0 |
| **Бенчмарк** | M3 80K = слабее на длинных | V2.5-Pro = 62% SWE-bench vs Claude 57% |
| **Stability** | Production (5 сервисов, watchdog, Council 2.0) | v0.1.2 (только что выпущен) |
| **Telegram интеграция** | ДА (наш killer feature) | НЕТ |
| **Self-hosting** | ДА (наш VPS) | ДА (но нужен GPU) |

---

## 🛠️ КАК БУДЕТ ОТЛИЧАТЬСЯ ОТ HERMES В РАБОТЕ

### Один и тот же запрос, разные ответы

**Запрос:** "Сделай рефакторинг модуля X, добавь type hints, обнови тесты, закоммить"

**Hermes (ALF на M3):**
```
→ inbric ALF задачу в inbox/alf/
→ ALF думает 20-30 сек
→ Один ответ: "Вот план, давай делать"
→ HERMES решает: выполнять или нет
→ ALF делает
→ Telegram: "готово, коммит X"
```
**Время:** 30-60 сек. **Контроль:** HERMES. **Верификация:** нет.

**MiMo (ALF-MiMo на V2.5):**
```
→ Router вызывает MiMo agent
→ MiMo Max Mode: 5 параллельных кандидатов
→ Goal: "все тесты пройдены, типизация 100%, коммит сделан"
→ 5 кандидатов пишут код параллельно
→ Judge выбирает лучшего
→ Verifier проверяет Goal
→ Если не достигнут — agent продолжает
→ Когда Goal достигнут — финальный commit
→ Router получает результат
```
**Время:** 2-5 минут (дольше, но автономно). **Контроль:** HERMES (через Router). **Верификация:** ДА (Goal).

### Где MiMo выигрывает

| Сценарий | Hermes | MiMo |
|---|---|---|
| Простой вопрос ("ping") | ✅ быстро, 6 сек | ✅ тоже быстро, 6 сек |
| Длинный аудит (500 строк кода) | ❌ обрезка на 80K, заголовок | ✅ 1M контекст, полный отчёт |
| "Сделай X от начала до конца" | ❌ нужно пинговать, теряет контекст | ✅ Goal mode, автономно |
| Задача с 10+ файлов | ❌ забывает контекст | ✅ checkpoint + memory |
| Нужно 5 разных вариантов | ❌ 1 ответ | ✅ Max Mode |
| Voice coding | ❌ нет | ✅ MiMo-V2.5-ASR |
| Telegram алерт | ✅ есть | ❌ нет (только CLI) |

### Где Hermes выигрывает

- **Telegram** — killer feature, MiMo нет
- **Stability** — наш production-ready, MiMo v0.1.2
- **Self-hosted без GPU** — у нас работает, MiMo требует железо
- **NotebookLM** — у нас есть интеграция, MiMo нет
- **Privacy** — наш VPS = наш контроль, Xiaomi cloud = их контроль

---

## 🎯 ИТОГ ДЛЯ РОЯ (3 модели)

**Если установить MiMo + дать API key:**

```
HERMES (M3) — дирижёр, скорость, Telegram, простые задачи
   │
   ├─ ALF (M3) — KB, цитаты, NotebookLM, точные данные  
   ├─ ALF-MiMo (V2.5) — длинные задачи, memory, Goal, Max Mode
   ├─ ALEX (DeepSeek на ПК) — тех. инженер, код
   ├─ ALINA (отдельный кейс) — клиент Николай
   └─ ALISA (отложена)
```

**Council 2.0 → 3-way voting** (если дать MiMo голос):
- HERMES: "ALF должен использовать Python-агент Библиотекарь"
- ALF (M3): "ЗА" (цитирует SOUL.md)
- ALF-MiMo (V2.5): "ЗА, с условием..." (длинный анализ, 1M контекст)
- Финал: **accepted** с расширенным обоснованием

**Каждый агент превосходит в своём:** M3 — скорость/точность, MiMo V2.5 — глубина/память, DeepSeek — код.

---

## ✅ ЧТО ГОТОВО УЖЕ СЕЙЧАС

- ✅ `npm install -g @mimo-ai/cli` (0.1.2)
- ✅ 6 успешных тестов с реальными ответами
- ✅ `/root/matryoshka/bin/mimo_query.py` (адаптер на :8402) — subprocess → HTTP
- ✅ `mimo-query.service` (systemd) — active
- ✅ `/health`, `/models`, `/query` endpoints
- ❌ Требует API key для production (Xiaomi закрыл free access)

## 🎯 ЧТО НУЖНО ОТ ОЛЕГА + АЛИКСА

1. Зарегистрироваться на mimo.xiaomi.com → получить API key
2. Передать мне API key (через переменную окружения или файл)
3. Я за 5 мин:
   - Обновлю mimo_query.py чтобы использовал auth
   - Добавлю `/mimo/query` endpoint в Router :8400
   - Покажу трёхмодельный Council

Пока жду — могу продолжить Block 4 (Healthcheck) + Block 5 (Router SPOF), это независимо.
