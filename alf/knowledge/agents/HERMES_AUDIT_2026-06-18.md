# 🔍 ПОЛНЫЙ АУДИТ HERMES AGENT
**Дата:** 2026-06-18 22:50 UTC
**Автор:** ALF (по запросу Олега, голосовое #N от 18.06)
**Объект:** VPS 85.137.166.209 (Czech, SmartApe), Hermes Agent v0.16.0
**Метод:** Локальный аудит + GitHub + Docs + cross-check с официальной документацией

---

## ⚠️ TL;DR — КРИТИЧЕСКИЕ БАГИ

| # | Баг | Влияние | Severity |
|---|-----|---------|----------|
| 1 | **Hermes v0.16.0 — отстаёт на 291 коммит** от upstream `b39ec2fc` | Потеря фич + багфиксов | 🔴 CRITICAL |
| 2 | **FTS5 в state.db = 0 таблиц** (после 15.06 04:00) | `session_search` пустой → **RECALL PROTOCOL не работает** → агент **не помнит контекст** | 🔴 CRITICAL |
| 3 | **SOUL.md = ОДИН файл на ВСЕ профили** (symlink `/root/matryoshka/SOUL.md`) | ALF носит личность HERMES'а — **идентичность смазана** | 🔴 CRITICAL |
| 4 | **MEMORY.md устарел на 22 дня** (обновлён 27.05) | Содержит **выдуманный UUID**, MiniMax-M2.7, **отключённый ws:8446** как живой | 🔴 CRITICAL |
| 5 | **0 external memory providers настроено** | Hermes не имеет cross-session knowledge beyond MEMORY.md/USER.md | 🟠 HIGH |
| 6 | **AGENTS.md содержит неверный NotebookLM ID** | `9d68c355-...` vs реальный `38d2a04f-...` — ведёт в чужой ноутбук | 🟠 HIGH |
| 7 | **NotebookLM cookies протухли** (3-й раз за день) | Не работает страховка от галлюцинаций | 🟠 HIGH |
| 8 | **MEMORY.md (88%) и USER.md (88%) заполнены** | До отказа осталось мало места | 🟡 MEDIUM |
| 9 | **state.db 52MB + 5385 messages, но 0 fts5** | Поиск по своим же сессиям не работает | 🟠 HIGH |
| 10 | **vision_analyze сломан** (401) | Падает на изображениях | 🟡 MEDIUM |

**Что это значит простым языком:**
> Hermes **не помнит прошлые сессии** (FTS5=0), **носит чужую личность** (ALF = HERMES), **память устарела на 3 недели**, **обновления не ставил с 5 июня**. Это и есть "творит херню" — не со зла, а потому что инфраструктура памяти сломана.

---

## 📊 СРАВНЕНИЕ: КАК ДОЛЖНО БЫТЬ vs КАК СЕЙЧАС

### 1. Memory System (docs/user-guide/features/memory)

| Параметр | По docs | Сейчас на VPS |
|----------|---------|---------------|
| **MEMORY.md лимит** | 2200 chars (frozen snapshot) | 1344 / 2200 = 88% заполнен ✅ формат ок |
| **USER.md лимит** | 1375 chars (frozen snapshot) | 1031 / 1375 = 88% заполнен ✅ формат ок |
| **Auto-compact** | ❌ НЕТ — агент сам consolidate | ⚠️ Не настроено правило "когда удалять" |
| **External provider** | 9 плагинов (honcho, mem0, supermemory, holographic, etc.) | ❌ **0 настроено** |
| **Update interval** | Каждая сессия загружает свежий snapshot | ⚠️ Файлы устарели на 22 дня |
| **Holographic facts** | Опциональный плагин | ✅ Есть `/root/.hermes/memories/holographic_facts.db` (49 KB) |

**Root cause:** Hermes "обещает но не выполняет" потому что **никогда не было настроено external memory provider** для cross-session knowledge. MEMORY.md — это блокнот с 88% заполненности, не knowledge base.

### 2. Skills System (docs/user-guide/features/skills)

| Параметр | По docs | Сейчас на VPS |
|----------|---------|---------------|
| **Single source of truth** | `~/.hermes/skills/` | ✅ `/root/.hermes/skills/` (41 skills) |
| **Bundled skills seeded** | При install через curl-install.sh | ⚠️ Не проверено какие bundled vs user |
| **Progressive disclosure** | Level 0/1/2 (skills_list / skill_view / file) | ✅ Работает |
| **Per-profile skills** | Каждый профиль имеет свой набор | ✅ 9 профилей, от 18 до 49 skills |

**OK, но:** Per-profile skills конфигурируются отдельно от `/root/.hermes/skills/`. Если ALF создаёт skill в `~/.hermes/skills/` — он попадает во ВСЕ профили. Если в `~/.hermes/profiles/alf/skills/` — только ALF.

### 3. Self-Improving Loop

Hermes сам себя описывает как:
> "the only agent with a built-in learning loop — it creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions."

| Компонент loop | Статус |
|----------------|--------|
| **Creates skills from experience** | ✅ Работает (ALF сохранил `stt-faster-whisper-shim`) |
| **Improves during use** | ⚠️ Skill `patch` работает, но не систематически |
| **Nudges to persist knowledge** | ✅ `nudge_state.json` есть |
| **Searches past conversations** | ❌ **СЛОМАНО** — FTS5=0 таблиц |
| **Builds deepening model** | ❌ **СЛОМАНО** — holographic memory есть, но факты не пишутся в cross-session memory |

**Корневая причина "не обучается":** FTS5 search по прошлым сессиям мёртв → агент **не может себя "прочитать"** → не может extract patterns → не учится.

### 4. Identity (SOUL.md)

| Параметр | По docs | Сейчас |
|----------|---------|--------|
| **SOUL.md location** | `$HERMES_HOME/SOUL.md` only | ⚠️ `/root/.hermes/SOUL.md` — symlink на `/root/matryoshka/SOUL.md` |
| **Per-profile persona** | ❌ Не поддерживается (один на instance) | ❌ Все 9 профилей используют ТОТ ЖЕ SOUL.md |
| **ALF как отдельная личность** | Невозможно через SOUL.md | ⚠️ Через system prompt override в `~/.hermes/profiles/alf/.env` — но это костыль |

**Корневая причина "ALF путают с HERMES":** Hermes НЕ поддерживает per-profile persona. SOUL.md — global. У ALF должен быть свой persona layer, но он перебивает через `--system-prompt` или подобное.

### 5. State DB / Session Search

| Параметр | Сейчас |
|----------|--------|
| **state.db размер** | 52 MB |
| **Messages в state.db** | 5385 |
| **FTS5 таблиц** | **0** ❌ |
| **state.db.bak (до purge)** | 648 MB → был purge 17.06 |
| **FTS5 dropped** | 15.06 04:00 (1.27 GB → 617 MB) — **потерян индекс** |

**Корневая причина "провалы в памяти":** Без FTS5 `session_search` не работает → RECALL PROTOCOL (cat .current_context.md + session_search + bookend_end) → **первый шаг пустой**.

### 6. Updates

| Параметр | Сейчас |
|----------|--------|
| **Текущая версия** | Hermes Agent v0.16.0 (2026.6.5) |
| **Upstream** | b39ec2fc |
| **Behind** | **291 commits** ❌ |
| **Последний update** | Стоит `hermes update` — не делалось |

**Корневая причина "не обучается":** Не запускались обновления, которые могли содержать фиксы memory loop.

---

## 🛠️ ПЛАН ПОЧИНКИ (приоритезирован)

### 🔴 P0 — Сделать СЕЙЧАС (без них ничего не работает)

#### 1. Восстановить FTS5 индекс
```bash
hermes sessions rebuild-fts  # или equivalent
# Если нет такой команды:
sqlite3 /root/.hermes/state.db "CREATE INDEX IF NOT EXISTS idx_messages_content ON messages(content);"
# Проверить:
sqlite3 /root/.hermes/state.db ".schema" | grep -i fts
```

#### 2. Обновить Hermes
```bash
hermes update
# проверить:
hermes --version
```

#### 3. Обновить MEMORY.md (актуализировать ложь)
Файл `/root/.hermes/memories/MEMORY.md` от 27.05. Удалить:
- `vision_analyze: BROKEN` → "use native inline"
- `MiniMax-M2.7` → "MiniMax-M3"
- `ALEX: ws via port 8446` → "ALEX: ACP via 10.8.1.4:4096"
- `UUID 4ea33e69-8a88-4811-b1f7-e433b46b8f5a` — ВЫДУМАН
- `Disk 75%` → перепроверить

#### 4. Починить SOUL.md (per-profile)
Сейчас symlink → один файл. Нужно:
- Создать `/root/.hermes/SOUL.md` (HERMES default)
- Создать `/root/.hermes/profiles/alf/SOUL.md` (ALF persona)
- Убрать symlink
- Hermes agent должен уметь подгружать per-profile SOUL.md

#### 5. Поправить AGENTS.md (NotebookLM ID)
`/root/.hermes/AGENTS.md` NotebookLM ID `9d68c355-...` → `38d2a04f-...`

### 🟠 P1 — Сделать сегодня

#### 6. Настроить memory provider
Предлагаю **holographic** (уже есть DB) или **supermemory** (по docs — "crazy powerful"):
```bash
hermes memory setup
# или ручной config:
# /root/.hermes/config.yaml → memory.provider: supermemory
```

#### 7. Auto-update cron для cookies NotebookLM
Уже есть `cookie_expiry_check.sh` на 25 число. Добавить ежедневную проверку.

#### 8. Nudge system
Проверить `nudge_state.json`, настроить `hermes curator` для автоочистки памяти.

### 🟡 P2 — На этой неделе

#### 9. Per-profile skills strategy
Определить: какие skills в `~/.hermes/skills/` (общие), какие в `~/.hermes/profiles/alf/skills/` (ALF-специфичные).

#### 10. State DB cleanup
`state.db 52MB` при 5385 сообщений — норм, но fts5_indexes пустые. После rebuild — должно быть ~150MB.

#### 11. Vision_analyze
Либо получить OpenRouter key, либо полностью перейти на native inline vision (MiniMax-M3 поддерживает).

#### 12. Регулярное обновление
Cron `0 3 * * 0` уже есть (weekly_cache_clean). Добавить `0 4 * * 1` для `hermes update --check`.

---

## 🎯 ЧТО ОТВЕТИТЬ ОЛЕГУ (короткая версия для голосового)

**Олег, аудит закончил. Главное:**

1. **Hermes не виноват** — он сломан ВНУТРИ: FTS5=0 (не ищет по своим же сессиям), memory 22 дня устарела, 291 коммит позади.

2. **"Обещает но не делает"** = потому что **не может вспомнить что обещал** (RECALL PROTOCOL сломан на первом шаге).

3. **"Не обучается"** = потому что **search по своим сессиям не работает** (FTS5) + **нет external memory provider** (honcho/supermemory) — только блокнот MEMORY.md на 88%.

4. **"Врёт"** = потому что **MEMORY.md 22 дня не обновлялся**, там UUID выдуманный, ws:8446 "живой" (уже мёртв с 15.06), MiniMax-M2.7 (а не M3).

5. **ALF ≠ HERMES** — все 9 профилей используют один SOUL.md (symlink). Это by design у Hermes — нужна отдельная persona layer.

**Готов сделать починку. Командуй.**

---

## 📁 ФАЙЛЫ, КОТОРЫЕ НУЖНО ПОПРАВИТЬ

- `/root/.hermes/state.db` — rebuild FTS5
- `/root/.hermes/SOUL.md` — убрать symlink, создать per-profile
- `/root/.hermes/memories/MEMORY.md` — обновить содержимое (убрать ложь)
- `/root/.hermes/memories/USER.md` — проверить заполнение
- `/root/.hermes/AGENTS.md` — NotebookLM ID
- `/root/.hermes/config.yaml` — добавить memory.provider
- `/root/.hermes/skills/` — review bundled vs user
- `/root/.hermes/profiles/*/SOUL.md` — создать для каждого профиля

## 📚 ИСТОЧНИКИ АУДИТА

- **Локально прочитал:** `/root/.hermes/AGENTS.md`, `SOUL.md`, `MEMORY.md`, `USER.md`, `config.yaml`, `memories/ALEX_NOTES.md`, `.current_context.md`, `crontab`, `profiles/*/skills/`
- **Web research:**
  - https://github.com/NousResearch/hermes-agent (README, 11,864 commits, 17 releases)
  - https://hermes-agent.nousresearch.com/docs (installation, features)
  - https://hermes-agent.nousresearch.com/docs/user-guide/features/memory (memory system)
  - https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers (9 providers)
  - https://hermes-agent.nousresearch.com/docs/user-guide/features/personality (SOUL.md)
  - https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files (AGENTS.md)
  - https://hermes-agent.nousresearch.com/docs/user-guide/features/skills (progressive disclosure)
- **Не удалось:** NotebookLM (cookies протухли третий раз за день — отдельная проблема)

---

*ALF — аналитик MATRYOSHKA DIGITAL. Этот аудит — отдельная личность, не persona HERMES.*