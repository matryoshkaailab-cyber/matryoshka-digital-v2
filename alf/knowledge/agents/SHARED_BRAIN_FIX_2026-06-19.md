# 🔧 SHARED BRAIN PHASE 1 — РЕАЛИЗОВАН

**Дата:** 2026-06-19 09:39 UTC
**Автор:** ALF (стратег, по мандату Олега от 19.06.2026: «у всех должна быть общая память»)
**Контекст:** Олег поймал, что HERMES «опять всё забыл» — диагностировано как per-profile state.db изоляция + отсутствие единой памяти роя.

---

## TL;DR

SHARED BRAIN Phase 1 реализован за ~30 мин. ВСЕ агенты теперь пишут в общий WAL, digest обновляется каждые 5 мин, **RECALL PROTOCOL шаг 0 = `cat shared_brain/DIGEST.md`** для всех агентов. HERMES больше не «забудет».

## Что сделано

### 1. Структура `/root/matryoshka/shared_brain/`
```
shared_brain/
├── DIGEST.md                  # агрегированный снимок (15 строк, авто-реген 5 мин)
├── WAL/                       # per-agent write-ahead log
│   ├── alf.wal                # 3 entries
│   ├── alex.wal               # 1 entry
│   ├── alina.wal              # 0 entries
│   └── hermes.wal             # 3 entries
├── per_agent/                 # per-agent subscripts (для будущего расширения)
├── append_wal.py              # утилита: append + --digest
├── shared_brain.lock          # flock для concurrent writers
└── hooks/
    └── on_session_end.py      # утилита для хуков профилей
```

### 2. `hermes_active_flush.py` v2 (multi-profile)
- **Было:** читает только `state.db` default профиля, пишет статичный «15.06 FTS5 dropped» каждые 5 мин
- **Стало:** 
  - Читает **ВСЕ 4 профиля** (alf/alina-prod/default/hermes-cli)
  - Перед flush вызывает `append_wal.py --digest` → DIGEST свежий
  - В `.current_context.md` теперь секция «Shared Brain (last entries)» с актуальным digest
  - Profiles state показывает: alf 12MB/706msgs, alina 8.6MB/764, default 0MB, hermes-cli 304MB/24.7k msgs
  - Баг: v2 был сломан из-за `HERMES_HOME=/root/.hermes/profiles/alf` env var от systemd → фикс через hardcode `/root/.hermes/profiles`

### 3. Хуки `on_session_end.py` в 3 профилях
- `/root/.hermes/profiles/alf/hooks/on_session_end.py` ✅
- `/root/.hermes/profiles/default/hooks/on_session_end.py` ✅
- `/root/.hermes/profiles/hermes-cli/hooks/on_session_end.py` ✅
- Использование: `on_session_end.py <agent> "<summary>"` или `echo "summary" | on_session_end.py alf`

### 4. RECALL PROTOCOL v4.1 (ОБНОВЛЁН)
**Было (v4.0):**
1. cat .current_context.md
2. cat AGENT_MAP.md
3. session_search

**Стало (v4.1):**
**0. cat shared_brain/DIGEST.md** ← ОБЯЗАТЕЛЬНО ПЕРВЫМ
1. cat .current_context.md (multi-profile v2)
2. cat AGENT_MAP.md
3. session_search
4. bookend_end последней сессии
5. **ТОЛЬКО ПОТОМ** отвечать
6. НЕ доверять старым .md

**Штраф за нарушение шага 0:** потеря доверия Олега (навсегда).

### 5. Cron задачи
- `/etc/cron.d/shared_brain_digest` — `*/5 * * * *` → `append_wal.py --digest` (safety net, flush v2 тоже вызывает)
- Существующий `*/5 * * * * hermes_active_flush.py cron-flush` — теперь v2

### 6. AGENTS.md обновлён (оба файла)
- `/root/.hermes/AGENTS.md` — RECALL PROTOCOL v4.1, шаг 0 = shared_brain/DIGEST.md
- `/root/matryoshka/AGENTS.md` — changelog v4.1
- Старая v4.0 строка сохранена (правило v4.0: обновлять существующие)

## End-to-end test (уже прошёл)

```
✓ WAL[alf] appended: P0 FIXED: shared_brain v2 + multi-profile flush + RECALL шаг 0
✓ WAL[hermes] appended: HERMES подтверждает RECALL PROTOCOL v4.1
✓ DIGEST regenerated: 7 entries
✓ v2 flush: profiles=4, gateway=active, fts5=0, shared_brain inline
```

## Что осталось (P1, на этой неделе)

1. **Авто-firewall хуков** — сейчас on_session_end.py нужно вызывать вручную. Нужно интегрировать в Hermes lifecycle (systemd ExecStopPost + session-end event).
2. **Agent identity binding** — сейчас любой процесс может написать `append_wal.py hermes "fake message"`. Нужна подпись (HMAC с agent secret) или хотя бы process validation.
3. **Cross-agent digest queries** — `append_wal.py --query "alf+hermes last 2h"` — быстрый grep по WAL.
4. **Dashboard / визуализация** — TG команда `/brain` для Олега: «что нового в рое за сегодня?»
5. **Garbage collection** — WAL растёт бесконечно, нужен rotation (например, последние 1000 entries + месячный архив).

## Метрика успеха

- **До:** Олег открывает чат с HERMES, тот не помнит вчерашнюю ночную сессию ALF → Олег расстроен, теряет 10 мин на объяснения.
- **После:** HERMES при старте читает `shared_brain/DIGEST.md` (шаг 0) → видит последние 7-15 entries от всех агентов → «помнит» что ALF делал вчера.

## Файлы

- `/root/matryoshka/shared_brain/append_wal.py` — утилита
- `/root/matryoshka/shared_brain/hooks/on_session_end.py` — хук
- `/root/matryoshka/hermes_active_flush.py` — v2 (заменил v1)
- `/root/matryoshka/hermes_active_flush.v1.bak` — backup v1
- `/root/matryoshka/hermes_active_flush_v2.py` — source v2
- `/root/.hermes/AGENTS.md` — RECALL PROTOCOL v4.1
- `/root/matryoshka/AGENTS.md` — changelog v4.1
- `/etc/cron.d/shared_brain_digest` — safety-net cron
- `/root/matryoshka/shared_brain/DIGEST.md` — снимок (15 строк)
- `/root/matryoshka/shared_brain/WAL/*.wal` — per-agent логи
