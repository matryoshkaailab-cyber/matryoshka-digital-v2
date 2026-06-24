# Council #2.0 (Этап 2) — 21.06.2026

**Тема:** Реализация 3 фич Hermes v0.17 в системе MATRYOSHKA:
1. Sub-agents (5 параллельных)
2. Multiple profiles (alf-strategist, alf-librarian)
3. Agent loops (builder + judge)

## 3 ЭТАПА (методология Олега 21.06.2026)

### Этап 1: СОБРАТЬ — DONE
- Аликс ИИ (11.8с + 71.8с): profiles 1-й, sub-agents 2-й, agent loops 3-й
- ALF (стратег/библиотекарь): schema → librarian → profiles (ДРУГОЙ ПОРЯДОК)
- Гермес (мой): profiles 1-й, sub-agents 2-й, agent loops 3-й

### Этап 2: ПЕРЕПРОВЕРИТЬ (counter-аргументы) — DONE
- Аликс опроверг 6/8 рисков:
  - #1 Knowledge fragmentation — ПРЕУВЕЛИЧЕН
  - #2 Cookie storm — ПРЕУВЕЛИЧЕН (Telegram stateless, нет cookies)
  - #3 Self-judge — СОГЛАСЕН УСЛОВНО
  - #4 Identity confusion — ПРЕУВЕЛИЧЕН
  - #5 Misroute — СОГЛАСЕН
  - #6 Race condition — СОГЛАСЕН, ВЫ НЕДООЦЕНИЛИ (P0)
  - #7 Schema migration — НЕВЕСОМ
  - #8 Council без WAL — ПРЕУВЕЛИЧЕН (для council хватит git append-only)

### Этап 3: SYNTHESIS (Олег применил 3 правки 21.06.2026):
1. **P3 → P1** (Council append-only ledger — не откладывать)
2. **P0 race window fix** (mv + commit в одной транзакции: subshell / worktree / hook)
3. **P1 kind enum расширить** (alf, alina-prod, alf-strategist, alf-librarian + backward-compat kind='')

## SELF-JUDGE FIX (пометка для будущего):
Holdout = 5 зафиксированных Q&A (sanity floor, ловит 80% regression). НЕ сейчас.

## РЕШЕНИЕ (Олег одобрил 21.06.2026)

**СТАРТ можно давать** после применения 3 правок.

### ПЛАН (финальный, после правок):

| Приоритет | Действие | Статус |
|-----------|----------|--------|
| **P0** | File lock / atomic write для `.hermes_result.json` (mv + commit в одной транзакции) | NEXT |
| **P1** | Council append-only ledger в git (`council/2026-06-21-*.md`) | NOW (этот файл) |
| **P1** | `kind` enum в `.hermes_task.json` (alf/alina-prod/alf-strategist/alf-librarian + legacy) | NEXT |
| P2 | Exponential backoff для 429 rate-limit | LATER |
| — | append-only markdown в git для audit | DONE (этот файл) |

## DISSENTING OPINIONS

- Аликс: schema v2 dual-write = bug-free (НЕ миграция)
- ALF: holdout 5 Q&A для agent loop (не сейчас)
- Олег: всё, что я сказал, — корректировки к этому плану

## ПРИНЯТО (Олег, 21.06.2026 03:35 CEST)

## alf-librarian v1.1 (21.06.2026 03:42 CEST)

- Telegram УБРАН (общий токен с ALF → conflict)
- File-queue через `.hermes_task_librarian.json` + cron watcher (60s)
- systemd unit: hermes-gateway-alf-librarian.service — ACTIVE
- bin/librarian_watcher.py: poll → process → write outbox

### Доступ
- ALF/ALEX → пишут в `.hermes_task_librarian.json` (kind=librarian)
- librarian_watcher.py читает каждые 60 сек
- Результат в `swarm/outbox/librarian/<task_id>.json`
- Олег может вызвать через Telegram-мост или HTTP /librarian endpoint (TODO)

## alf-librarian v1.2 — ЧАСТИЧНО (21.06.2026 03:46)

**Создано:**
- /root/.hermes/profiles/alf-librarian/ (config + SOUL.md + .env)
- personality: librarian
- toolsets: [notebooklm, research, memory, file, session_search, skills]
- model: openrouter/minimax/MiniMax-M3 (TODO: minimax provider)

**НЕ РАБОТАЕТ:**
- v0.17 НЕТ `file` platform (только telegram, slack, signal, webhook, etc)
- systemd unit удалён (alf-librarian = НЕ gateway, а agent)
- `hermes chat --profile alf-librarian` возвращает "no final response" (timeout?)

**TODO:**
- Тест через ALF delegate (sub-agent v0.17): alf-strategist / alf-librarian как sub-agents ОДНОГО gateway
- Или через ALF-librarian как cron job (hermes -p с prompt)
- Переключить model на provider=minimax (НЕ openrouter)
- Создать отдельный Telegram bot через @BotFather (TODO: Олег)
