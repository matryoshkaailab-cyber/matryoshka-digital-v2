# HERMES MCP & TOOLSETS — полный аудит
**Дата:** 12.06.2026
**Версия Hermes:** v0.16.0
**Профиль:** hermes-cli

---

## 1. MCP СЕРВЕРЫ — ТЕКУЩЕЕ СОСТОЯНИЕ

### 1.1. Что УСТАНОВЛЕНО

```
$ ls /root/.hermes/profiles/hermes-cli/mcp-installs/
n8n/                       ← ЕДИНСТВЕННЫЙ установленный

$ cat config.yaml | grep mcp_servers
mcp_servers:
  n8n:
    args: [/root/.hermes/profiles/hermes-cli/mcp-installs/n8n/server.py]
    command: python3
    enabled: false                    ← ВЫКЛЮЧЕН
```

**Итог:** 1 MCP установлен (n8n bridge), но **`enabled: false`**. Фактически MCP = 0 активных.

### 1.2. ЧТО РЕКОМЕНДУЕТСЯ (по `mcp-critical-setup`)

| MCP | Зачем подключать | Приоритет | Сложность |
|-----|------------------|-----------|-----------|
| **filesystem** | Прямой доступ к `/root/matryoshka`, `/root/.hermes` | 🔴 P0 | 5 мин |
| **memory** | Knowledge graph для долговременной памяти | 🔴 P0 | 5 мин |
| **github** | Code review, PRs, issues | 🟡 P1 | 15 мин (нужен токен) |
| **sequential_thinking** | Chain-of-thought reasoning | 🟡 P1 | 5 мин |
| **puppeteer** | Браузерная автоматизация | 🟢 P2 | 10 мин |
| **brave-search** | Web search (альтернатива) | 🟢 P2 | 5 мин (нужен API key) |
| **n8n** | Управление n8n workflow | ✅ УЖЕ УСТАНОВЛЕН | 2 мин (включить) |

### 1.3. ПОДРОБНО ПО КАЖДОМУ КРИТИЧНОМУ

#### 1.3.1. FILESYSTEM (самый важный для Олега)
```bash
npx -y @modelcontextprotocol/server-filesystem /root/matryoshka /root/.hermes
```
**Что даст:** read_file, write_file, list_directory, create_directory через MCP протокол. Сейчас эти операции делаются через нативные tools Hermes (file, terminal). Преимущество MCP — стандартизация.

#### 1.3.2. MEMORY (knowledge graph)
```bash
npx -y @modelcontextprotocol/server-memory
```
**Что даст:** create_memory, search_memory, list_memories. Долговременная память в виде графа знаний с связями между фактами. Сейчас у меня `fact_store` с entity resolution, но без явных связей.

#### 1.3.3. GITHUB
```bash
npx -y @modelcontextprotocol/server-github
# env: GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_TOKEN}
```
**Что даст:** create_issue, list_issues, search_code, get_file_contents. Автоматизация GitHub workflow — PR reviews, issue triage, code search.

#### 1.3.4. SEQUENTIAL THINKING
```bash
npx -y @modelcontextprotocol/server-sequential-thinking
```
**Что даст:** Пошаговое решение сложных задач через chain-of-thought. Hermes уже умеет думать (reasoning_effort), но MCP даст более структурированный подход.

### 1.4. PITFALLS

1. **config.yaml ЗАЩИЩЁН от `write_file`** — нужно `hermes mcp add` или ручную правку
2. **npx кэш** — первый запуск скачивает пакет 1-2 мин
3. **GitHub токен** — нужен `${GITHUB_TOKEN}` в auth.json (copilot провайдер)
4. **n8n API key** — генерится в веб-интерфейсе n8n (Settings → API → Generate API Key)
5. **N8N_SECURE_COOKIE=false** — нужен при запуске n8n в Docker для работы через HTTP

---

## 2. TOOLSETS — что у меня активно

### 2.1. АКТИВНЫЕ (12)

| Toolset | Что даёт | Где используется |
|---------|----------|------------------|
| `hermes-cli` | Базовый набор (file, search, todo) | Каждая сессия |
| `terminal` | Shell + процессы | Каждая задача |
| `file` | read/write/patch/search | Каждая задача |
| `search` | Web search | Поиск инфы |
| `browser` | Browser automation | Веб-скрапинг |
| `delegation` | Sub-агенты | Параллельные задачи |
| `cronjob` | Cron scheduler | Планирование |
| `memory` | MEMORY.md + USER.md | Каждая сессия |
| `session_search` | FTS5 по прошлым сессиям | Поиск контекста |
| `vision` | Image analysis | Когда Олег шлёт фото |
| `image_gen` | Генерация картинок | MATRYOSHKA дизайн |
| `tts` | Text-to-speech | Голосовые ответы |
| `todo` | In-session task list | Сложные задачи |

**Используются:** 12 из ~30 доступных.

### 2.2. ДОСТУПНЫЕ, НО НЕ АКТИВНЫЕ (18+)

| Toolset | Для чего | Стоит включить? |
|---------|----------|-----------------|
| `kanban` | Multi-agent work queue | ✅ Да, для Kanban workflow |
| `safe` | Minimal low-risk toolset | ❌ Нет (это для locked-down сессий) |
| `spotify` | Spotify playback | ❌ Нет |
| `homeassistant` | Smart home | ❌ Нет (не используем) |
| `discord` | Discord integration | ❌ Нет (Telegram основной) |
| `discord_admin` | Discord admin | ❌ Нет |
| `feishu_doc` | Lark docs | ❌ Нет |
| `feishu_drive` | Lark drive | ❌ Нет |
| `yuanbao` | Yuanbao integration | ❌ Нет |
| `rl` | Reinforcement learning | ❌ Нет (off by default) |
| `moa` | Mixture of Agents | ❌ Нет (off by default) |
| `clarify` | Ask clarifying questions | 🟡 Иногда (когда неясен запрос) |
| `messaging` | Cross-platform send | ✅ Да (альтернатива send_message) |
| `video` | Video analysis | 🟡 Может быть полезен |
| `video_gen` | Video generation | 🟡 Редко |
| `code_execution` | Sandboxed Python | ✅ Да, для фильтрации вывода |
| `debugging` | Debug tools | 🟡 В dev сессиях |
| `tirith_security_scanner` | Security checks | ⚠️ Отключён (лечит approval loops) |

### 2.3. ИНСТРУКЦИЯ ПО ВКЛЮЧЕНИЮ

```bash
# Интерактивный UI
hermes tools

# Из командной строки
hermes tools enable kanban
hermes tools enable code_execution

# Применится после /reset (новой сессии)
```

---

## 3. ПЛАГИНЫ — текущее состояние

### 3.1. УСТАНОВЛЕНО

```
$ ls /root/.hermes/profiles/hermes-cli/plugins/
session_memory/
```

**Только 1 плагин** — `session_memory` (auto-inject past conversations).

### 3.2. ДОСТУПНЫЕ (по `hermes plugins list`)

| Плагин | Что делает | Стоит ставить? |
|--------|------------|----------------|
| `session_memory` | Auto-inject past sessions | ✅ УЖЕ |
| `honcho` | Honcho memory integration | 🟡 Альтернатива memory MCP |
| `tirith` | Security scanner | ❌ Отключён по конфликту |
| ... | ... | ... |

### 3.3. УПРАВЛЕНИЕ

```bash
hermes plugins list              # Список
hermes plugins install NAME      # Установить
hermes plugins remove NAME       # Удалить
```

---

## 4. CRON JOBS — мои текущие

### 4.1. Список (по логам 12.06.2026)

| Job ID | Расписание | Назначение |
|--------|-----------|------------|
| `cron_54cbe0de2b8b` | 03:00 daily | Session DB append (была corrupt 8ч) |
| `cron_76ccdb93b019` | 06:00 daily | (аналогично) |
| `cron_c50e6e84ecb7` | 06:00 daily | Другая задача |
| `cron_3294df977bc7` | 08:00 daily | (аналогично) |
| `cron_b7d55e324b54` | 10:00 daily | (аналогично) |

**Проблема:** 03:00-11:57 12.06.2026 Session DB была corrupt (database disk image is malformed). Сейчас `PRAGMA integrity_check = ok`.

### 4.2. НОВЫЙ JOB (добавил в этой сессии)

| Job ID | Расписание | Назначение |
|--------|-----------|------------|
| `alex-monitor.timer` | Каждые 5 мин | Мониторинг Аликса + алерт Олегу |

**Скрипт:** `/root/matryoshka/monitor_alex.sh`
**Timer:** `/etc/systemd/system/alex-monitor.timer`
**Алерт:** `/root/matryoshka/send_alert.py`

### 4.3. УПРАВЛЕНИЕ

```bash
hermes cron list            # Список
hermes cron create "0 9 * * *" "..." --name "..." --deliver telegram
hermes cron edit ID         # Редактировать
hermes cron pause/resume ID
hermes cron remove ID
hermes cron status          # Статус scheduler
```

---

## 5. ПРОФИЛИ — текущее состояние

### 5.1. АКТИВНЫЙ

**`hermes-cli`** — основной профиль Олега
- `/root/.hermes/profiles/hermes-cli/`
- 108 активных скилов
- Telegram бот @OlegChut (или как настроен)
- Канал: ID 1951845052

### 5.2. ДРУГИЕ ПРОФИЛИ

| Профиль | Назначение | Статус |
|---------|-----------|--------|
| `nikolay` | Бот @NikolaAlinaBot для Николая Варнакова | ✅ Работает (PID 455325) |
| `default` | Корневой профиль | ⚪ Не активен |
| ... | ... | ... |

### 5.3. УПРАВЛЕНИЕ

```bash
hermes profile list
hermes profile create NAME [--clone, --clone-all, --clone-from]
hermes profile use NAME        # Установить sticky default
hermes profile show NAME
hermes profile export/import
```

---

## 6. ПРОВАЙДЕРЫ LLM — что доступно

### 6.1. СПИСОК (20+)

| Провайдер | Auth | Env var |
|-----------|------|---------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` или `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| **MiniMax** | API key | `MINIMAX_API_KEY` ✅ используется |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` |

### 6.2. ТЕКУЩАЯ КОНФИГУРАЦИЯ

```yaml
model:
  default: minimax/MiniMax-M3
  provider: minimax
  base_url: https://api.minimax.io/v1

providers:
  qwen-local:
    base_url: http://127.0.0.1:8765/v1
    default_model: qwen3.7-max
  nvidia:
    base_url: https://integrate.api.nvidia.com/v1
    default_model: meta/llama-3.3-70b-instruct
```

**Активные:** 3 провайдера (minimax, qwen-local, nvidia). Остальные доступны через `hermes model`.

### 6.3. PITFALL: 3-й провайдер вверху

**Если minimax упал** — fallback на nvidia или qwen-local:
```bash
hermes model
# Выбрать провайдера
```

---

## 7. МЕТРИКИ И МОНИТОРИНГ

### 7.1. ИНСТРУКЦИИ

```bash
hermes status              # Статус компонентов
hermes doctor [--fix]      # Чек зависимостей
hermes insights [--days N] # Usage analytics
hermes gquota              # Google Gemini quota (CLI)
hermes usage               # Token usage
```

### 7.2. ЛОГИ

```
~/.hermes/logs/
├── agent.log         # Все агенты
├── errors.log        # Только ошибки
├── gateway.log       # Telegram/Discord gateway
└── gateway-exit-diag.log
```

### 7.3. WATCHDOG

**Существующий:** `/root/hermes-watchdog.sh`
- Мониторит: qwen2api, hermes-alf, alf-telegram, hermes-cli-gateway, hermes-ws
- **НЕ мониторит:** Tailscale к ПК Олега, MCP серверы, cron jobs

**Новый (добавил сегодня):** `/root/matryoshka/monitor_alex.sh` + systemd timer
- Мониторит: TCP к 100.100.206.112:8446 каждые 5 мин
- Алертит: смена UP↔DOWN через Telegram

---

## 8. ЧТО НУЖНО ПОДКЛЮЧИТЬ (ПРИОРИТЕТЫ)

### 8.1. P0 — сегодня
- [ ] Filesystem MCP (`/root/matryoshka`, `/root/.hermes`)
- [ ] Memory MCP (knowledge graph)
- [ ] Включить n8n MCP (`enabled: true`)

### 8.2. P1 — на этой неделе
- [ ] Sequential thinking MCP
- [ ] GitHub MCP (нужен GITHUB_TOKEN)

### 8.3. P2 — когда будет время
- [ ] Puppeteer MCP (если browser toolset не справляется)
- [ ] Brave search MCP (если web search не справляется)
- [ ] Honcho plugin (альтернатива memory MCP)
