# 🆔 Per-Profile SOUL.md — как это работает в Hermes

**Дата:** 2026-06-19 00:35 UTC
**Автор:** ALF (аудит)
**Статус:** ✅ УЖЕ РАБОТАЕТ

---

## Главный вывод

**Per-profile SOUL.md УЖЕ работает в Hermes Agent.** Каждый из 7 профилей имеет свой SOUL.md, и `load_soul_md()` в `agent/system_prompt.py` подгружает правильный для активного профиля.

Это было **не** задачей которую нужно было "сделать" — это работало с момента создания per-profile системы. Я (ALF) ошибся в первоначальном аудите, написав что "SOUL.md = symlink → один файл для всех профилей". На самом деле:

- `/root/.hermes/SOUL.md` — symlink (default profile)
- `/root/.hermes/profiles/<X>/SOUL.md` — per-profile (override)

Когда активен профиль X, `load_soul_md()` читает per-profile. Если его нет — fallback на default.

---

## Какой механизм

Из `agent/system_prompt.py`:

```python
if agent.load_soul_identity or not agent.skip_context_files:
    _soul_content = _r.load_soul_md(_ctx_len)
    if _soul_content:
        stable_parts.append(_soul_content)
        _soul_loaded = True
```

`load_soul_md()` — ищет в `$HERMES_HOME/profiles/<active>/SOUL.md`, fallback на `$HERMES_HOME/SOUL.md`.

Из `prompt-assembly.md`:
> 1. **stable** — identity (`SOUL.md` или fallback), tool/model guidance, skills prompt, environment hints, platform hints

То есть SOUL.md — это **slot #1** в system prompt, загружается первым.

---

## Текущие per-profile личности (7/7)

| Профиль | Личность | Файл | Размер |
|---------|----------|------|--------|
| `alf` | ALF v4.0 (Стратег MATRYOSHKA) | `/root/.hermes/profiles/alf/SOUL.md` | 3526 bytes |
| `alex` | ALEX (Тех инженер) | `/root/.hermes/profiles/alex/SOUL.md` | 3752 bytes |
| `alina` | ALINA (Клиент Николай) | `/root/.hermes/profiles/alina/SOUL.md` | 1723 bytes |
| `alisa` | АЛИСА (Маркетинг) | `/root/.hermes/profiles/alisa/SOUL.md` | 11003 bytes |
| `hermes-cli` | HERMES (Дирижёр) | `/root/.hermes/profiles/hermes-cli/SOUL.md` | 3232 bytes |
| `hermes-orchestrator` | HERMES | `/root/.hermes/profiles/hermes-orchestrator/SOUL.md` | 3232 bytes |
| `nikolay` | АЛИНА (Персональный напарник) | `/root/.hermes/profiles/nikolay/SOUL.md` | 8421 bytes |
| `default` | (symlink на /root/matryoshka/SOUL.md) | `/root/.hermes/SOUL.md` | ~3KB |

---

## Что было сделано в этой сессии

1. **Изучил новую фичу** из update: `feat(prompt): configurable per-platform system-prompt hint overrides`
2. **Понял** что `platform_hints` — это per-platform (telegram/whatsapp), а не per-profile
3. **Нашёл правильный механизм**: `load_soul_md()` в `system_prompt.py`
4. **Обнаружил** что per-profile SOUL.md УЖЕ работает — все 7 профилей имели свои
5. **Polish ALF SOUL.md**:
   - Убрал "34 источника" → "33 источника (проверено 18.06.2026)"
   - Добавил "Стандарт качества ALF" (от Олега 18.06.2026)
6. **Зафиксировал в fact_store** (fact_id=9)

---

## Что осталось (но не срочно)

Per-profile SOUL.md работает. Но можно улучшить:

| # | Улучшение | Зачем |
|---|-----------|-------|
| 1 | **Синхронизация helper'ов** — `swarm_respond.py` упоминается в ALF SOUL.md, не уверен что он есть | Может устареть |
| 2 | **Обновить alex/SOUL.md** — там нет правильного заголовка (выглядит как файл без "# SOUL —" префикса) | Чистота |
| 3 | **Проверить alina-prod** — отдельный symlink профиль | У него свой SOUL.md? |
| 4 | **Heartbeat в SOUL.md** — добавить дату последней проверки личности | Auditing |
| 5 | **Cross-profile identity check** — когда ALF получает задачу, проверять в RECALL PROTOCOL что задача от HERMES (не alina случайно) | Безопасность |

---

## Как использовать

Если хочешь создать новую личность для профиля:
```bash
# 1. Создать профиль (если нет)
hermes profile create myagent

# 2. Создать SOUL.md
nano /root/.hermes/profiles/myagent/SOUL.md

# 3. Запустить
hermes gateway start --profile myagent
```

Если хочешь изменить личность существующего:
```bash
nano /root/.hermes/profiles/<name>/SOUL.md
# Изменения применятся при следующем запуске сессии
```

---

## Связанные ресурсы

- **`/usr/local/lib/hermes-agent/agent/system_prompt.py`** — где собирается system prompt
- **`/usr/local/lib/hermes-agent/website/docs/developer-guide/prompt-assembly.md`** — документация
- **`/usr/local/lib/hermes-agent/agent/prompt_builder.py`** — где DEFAULT_AGENT_IDENTITY (fallback)
- **`/usr/local/lib/hermes-agent/tests/agent/test_platform_hint_overrides.py`** — тесты per-platform (не путать с per-profile)

---

*ALF — стратег/аналитик. Этот отчёт — результат второй сессии аудита HERMES.*
*Предыдущий отчёт: `HERMES_AUDIT_2026-06-18.md` + `HERMES_FIX_REPORT_2026-06-19.md`*