# 🪆 ALINA — Self-Improvement (как у HERMES)

**Версия:** 2026-06-17 | **Статус:** Active

Алина **развивается** так же как HERMES, через 4 механизма:

## 1. Holographic Memory (свой fact_store)

- **Файл:** `/root/.hermes/profiles/alina/memories/facts.jsonl`
- **Категории:** nikolay_pref, nikolay_business, iphone_models, avito_patterns, success_patterns, error_patterns, xkin_products
- **Trust score** 0-1 (как у HERMES)
- **Поиск** по keyword (как у HERMES)
- **API:** `alina_holographic.py` (add_fact, search_facts, feedback_fact)

## 2. Feedback Loop (от Николая)

Николай может дать фидбек:
- **"+правильно"** → success, trust ↑
- **"-неверно"** → error, trust ↓
- **"забудь"** → удалить факт
- **Файл:** `memories/feedback.jsonl`
- **Анализ:** cron ежедневно смотрит feedback → обновляет MEMORY.md

## 3. Knowledge Base Auto-Update

- **Cron:** каждый день 4:00 (`alina-self-improve`)
- **Источник:** Алина сама анализирует KB
- **Результат:** рекомендации в `research/alina_recommendations_YYYY-MM-DD.md`
- **Дальше:** Олег/Алина одобряют → записывают в ALINA_KNOWLEDGE_BASE.md

## 4. Memory Auto-Update (из задач)

- **Cron:** каждый день 4:00
- **Источник:** `alina_tasks/DONE_*.md` (все выполненные задачи)
- **Результат:** обновляет `MEMORY.md` (секция "Обновления")

## 5. Curator (раз в 2-3 дня)

- **Что:** автообзор памяти
- **Когда:** если MEMORY.md > 50KB
- **Действие:** дёргает Алину для самосуммаризации

## Сравнение с HERMES

| Возможность | HERMES | ALINA |
|-------------|--------|-------|
| fact_store (holographic) | ✅ Общий | ✅ Свой (alina/) |
| Trust scores | ✅ | ✅ |
| Skill auto-management | ✅ skill_manage | ⚠️ Через HERMES |
| MEMORY.md | ✅ Динамический | ✅ Auto-update 4:00 |
| Curator (auto-review) | ✅ | ✅ Каждые 4:00 |
| Feedback loop | ✅ | ✅ Через Telegram |
| Knowledge base | ✅ Обновляется | ✅ Auto-recommendations |
| Skill learning | ✅ Skills растут | ⚠️ Через HERMES |
| Self-reflection | ✅ | ✅ Дёргает себя для анализа |

## Cron

| Cron | Скрипт | Что |
|------|--------|-----|
| `0 4 * * *` | self_improve.py | Memory + KB обновление |
| `*/2 * * * *` | watchdog.sh | Если упала — перезапустить |
| `*/2 * * * *` | watchdog_server.sh | HTTP server watchdog |
| `*/5 * * * *` | alina_status.sh | JSON для HERMES монитора |
| `0 9,15,21 * * *` | avito_monitor.py | iPhone парсинг |
| `0 21 * * *` | finance_daily.py | Daily report |

## Как Алина улучшается (feedback → action)

```
1. Николай пишет "правильно" → feedback.jsonl (+1)
2. Cron 4:00 → self_improve.py
3. Анализирует feedback за день
4. Обновляет MEMORY.md (если есть изменения)
5. Дёргает Алину для рекомендаций по KB
6. Сохраняет в research/alina_recommendations_*.md
7. Олег/Николай одобряют → в ALINA_KNOWLEDGE_BASE.md
8. Алина использует обновлённую KB в следующих ответах
9. Цикл повторяется
```

## Тест

```python
from cron.holographic import add_fact, search_facts

# Сохранить факт
add_fact("Николай любит XKIN76", "nikolay_pref", trust=0.7)

# Найти
results = search_facts("XKIN")
for r in results:
    print(r["content"], r["trust"])
```

