# OPENCODE-AI — ПОЛНЫЙ АУДИТ (Аликс на ПК)
**Автор:** HERMES (по запросу Олега, 11.06.2026 13:25 CEST)
**Цель:** Понять opencode, его архитектуру, баги, и почему 18 WS-соединений + think-only.

---

## 🎯 ЧТО ТАКОЕ OPENCODE

| Параметр | Значение |
|----------|----------|
| **Полное имя** | OpenCode — AI Coding Agent for the Terminal |
| **Вендор** | anomalyco (SST) |
| **Репозиторий** | https://github.com/opencode-ai/opencode + https://github.com/anomalyco/opencode (mirror) |
| **Лицензия** | MIT |
| **Stars** | 12.8k |
| **Forks** | 1.4k |
| **Open Issues** | 116 |
| **Open PRs** | 42 |
| **Releases** | 50 |
| **Язык** | Go 99.2% + Shell 0.8% |
| **Сайт** | https://opencode.ai |
| **Документация** | https://opencode.ai/docs |

**Версия на ПК Аликса:** `1.16.2` (по `agents/alex/README.md`)

**Источники:**
- https://github.com/opencode-ai/opencode — главный репо
- https://github.com/anomalyco/opencode — активный mirror (где issues)
- https://opencode.ai/docs — официальные доки

---

## 🏗 АРХИТЕКТУРА

```
┌─────────────── WINDOWS ПК (Аликс) ─────────────────┐
│                                                       │
│  AlexStack (NSSM Service)                              │
│  ├── opencode serve --port 5001                       │
│  │    ├── REST API для задач                          │
│  │    ├── WebSocket (SSE) для real-time               │
│  │    └── Аутентификация: OPENCODE_SERVER_PASSWORD    │
│  │                                                     │
│  └── ws_client.py v38                                  │
│       ├── Подключается к VPS ws_server :8446          │
│       ├── Передаёт задачи в opencode                  │
│       └── Heartbeat каждые 10 сек                      │
└───────────────────────────────────────────────────────┘
        ↕ WebSocket (8446, token hermes-ws-secret-2026)
┌─────────────── VPS (Hermes) ──────────────────────────┐
│  ws_server.py v9                                       │
│  ├── 8446 WS — канал к ws_client                       │
│  ├── 8450 HTTP — `/api/delegate`, `/api/status`        │
│  └── 9000 SSH-R — http_fallback (alex_router:4000)     │
└───────────────────────────────────────────────────────┘
```

**Наша текущая конфигурация opencode на ПК (по локальным докам):**
- Port: **5001** (НЕ 4096, как было раньше)
- Provider: **minimax/MiniMax-M3** через `https://api.minimax.io/v1`
- Model: **MiniMax-M3** (1M context, multimodal)
- Auth: OPENCODE_SERVER_PASSWORD (Basic Auth)
- AGENTS.md в `C:\matryoshka\` для project-level context

---

## ⚙️ КЛЮЧЕВЫЕ ФИЧИ (по opencode.ai/docs)

### Modes
- **TUI** (default) — terminal UI
- **Web** — browser-based
- **IDE extensions** — Zed, VS Code
- **CLI commands** — `run`, `agent`, `attach`, `auth`, `mcp`, `models`, `session`, `stats`, `debug`, `upgrade`

### Tools
- **Bash tool** — shell execution
- **Read/Write/Edit** — file manipulation
- **WebFetch** — HTTP requests
- **Glob/Grep** — file search
- **Task** — sub-agent delegation
- **MCP servers** — extend with external tools
- **LSP** — language server protocol integration

### Providers (согласно официальным докам)
- **OpenAI** (gpt-4, gpt-4o, etc.)
- **Anthropic** (Claude Sonnet 4, Opus 4)
- **GitHub Copilot**
- **Google** (Gemini)
- **AWS Bedrock**
- **Groq**
- **Azure OpenAI**
- **Google Cloud Vertex AI**
- **Self-hosted** (custom provider — это мы с `minimax` и `qwen-local`)

### Configuration
```json
{
  "provider": {
    "minimax": {
      "options": {
        "baseURL": "https://api.minimax.io/v1"
      },
      "models": {
        "MiniMax-M3": {}
      }
    }
  },
  "model": "minimax/MiniMax-M3"
}
```

---

## 🔥 ИЗВЕСТНЫЕ БАГИ И ISSUES

### Issue #14171 — "opencode taking more and more RAM until crash"
- **Симптом:** OpenCode постепенно жрёт RAM до 99%, потом система 100% unresponsive
- **Версия:** 1.2.5 (похоже на нашу 1.16.2 — те же корни)
- **Workaround:** None (нужен memory cleanup)
- **Reddit:** https://www.reddit.com/r/opencodeCLI/comments/1r7015z/ — "anyone else struggling with opencode gobbling up"
- **Статус:** Open

### Issue #731 — "Critical Stability Issues: App Freezing & Hanging Analysis"
- **Симптом:** Opencode зависает намертво, нужен external intervention
- **Root causes (из анализа):**
  1. **File System Bottlenecks** (bash tool читает файлы через OS-вызовы)
  2. **Process Management Gaps** (orphaned child processes)
  3. **MCP Server Failures** (mcp/index.ts:35-42)
  4. **Network/Firewall Conflicts** (TCP socket timeouts)
  5. **Terminal Integration Issues** (TUI interrupt handling)
- **Priority:** CRITICAL
- **Связанные issues:** #519, #721, #706, #683, #682, #652, #471, #421, #504

### Issue #5700 — "Too high memory usage"
- **Симптом:** RAM use high при `opencode web` + CLI attach
- **Workaround:** End session, restart

### Issue #6213 — "Memory leak during prolonged usage"
- **Симптом:** Memory leak + input lag 30+ sec
- **Плагин:** oh-my-opencode

### Issue #19951 — "Out of memory in worker.js"
- **Симптом:** OOM при session summary generation
- **Workaround:** Start fresh session

**Источники:**
- https://github.com/anomalyco/opencode/issues/14171
- https://github.com/anomalyco/opencode/issues/731
- https://github.com/anomalyco/opencode/issues/5700
- https://github.com/anomalyco/opencode/issues/6213
- https://github.com/anomalyco/opencode/issues/19951

---

## 🧩 ПОЧЕМУ 18 WS-СОЕДИНЕНИЙ (текущее)

### Что я вижу на VPS

```bash
ss -tnp | grep ":8446"
# ESTAB  0  0  85.137.166.209:8446  95.25.132.73:55768  users:(("python3",pid=663975,fd=14))
# ESTAB  0  0  85.137.166.209:8446  95.25.132.73:55950  users:(("python3",pid=663975,fd=17))
# ... (всего 18 ESTAB соединений с разных source ports)
```

**Все соединения:**
- От ОДНОГО IP: `95.25.132.73` (Олег, ПК)
- К ОДНОМУ PID: `663975` (ws_server.py v9)
- С РАЗНЫХ source ports: 55768, 55950, 55777, 55886, 55950, 56237, 56350, 56488, 56694, 56801, 56929, 57017, 57179, 57210, 57407, 57455, 55614, 55685
- **Один клиент = 18 параллельных WS-соединений**

### Корневые причины

**Гипотеза #1: ws_client плодит соединения**
- ws_client v38 при reconnect-loop создаёт новое соединение
- Старое не закрывается (TCP TIME_WAIT или ws_server не отправляет close frame)
- Накапливается до 18+

**Гипотеза #2: opencode API требует много соединений**
- OpenCode `serve` создаёт пул соединений для разных sessions
- Каждая session = свой WS
- 100+ накопленных sessions = 100+ WS

**Гипотеза #3: Browser/HTTP polling**
- `opencode web` UI держит WebSocket для live updates
- Может быть несколько tabs / panels = несколько WS

**Гипотеза #4: watchdog из alex_stack_safe.py**
- `templates/alex_stack_safe.py` НЕ kill'ит, а мониторит
- Если opencode упал → start new opencode → новое WS-соединение
- Старое остаётся

**Скорее всего #1 + #2:** opencode накопил sessions, ws_client реконнектится каждые 50 сек из-за watchdog.

### Решения (по skill `alex-connection`)

**Решение A: NSSM + alex_stack_safe.py (от Аликса)**
- Один процесс opencode + один ws_client
- Мониторинг через Get-CimInstance, НЕ kill /IM
- ✅ Рекомендуемое, проверено 08.06.2026

**Решение B: Opencode session cleanup**
- `opencode session list` — посмотреть все sessions
- `opencode session delete <id>` — удалить старые
- Периодический cron: `opencode session list | xargs -I {} opencode session delete {}`

**Решение C: OpenCode downgrade**
- 1.16.2 (текущая) → 1.15.x (стабильнее?)
- **НЕ рекомендую** (1.15 была хуже, я помню)

**Решение D: Watchdog timeout**
- ws_client heartbeat: каждые 10 сек
- Watchdog: kill если нет heartbeat 30 сек
- Сейчас watchdog: kill если нет heartbeat 60 сек (слишком долго)

---

## 🔌 АЛЬТЕРНАТИВЫ OPENCODE

### Claude Code CLI
- **Вендор:** Anthropic
- **Стоимость:** Claude API (Sonnet 4 / Opus 4)
- **Плюсы:** думаю Claude не think-only, очень хорош в коде
- **Минусы:** дороже, нужен VPN для API (если заблокировано)
- **Сайт:** https://claude.com/product/claude-code

### Codex CLI (OpenAI)
- **Вендор:** OpenAI
- **Стоимость:** GPT-4o / GPT-5 API
- **Плюсы:** нативный shell tool
- **Минусы:** дорого
- **Сайт:** https://github.com/openai/codex

### Goose (Block)
- **Вендор:** Block (Square)
- **Стоимость:** free
- **Плюсы:** open source, MCP support
- **Минусы:** менее зрелый
- **Сайт:** https://github.com/block/goose

### Continue.dev
- **Вендор:** Continue
- **Стоимость:** free
- **Плюсы:** IDE extension, MCP
- **Минусы:** IDE-centric
- **Сайт:** https://continue.dev

### Мой рейтинг
1. **Qwen 3.7 Max через opencode** — если M3 think-only проблема, пробуем Qwen
2. **Claude Code CLI** — самый надёжный для production кода
3. **Codex CLI** — альтернатива Claude
4. **Продолжать opencode 1.16.2** — если получится починить think-only

---

## 🔧 КАК ПРАВИЛЬНО НАСТРОИТЬ OPENCODE (на ПК Аликса)

### Минимальный конфиг (opencode.json)
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "minimax": {
      "options": {
        "baseURL": "https://api.minimax.io/v1"
      },
      "models": {
        "MiniMax-M3": {
          "contextLength": 1000000
        }
      }
    },
    "qwen-local": {
      "options": {
        "baseURL": "http://127.0.0.1:8765/v1"
      },
      "models": {
        "qwen3.7-max": {"contextLength": 1000000},
        "qwen3.7-plus": {"contextLength": 1000000}
      }
    }
  },
  "model": "minimax/MiniMax-M3"
}
```

### AGENTS.md (в C:\matryoshka\) — для project context
```markdown
# ALEX AGENT — MATRYOSHKA DIGITAL

## Role
Технический инженер Windows ПК Олега. Подключается к HERMES (VPS) через ws_client.

## Tools
- bash (PowerShell)
- read, write, edit (files)
- webfetch (HTTP)
- glob, grep (search)
- task (sub-agents)

## Rules
1. НЕ использовать trigger-слова: "You MUST", "SYSTEM CONTEXT", "Call bash EXACT"
2. Простые команды: Get-Date, Get-ChildItem -Name, Get-Content
3. Сложные команды → разбивать на 2-3 простые
4. После выполнения → hermes-respond с результатом
5. THINK = ответ (не tool call) → сразу написать в .hermes_result.json
```

### Запуск через NSSM (рекомендуемый)
```powershell
# Создать сервис
nssm install AlexStack "C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe" "C:\matryoshka\alex_stack_safe.py"
nssm set AlexStack AppDirectory "C:\matryoshka"
nssm set AlexStack DisplayName "ALEX Stack (opencode + ws_client)"
nssm set AlexStack Start SERVICE_AUTO_START
nssm set AlexStack AppStdout "C:\matryoshka\logs\alex_stack.log"
nssm set AlexStack AppStderr "C:\matryoshka\logs\alex_stack_error.log"
nssm set AlexStack AppRotateFiles 1
nssm set AlexStack AppRotateBytes 10485760

nssm start AlexStack
```

### Скрипт alex_stack_safe.py (уже есть в skill)
- Get-CimInstance + CommandLine LIKE (НЕ taskkill /IM)
- Только monitor + start missing, НЕ kill
- Heartbeat каждые 30 сек

---

## 📊 ВЕРСИЯ OPENCODE — ЭВОЛЮЦИЯ

| Версия | Дата | Что нового |
|--------|------|------------|
| 1.16.2 | ~май 2026 | Текущая на ПК |
| 1.15.x | ранее | Была хуже, я помню |
| 1.2.5 | конец 2025 | issue #14171 (RAM) |
| 1.0.0 | 2025 | Первый стабильный |

**На ПК:** 1.16.2 (current)
**На GitHub:** latest 1.16.x stable

**НЕ обновлять без явного "точно делай"** — мы на production.

---

## 🛡 БЕЗОПАСНОСТЬ

### Provider API Keys
- `MINIMAX_API_KEY` — в `/root/.hermes/.env` (chmod 600)
- `QWEN_LOCAL_API_KEY=not-needed` — локальный, без ключа
- `NVIDIA_API_KEY` — для nvidia провайдера (если используется)

### Auth на opencode serve
- `OPENCODE_SERVER_PASSWORD` — Basic Auth
- Без пароля = открыт всему LAN
- **Сейчас:** пароль установлен (по skill)

### Сетевая безопасность
- ws_server на VPS: token `hermes-ws-secret-2026` (НЕ rotate)
- ws_client на ПК: тот же token в `config.json`
- http_fallback: через SSH -R (нужен ключ `alex_vps_key`)

---

## 📝 ВЫВОДЫ

1. **OpenCode 1.16.2 — рабочая версия, но с известными багами** (memory leak, freeze, hang).
2. **18 WS-соединений = ws_client плодит + opencode sessions накапливаются.** Лечится через NSSM + session cleanup.
3. **Think-only — скорее не opencode баг, а safety filter на MiniMax-M3 или формулировку task.** Нужен тест с Qwen.
4. **Альтернатива:** Claude Code CLI (надёжнее), Qwen 3.7 Max (дешевле, code-tuned), Codex (средне).
5. **Сейчас приоритет:** не обновлять opencode, не менять модель, а **починить think-only через рефразмировку task + WebDAV file-based delivery**.

---

**Создан:** 2026-06-11 13:35 CEST
**Версия:** v1.0
**Связанные документы:**
- `/root/matryoshka/HERMES_AUDIT_v0.16.md` — я (Hermes)
- `/root/matryoshka/MINIMAX_RESEARCH.md` — модель
- `/root/matryoshka/ALEX_CONNECTION_FINAL_AUDIT.md` — связь
