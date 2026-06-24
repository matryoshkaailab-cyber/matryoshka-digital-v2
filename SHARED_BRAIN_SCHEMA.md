# SHARED BRAIN — Schema & WRITE-AUTHORITY

> **Часть Phase 1: WAL + Digest + NBSync**
> **Создан:** 2026-06-18 23:15
> **Файл:** `/root/matryoshka/SHARED_BRAIN_SCHEMA.md`

---

## 🎯 Что это

Единый источник правды о том, **кто** имеет право писать в какие файлы SHARED BRAIN. Без этой матрицы — конфликты, stale data, "ALF = persona" vs "ALF = личность".

---

## 📐 Матрица зон (WRITE-AUTHORITY)

| Зона (файл) | HERMES | ALF | ALEX | Олег (напрямую) |
|-------------|:------:|:---:|:----:|:---------------:|
| `SHARED_BRAIN.md` (полный лог) | ✅ write | ❌ только через HERMES | ❌ только через HERMES | ❌ через HERMES |
| `SHARED_BRAIN_DIGEST.md` (30 строк) | ✅ auto-gen | ❌ read-only | ❌ read-only | 👁 read |
| `.sessions/DIGEST.md` (per-agent) | ✅ свой | ✅ свой | ✅ свой | 👁 read |
| `.sessions/WAL/*.jsonl` (write-ahead log) | ✅ write | ✅ append | ✅ append | ❌ через HERMES |
| `.sessions/SHARED_BRAIN.lock` | ✅ acquire | ✅ acquire | ✅ acquire | — |
| `AGENTS.md` (правила роя) | ✅ update | ❌ PR | ❌ PR | ✅ direct + review |

### Правило конфликта (supersede)

Если два агента пишут в WAL одновременно — последняя запись supersedes предыдущую, **НО** старая запись остаётся в WAL с пометкой `superseded_by: <new_entry_id>`.

---

## 📋 Структура одной WAL записи (JSONL)

```json
{
  "id": "wal-2026-06-18T23:15:00Z-hermes-001",
  "ts": "2026-06-18T23:15:00Z",
  "op": "create|update|delete|supersede",
  "author": "hermes|alf|alex|oleg",
  "path": "SHARED_BRAIN.md#section-3.2",
  "version": 1,
  "supersedes": null,
  "content": "ALF = отдельный агент, не persona",
  "digest": "ALF=agent",
  "trust": 0.95,
  "source": "v4.0-disussion|user-direct|system-event"
}
```

### Поля
- `id` — уникальный идентификатор
- `ts` — ISO 8601 UTC
- `op` — операция
- `author` — кто написал
- `path` — какой файл/секция
- `version` — монотонно растёт для одного path
- `supersedes` — id предыдущей записи (если есть)
- `content` — текст (≤200 символов)
- `digest` — сокращённая версия (≤50 символов)
- `trust` — 0.0..1.0 (доверие к источнику)
- `source` — откуда пришло

---

## 🔐 Lock-протокол

```python
LOCK_PATH = "/root/matryoshka/.sessions/SHARED_BRAIN.lock"

def acquire_lock(timeout=10):
    # O_CREAT|O_EXCL — атомарно создаёт файл или возвращает ошибку
    # Если файл существует — ждём до timeout
```

**Правило:** перед ЛЮБОЙ записью в SHARED_BRAIN.md или WAL — `acquire_lock()`. После записи — `release_lock()`.

---

## 📊 Digest (30 строк) — что включать

```markdown
# SHARED BRAIN DIGEST — {timestamp}

## P0 Decisions (4)
1. ...
2. ...
3. ...
4. ...

## Active Entities (10)
- HERMES (PID xxx)
- ALF (PID xxx)
- ...

## Pending Operations
- ...

## Open Questions
- ...

## Superseded (last 5)
- wal-xxx → wal-yyy (reason)
```

**Исключить:** полные файлы, логи, git diff, env values.

---

## 🚨 Конфликт-резолв

Если Олег или агент видит что WAL содержит `supersedes`-цепочку >3 уровней → это сигнал для HERMES review:
- Проверить что новые данные правильные
- Удалить старые если obsolete
- Сделать announce в Digest

---

*Файл обновляется при изменении правил. Автор изменений: HERMES (после обсуждения с ALF и ALEX).*
