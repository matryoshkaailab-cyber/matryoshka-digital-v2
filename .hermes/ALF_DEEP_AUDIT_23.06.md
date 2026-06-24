# ALF DEEP AUDIT — 23.06.2026 13:35 CEST
**Инициатор:** Олег («разберите его на болтики»)
**HERMES:** файлы, конфиги, процессы, задачи
**ALEX:** валидация (opinion через ACP)

## 🔴 КРИТИЧНЫЕ НАХОДКИ

### 1. SOUL.md полностью устарел
| Что говорит SOUL.md | Реальность |
|---|---|
| Модель: NVIDIA Nemotron Ultra 550B (OpenRouter) | **minimax/MiniMax-M3** (config.yaml + healthcheck) |
| PID 3119831 | **PID 3735323** |
| context 128K | **80K** (60K ломает — Failed to initialize agent) |
| "ALF не реагирует на inbox/alf/" | **реагирует** (FileWatcher v3 работает) |
| swarm_respond.py | **alf_filewatcher.py → outbox** (другая архитектура) |
| Не обновлялся с | **20.06.2026** |

### 2. Knowledge base 4 дня слепой зоны
- 43 файла, 17 папок в `/root/matryoshka/alf/knowledge/`
- **Последний файл: 19.06.2026** (`ALF_IMPROVEMENT_PLAN`)
- После 19.06 — НИЧЕГО нового

### 3. Shared brain protocol НЕ соблюдается
- `alf.wal` — 27 entries, последняя **19.06.2026**
- После 19.06: **0 записей** (ALF не пишет в shared_brain)
- Каждый "запуск" — как первый раз, нет эпизодической памяти

### 4. ALF не отвечает на длинные structured prompts
- Задача `deep-audit-self-report-23.06-13:10`: промпт 714 chars, требовал 200-400 слов
- ALF ответил за 76 сек, **output = 46 chars (только заголовок)**:
  ```
  # 🔍 ГЛУБОКИЙ АУДИТ ALF — 23.06.2026 13:30 CEST
  ```
- ok=True, status=done. Никакого реального ответа.
- **Вывод по Аликсу:** M3 слабая для structured long prompts, обрезает/теряет контекст

### 5. ALF галлюцинирует собственный стек
- Baseline-test (13:03): ответил «Nemotron 550B через OpenRouter»
- Реально: M3 через minimax API
- ALF **не знает** какая модель в нём работает

## 🟢 ЧТО РАБОТАЕТ ПРАВИЛЬНО

| Компонент | Статус |
|---|---|
| hermes-gateway-alf.service | ✅ active, PID 3735323, memory 307MB |
| alf-filewatcher.service | ✅ FileWatcher v3 (race fix + retry) |
| swarm-alf-bridge.service | ✅ Bridge v2 (notify в Telegram) |
| alf-healthcheck.service | ✅ :8452 /health + /metrics |
| alf-watchdog.timer | ✅ каждые 60 сек, 6 проверок |
| FileWatcher → ALF → outbox | ✅ 22 сек turnaround (baseline-test) |
| Knowledge base доступ | ✅ 43 файла в knowledge/ |
| systemd units правильно настроены | ✅ PartOf, Restart, EnvFile |

## 🎯 МНЕНИЕ АЛИКСА (702 токена, 13.3 сек)

> **Verdict:** ALF в состоянии «фантомные боли» — думает что он супермодель, а реально M3 еле отвечает. Начать с SOUL.md и WAL, остальное — после подтверждения связи.

**СЕЙЧАС:**
- Переписать SOUL.md: модель M3, PID 3735323, дата 23.06
- Baseline-test в ~300-400 chars (M3 friendly)
- Healthcheck ответа на короткий промпт (<50 chars = retry)
- Включить запись в shared_brain

**ПОДОЖДАТЬ:**
- Полный рефакторинг knowledge base
- Смена модели (M3 → что-то сильнее)
- Deep-audit в текущем виде — НЕ ЗАПУСКАТЬ

## 📊 СООТВЕТСТВИЕ РЕАЛЬНОСТИ MATRYOSHKA

| Что | Реальность | Соответствует? |
|---|---|---|
| 3 РОЯ (Белый/Синий/Красный) | Да, AGENTS.md | ✅ |
| ALF = стратег в Белом Рое | Да | ✅ |
| ALEX = тех инженер в Синем Рое | Да | ✅ |
| ALINA = клиентский кейс Николая | Да, отдельный профиль | ✅ |
| ALISA = отложена | Да | ✅ |
| NotebookLM как страховка | Настроено, но 14/33 источников | ⚠️ |
| Право вето Библиотекаря | Не реализовано | ❌ |
| Единый router :8400 | Не реализовано | ❌ |
| Council 2.0 ledger | Реализовано (e9f8e6b) | ✅ |
| FileWatcher v3 + race fix | Реализовано | ✅ |
| Watchdog + healthcheck | Реализовано сегодня | ✅ |

## 🎯 СЛЕДУЮЩИЕ ШАГИ (приоритет)

**P0 — сейчас (30 мин):**
1. Переписать SOUL.md ALF — убрать Nemotron, поставить M3, актуальный PID
2. Включить запись в shared_brain WAL для ALF
3. Сократить baseline-test до 300 chars
4. Простой smoke-test: ALF отвечает на 3 коротких вопроса?

**P1 — после P0:**
5. Обновить knowledge base (хотя бы PRIORITY_PLAN.md + актуальные факты)
6. Решить что делать с M3 (продолжать или менять модель)

**P2 — Фаза 2 (после P0+P1):**
7. ALF-Библиотекарь Python-агент — НО с учётом ограничения M3 (короткие промпты)
8. Единый router :8400
9. Council 2.0 в router
