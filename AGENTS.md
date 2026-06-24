# MATRYOSHKA DIGITAL — Проектные правила v4.0

> **Для AI-агентов (ALEX, HERMES)**: оперативные команды, порты, протоколы — в [`readme-for-agents.md`](readme-for-agents.md).
> **Обновлено 18.06.2026 22:35** после обсуждения роя v4.0. Полный протокол: `/root/matryoshka/.hermes/SWARM_V4_DECISION.md`
> **Правило v4.0:** обновлять СУЩЕСТВУЮЩИЕ файлы, не плодить новые версии.

## Проект
MATRYOSHKA DIGITAL — IT-компания, предоставляющая AI-сотрудников (HERMES, ALEX, ALF, ALISA) + защищённый VPN. Отдельный кейс: **ALINA** — клиентский бот для Николая (@NikolaAlinaBot, связан с HERMES).

## Архитектура v4.0 — ГИБРИД

### ⚪ Белый Рой (Мозг) — VPS
- **HERMES** — Дирижёр Оркестра (VPS, MiniMax-M3, профиль `hermes-cli`)
- **ALF** — Стратег + Librarian (VPS, профиль `alf`, **отдельный процесс `hermes-gateway-alf.service`**)

### 🔵 Синий Рой (Система) — ПК Олега
- **ALEX** — Технический инженер (Windows ПК, opencode через ACP :4096)

### 🔴 Красный Рой (Витрина)
- **ALISA** — Маркетинг / Контент (@AlisaMatBot, отложена)

### 👤 Клиентский кейс (ОТДЕЛЬНЫЙ от роя Олега)
- **ALINA** — AI-ассистент для клиента Николая (@NikolaAlinaBot, профиль `alina-prod`)

## Цепочка управления v4.0

```
ОЛЕГ (Директор, @oleglab22, ID 1951845052)
  ↓ Telegram (ТОЛЬКО через HERMES)
HERMES (Дирижёр, VPS) ← единственная точка входа
  ├→ ALEX (через ACP :4096)
  ├→ ALF  (через профиль alf / @IlonAnalyticBot)
  ├→ ALINA (ОТДЕЛЬНЫЙ КЕЙС, @NikolaAlinaBot)
  └→ ALISA (отложена)

ALF → ALEX: только через HERMES (через .hermes_task_alf.json)
```

**v4.0 vs v3.3:**
- ALF теперь ОТДЕЛЬНЫЙ systemd-процесс (не persona внутри HERMES)
- ALF может ИНИЦИИРОВАТЬ задачи ALEX через HERMES (раньше только Олег мог)
- ALINA жёстко изолирована (отдельный venv, профиль, доступ)

## Архитектура роя (workflow)

1. **Олег** ставит задачу **HERMES** через Telegram
2. **HERMES** декомпозирует по роям:
 - 🔵 Техническая часть → **ALEX** (через ACP :4096 или `.hermes_task.json`)
 - ⚪ Логическая/аналитическая → **ALF** (через профиль `alf`)
 - 🔴 Графика/визуал/контент → **ALISA** (отложена)
 - ⚪ Стратегическая — ALF может сам поставить задачу ALEX через `.hermes_task_alf.json`
3. Каждый агент выполняет свою часть
4. **HERMES** собирает результаты и формирует отчёт **Олегу**

> ⚠️ **ALEX НЕ общается с Олегом напрямую** — только через HERMES.
> ⚠️ **ALF ↔ ALEX только через HERMES** — никаких прямых каналов.
> ⚠️ **ALINA** — отдельный кейс для клиента Николая. **Не часть роя Олега.** Изоляция данных v3.2.

### ❌ НЕ СУЩЕСТВУЕТ (удалить все упоминания)
- ARCHITECT-X — никогда не существовал
- ECLER / Ecler — переименована в ALINA 07.06.2026
- ILON / TOLIK — не существует
- OpenClaw — заменён на Hermes Agent
- ALEX в облаке — ALEX только на ПК
- ~~alf-prod / alf-prod-*~~ — **удалено 18.06.2026** (ALF = `hermes-gateway-alf.service`)

## Инфраструктура (контуры)

- **VPS**: `85.137.166.209` (Чехия, SmartApe) — HERMES, ALF, ALISA, ALINA, n8n, nginx, xray
- **ПК Олега** (Windows): ALEX через opencode
- **VPN**: AmneziaWG, сеть `10.8.1.0/24` (VPS=`10.8.1.1`, ПК=`10.8.1.4`)

### Каналы HERMES↔ALEX (см. readme-for-agents.md §4):
 - **PRIMARY** — ACP (VPN, порт 4096)
 - **BACKUP** — HTTP Bridge `alex_bridge.py` (VPN, порт 8446) — отключён 15.06
 - **FALLBACK** — Cloudflared TCP-туннель на `:8446` — отключён 15.06

### Каналы ALF↔ALEX (v4.0):
 - **PRIMARY** — через HERMES, файл `/root/matryoshka/.hermes_task_alf.json`
 - ALF пишет задачу → HERMES читает → маршрутизирует в ACP → ALEX выполняет → результат в `.hermes_result.json`

> 📋 Полная таблица портов, команд SSH/Docker, переменных окружения — в [`readme-for-agents.md`](readme-for-agents.md).

## Управление локальными сервисами v4.0

| Сервис | Тип | Управление |
|--------|-----|-----------|
| `hermes-cli-gateway.service` | systemd (VPS) | `systemctl {start,stop,restart,status}` |
| `hermes-gateway-alf.service` | systemd (VPS) ✅ NEW | то же |
| `alina-prod-gateway.service` | systemd (VPS) | то же |
| `alina-prod-*.service` (7 шт) | systemd (VPS) | для микросервисов Алины |

> ❌ **Запрещено**: `taskkill /F /IM python.exe` — убивает все процессы. Только `systemctl` или `kill <PID>` конкретного процесса.
> Полный workflow «сервис упал» — в [`readme-for-agents.md`](readme-for-agents.md] §2.

## Протокол HERMES (файловая очередь) v4.0

| Файл | Назначение | Кто пишет | Кто читает |
|------|------------|------------|------------|
| `.hermes_task.json` | задача для ALEX | HERMES / Олег | ALEX |
| `.hermes_result.json` | результат от ALEX | ALEX | HERMES |
| `.hermes_task_vps.json` | задача для VPS-части | HERMES | cron / systemd |
| **`.hermes_task_alf.json`** | **задача от ALF к ALEX через HERMES** ✅ NEW | **ALF** | **HERMES** |

**Цикл ALEX**: читает `.hermes_task.json` → если `status == "pending"` → выполняет → пишет в `.hermes_result.json`.

**Цикл v4.0 ALF**: пишет в `.hermes_task_alf.json` (status=pending) → HERMES видит → перекладывает в `.hermes_task.json` → ALEX выполняет.

## Структура .opencode/
- `.opencode/agents/` — саб-агенты (@hermes-handler, @infra-check)
- `.opencode/commands/` — кастомные команды (/ssh, /check, /deploy, /vpn, /fix)
- `.opencode/tools/` — кастомные инструменты (hermes-respond, n8n-trigger)
- `.opencode/skills/` — навыки (vpn-config, deploy, log-analyst, hermes-protocol)

## Ключевые файлы v4.0

| Файл | Что |
|------|-----|
| [`readme-for-agents.md`](readme-for-agents.md) | Оперативная сводка для агентов (порты, команды, протоколы) |
| `/root/matryoshka/.hermes/SWARM_V4_DECISION.md` | **Протокол обсуждения v4.0** ✅ NEW |
| `/root/.hermes/AGENTS.md` | Архитектура + RECALL PROTOCOL (system prompt) |
| `SOUL.md` | Идентичность ALEX |
| `.env` / `SECRETS/.env` | Секреты (**не коммитить, не выводить значения**) |
| `PRIORITY_PLAN.md` | Приоритетный план (P0 завершён) |
| `MASTERPLAN.md` / `ROADMAP_W22_2026.md` | Долгосрочные планы |
| `CLAUDE.md` | legacy (историческая справка) |

> Полная карта директорий — в [`readme-for-agents.md`](readme-for-agents.md) §8.

## GitHub (25.05.2026, обновлено 18.06.2026)
- Org: `matGT2205` (private) — для MATRYOSHKA
- Репо: **matGT2205/matryoshka-repo**
- Push крупных файлов (>50MB) через VPS-fallback (токен `REDACTED_GH_TOKEN`, инструкция в readme §10)
- **Для ALINA (Николай)**: личный GitHub Николая — инструкция в `/root/matryoshka/cases/nikolay/ALINA_GITHUB_SETUP.md` ✅ NEW

## Провайдеры AI на ПК
opencode (Zen, **ОСНОВНОЙ**: qwen3.6-plus-free, claude-*, gemini-*, kimi-*, nemotron-*), deepseek, nvidia, cloudflare-workers-ai, cloudflare-ai-gateway.

## Стек
Python, PowerShell, JavaScript/TypeScript · Docker · systemd · Nginx · n8n · OpenCode Zen API · Telegram Bot API · WebSocket · FastAPI · Node.js 20+

## 📊 История версий

- **v4.1 (19.06.2026 09:35)** — SHARED BRAIN Phase 1 реализован: /root/matryoshka/shared_brain/ (WAL + DIGEST + append_wal.py + хуки on_session_end в 3 профилях). hermes_active_flush.py → v2 (multi-profile). RECALL PROTOCOL шаг 0 = shared_brain/DIGEST.md. Фикс «HERMES забывает». Олег мандат: «у всех должна быть общая память».
- **v4.0 (18.06.2026 22:35)** — Гибрид иерархии, ALF→ALEX через HERMES, Obsidian+session_search, ALINA изолирована
- v3.3 (16.06.2026) — MIRROR SYNC mandate, разделение роя
- v3.0 (07.06.2026) — ECLER → ALINA, 3 РОЯ
- v2.x (25.05.2026) — GitHub integration, OpenCode на ПК

---

**Правило v4.0:** обновлять СУЩЕСТВУЮЩИЕ файлы, не плодить v4.1/v5/FINAL.
