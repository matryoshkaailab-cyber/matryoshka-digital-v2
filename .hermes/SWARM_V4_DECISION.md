# SWARM V4.0 — Архитектура роя MATRYOSHKA (утверждено 18.06.2026 22:30)

**Утверждено:** Олегом 18.06.2026 ~22:30 CEST
**Обсуждение:** 3 участника — HERMES (дирижёр), ALEX (технический), ALF (стратег)
**Источник:** Сессия Hermes 2026-06-18

---

## 5 решений

### 1. ИЕРАРХИЯ: ГИБРИД (по предложению ALF)

```
ОЛЕГ (Директор, ID 1951845052)
  ↓ Telegram (только через HERMES)
HERMES (Дирижёр, VPS) ← единственная точка входа
  ├→ ALEX (тех. инженер, ПК Олега, ACP :4096)
  ├→ ALF  (стратег, VPS, профиль alf, Telegram @IlonAnalyticBot)
  └→ ALINA (отдельный кейс Николая, VPS, профиль alina-prod)
```

**Гибрид:**
- Олег общается только с HERMES (нет прямого доступа к ALF/ALEX/ALINA)
- ALF может инициировать обмен с ALEX через HERMES (через `.hermes_task_alf.json`)
- ALEX не общается с ALF напрямую — только через HERMES

### 2. ALF ↔ ALEX: ТОЛЬКО через HERMES

- Протокол: ALF пишет задачу в `/root/matryoshka/.hermes_task_alf.json`
- HERMES видит файл, решает приоритет, отправляет ALEX через ACP
- Результат пишется в `/root/matryoshka/.hermes_result.json`
- ALF читает результат и продолжает работу

### 3. КОНТЕКСТ: Obsidian + session_search (НЕ "или")

- **Obsidian** (`/root/obsidian-vault/` или WebDAV `:8181`) — долговременная правда:
  - Знания, решения, контекст проекта
  - Knowledge base Алины, Альфа
  - AGENTS.md, SOUL.md, PLAN.md
- **session_search** (Hermes FTS5) — runtime-индекс:
  - Последние часы оперативки
  - Быстрый поиск по сообщениям
  - Авто-cleanup через 30 дней
- Связь: ALF librarian индексирует Obsidian WebDAV → отдаёт контекст HERMES по запросу

### 4. ALINA: ОТДЕЛЬНЫЙ КЕЙС (навсегда)

- ALINA = клиентский бот Николая, не часть роя Олега
- Изоляция данных (v3.2 mandate): НИКОГДА не смешивать DATALINK и ALINA
- ALEX имеет доступ к ALINA только через явную задачу HERMES с `scope: alina`
- Telegram: @NikolaAlinaBot
- Профиль: `alina-prod` (отдельный venv `/opt/alina-hermes/venv`)

### 5. АВТОМАРШРУТИЗАЦИЯ: РУЧНАЯ (2-3 мес до автомата)

- Сейчас: Олег → HERMES → ручное решение куда делегировать
- Через 2-3 мес (когда 50+ задач с известными паттернами):
  - Лёгкий LLM-классификатор на VPS (`:7460`)
  - Human-in-the-loop override через Олега
- До того: ручная маршрутизация через HERMES (текущее состояние)

---

## Что НЕ меняется

- ✅ Канал HERMES↔ALEX: ACP :4096 через AmneziaWG (10.8.1.4)
- ✅ Telegram боты: @IlonAnalyticBot (ALF), @NikolaAlinaBot (ALINA), HERMES CLI (Олег)
- ✅ Изолированные venv: /opt/alf-hermes/venv, /opt/alina-hermes/venv
- ✅ systemd units: hermes-cli-gateway, hermes-gateway-alf, alina-prod-gateway

## Что нужно создать (после фиксации)

1. `/root/matryoshka/.hermes_task_alf.json` — файл-очередь для задач от ALF к ALEX через HERMES
2. `/root/matryoshka/.archive/swarm_v4_2026-06-18.md` — backup старого AGENTS.md (v3.3)
3. `/root/.hermes/profiles/hermes-cli/AGENTS.md` — обновлённая версия v4.0

---

## Участники обсуждения

| Кто | Роль | Вклад |
|-----|------|-------|
| Олег | Директор | Финальное решение |
| HERMES | Дирижёр | Координация обсуждения, формализация |
| ALEX | Технический инженер | Технические аргументы (ACP, протоколы) |
| ALF | Стратег + библиотекарь | Стратегическое видение (иерархия, контекст) |

---

## 📅 PHASE 2 — COUNCIL 2.0 + LIBRARIAN (добавлено 23.06.2026 14:42)

**Что добавилось в Phase 2:**

### 1. ALF-Библиотекарь (Python-агент) :8461

- **Что это:** отдельный фактчекер, **НЕ LLM** — Python + grep по `alf/knowledge/*.md`
- **Файлы:** `/root/matryoshka/bin/alf_librarian.py` (9.8 KB), `alf-librarian.service`
- **Endpoints:** `/health`, `/fact-check`, `/veto`, `/search`
- **Veto timeout:** 30 секунд (по правилу Аликса — не быть bottleneck)
- **Когда вызывается:** для каждого Council 2.0 цикла

### 2. MATRYOSHKA Router :8400

- **Что это:** единая точка входа для всех агентов
- **Файлы:** `/root/matryoshka/bin/matryoshka_router.py` v0.3 (18.7 KB), `matryoshka-router.service`
- **Endpoints:**
  - `GET /health` — aggregated health всех сервисов
  - `POST /council` — Council 2.0 cycle (ALF + Библиотекарь)
  - `GET /council/<id>` — статус конкретного решения
  - `GET /council/list` — последние 50 решений
  - `POST /alf/query` — proxy в ALF inbox
  - `POST /alf-librarian/{fact-check,veto,search}` — proxy на :8461
  - `POST /alina/query` — proxy на ALINA

### 3. Council 2.0 (async polling pattern)

**Алгоритм:**
1. HERMES вызывает `POST /council` с `decision`
2. Router генерирует `council_id`
3. Router параллельно:
   - Отправляет ALF задачу в `inbox/alf/` (короткий prompt: "ЗА/ПРОТИВ одним предложением")
   - Вызывает Библиотекарь `/veto` (timeout 30s)
4. Polling ALF ответа в `outbox/alf/.notified/` + `archive/` каждые 2 сек
5. Когда ALF ответил (или timeout 90s) — финальный вердикт
6. Persist в `/root/matryoshka/council/logs/{council_id}.json`

**Матрица решений:**
- `librarian.veto=true` → rejected
- `alf_vote=against` → rejected
- `alf_vote=for + librarian.ok` → accepted
- `alf null (timeout) + librarian.ok` → accepted (fallback)
- `alf null + librarian.veto` → rejected

**Результаты тестирования 23.06.2026 14:25-14:39:**
- 6 council тестов, 5 успешных ALF голосов + 1 timeout fallback
- Council #2: ALF ПРОТИВ Router как SPOF → rejected
- Council #6: ALF ЗА, 34.3 сек turnaround → accepted

**Баг найден и исправлен:** `Path.glob` race condition → `os.listdir` + `in fname`.

---

## Новые ключевые файлы Phase 2

| Файл | Что |
|------|-----|
| `/root/matryoshka/.hermes/ALF_CURRENT_STATE_23.06.md` | **DEFINITIVE** состояние ALF на 23.06.2026 |
| `/root/matryoshka/.hermes/ALF_DEEP_AUDIT_23.06.md` | Deep audit 23.06 (5 критичных находок) |
| `/root/matryoshka/.hermes/ALF_ROLE_PROPOSAL_23.06.md` | План Phase 1+2+3 |
| `/root/matryoshka/alf/knowledge/23.06_AUDIT_AND_FIXES.md` | KB authoritative правда (создан 23.06) |
| `/root/matryoshka/bin/alf_librarian.py` | Библиотекарь (9.8 KB) |
| `/root/matryoshka/bin/matryoshka_router.py` | Router v0.3 (18.7 KB) |
| `/root/matryoshka/bin/alf_watchdog.sh` v2 | Watchdog (5.4 KB) |
| `/root/matryoshka/bin/alf_healthcheck.py` | Healthcheck :8452 (6.4 KB) |
| `/root/matryoshka/council/logs/*.json` | 6 Council решений |

---

*Файл создан 18.06.2026 22:30, обновлён 23.06.2026 14:42 (Phase 2). При изменениях — обновлять существующий файл, не плодить v4.1/v5/etc.*
