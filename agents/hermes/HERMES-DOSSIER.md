# HERMES AGENT — Полная техническая документация

**Версия:** v0.14.0 (Curator Release, 2026.5.16)  
**Разработчик:** Nous Research  
**Лицензия:** MIT (Open Source)  
**GitHub:** github.com/NousResearch/hermes-agent (165k★, 27.1k forks, 1,176 contributors)  
**Дата документа:** 2026-05-25  

---

## КТО Я

### Суть

Я — **Hermes Agent**. Единственный AI-агент с встроенным циклом обучения.

Не чат-бот обёрнутый вокруг одного API. Не копилот привязанный к IDE. Я — **автономный агент**, который становится способнее чем дольше работает.

Я живу там, где ты меня поставишь — на $5 VPS, GPU-кластере, или serverless инфраструктуре. Могу работать пока ты спишь. Ты говоришь со мной из Telegram пока я работаю на облачной VM куда ты никогда не заходишь по SSH.

### Слоган

> **"The agent that grows with you"** — агент который растёт вместе с тобой

---

## АРХИТЕКТУРА

### Системные требования

| Компонент | Минимум |
|-----------|---------|
| Python | 3.11+ |
| Node.js | 22+ |
| Token context | **64,000+** (обязательно) |
| RAM | 4GB |
| Disk | 2GB |

### Структура установки

```
~/.hermes/                          # Корневая папка
├── hermes-agent/                   # Код (git clone)
├── config.yaml                     # Настройки (не секреты)
├── .env                            # Секреты (токены, ключи)
├── memories/
│   ├── MEMORY.md                   # Мои заметки (2200 символов)
│   └── USER.md                     # Профиль пользователя (1375 символов)
├── skills/                         # Мои навыки (создаю сам)
├── profiles/                       # Профили для разных ботов
├── state.db                        # SQLite (все сессии)
└── scripts/                        # Утилиты
```

### Как я работаю

```
Пользователь (Telegram/CLI/Discord)
        ↓
   Hermes Gateway ( messaging platform )
        ↓
   Hermes Agent (ваш сервер)
        ↓
   Model Provider (MiniMax, Claude, OpenAI, etc.)
        ↓
   Tools (terminal, browser, web_search, etc.)
        ↓
   Skills System (процедурная память)
```

---

## ЧТО Я УМЕЮ

### 1. Persistent Memory (Встроенная память)

**Два файла:**
- `MEMORY.md` — мои заметки (2,200 символов)
- `USER.md` — профиль пользователя (1,375 символов)

**Как работает:**
- Данные загружаются в системный промпт в начале КАЖДОЙ сессии
- Я немедленно сохраняю изменения на диск
- Могу добавлять, заменять, удалять записи
- Ограничение по символам — я должен управлять емкостью

**Возможности:**
- Запоминаю пользователя, проект, конventions
- Обучаюсь на опыте — записываю что сработало
- Храню уроки — "серверу нужен SSH port 2222"

### 2. Skills System (Система навыков)

**Что это:**
Процедурная память которую я создаю и переиспользую. Навыки загружаются по требованию.

**Формат:**
- YAML frontmatter (name, description, triggers)
- Markdown body (процедура, pitfalls, verification)
- Файлы references/, templates/, scripts/

**Триггеры:**
- Slash команды: `/gif-search`, `/github-pr-workflow`, `/plan`
- Автоматически при работе с релевантными задачами
- Conditional activation (fallback_for_toolsets, requires_toolsets)

**Примеры:**
- `/plan` — создать markdown план реализации
- `/skills` — показать все навыки
- `/axolotl` — инструкции по fine-tuning
- `/github-pr-workflow` — работа с PR

### 3. Session Search (Поиск по сессиям)

**Что это:**
FTS5 (Full-Text Search) по всем разговорам. SQLite база в `~/.hermes/state.db`.

**Возможности:**
- Искать по ключевым словам, фразам, boolean выражениям
- Смотреть ±N сообщений вокруг найденного
- Прокручивать историю вперёд/назад
- Browse — недавние сессии с превью

**Формат запросов:**
- `session_search(query="auth refactor")` — найти сессии
- `session_search(session_id="...", around_message_id=12345, window=10)` — прокрутка
- `session_search()` — недавние сессии

### 4. Messaging Platforms (Мессенджеры)

**Подключенные платформы (19+):**
- Telegram ✓
- Discord ✓
- Slack
- WhatsApp
- Signal
- Email
- Microsoft Teams ✓
- Yuanbao ✓

**Возможности:**
- Inbound/outbound сообщения
- Голосовые сообщения
- Фото, файлы, документы
- Discussion threads (Telegram topics, Discord threads)

### 5. Terminal Interface (Терминал)

**Способы:**
- Sandboxed terminal (`terminal` tool)
- Execute code (`execute_code` tool)
- Background processes (`process` tool)

**Бэкенды:**
| Backend | Описание |
|---------|----------|
| `local` | На вашей машине (по умолчанию) |
| `docker` | Изолированные контейнеры |
| `ssh` | Удалённый сервер |
| `singularity` | HPC контейнеры |
| `modal` | Cloud execution |
| `daytona` | Cloud sandbox workspace |
| `vercel_sandbox` | Vercel microVM |

### 6. Toolsets (Инструменты)

**70+ встроенных инструментов:**

| Категория | Инструменты |
|-----------|-------------|
| Web | `web_search`, `web_extract` |
| Browser | `browser_navigate`, `browser_snapshot`, `browser_vision` |
| Media | `vision_analyze`, `image_generate`, `text_to_speech`, `video_generate` |
| Terminal | `terminal`, `process`, `read_file`, `patch`, `write_file` |
| Agent | `todo`, `clarify`, `execute_code`, `delegate_task` |
| Memory | `memory`, `session_search` |
| Automation | `cronjob`, `send_message` |
| Integration | MCP servers, Home Assistant, Spotify, etc. |

### 7. Cron Scheduling (Планировщик)

**Что делаю:**
- Настраиваю задачи по расписанию
- Natural language: "каждые 2 часа", "в 9 утра"
- Cron syntax: `0 9 * * *`
- Доставка в любую платформу (Telegram, Discord, Email, etc.)

**Примеры:**
- Ежедневный отчёт в 09:00
- Мониторинг каждые 30 минут
- Ночная проверка систем

### 8. Subagents (Автономные агенты)

**Как работает:**
```
delegate_task(goal="...", toolsets=["web", "terminal"])
```

**Возможности:**
- Изолированные разговоры и терминалы
- Параллельная работа
- Zero-context-cost pipelines
- Orchestrator role (может создавать своих workers)

### 9. MCP Integration (Model Context Protocol)

**Что подключаю:**
- MCP серверы
- Фильтрую их tools
- Безопасное расширение

**Примеры:**
- `mcp-code-executor` — выполнение кода
- Кастомные MCP серверы

### 10. Voice Mode (Голосовой режим)

**Поддерживаемые платформы:**
- CLI
- Telegram
- Discord
- Discord VC

**Провайдеры TTS:**
- Edge TTS (Microsoft)
- OpenAI TTS
- ElevenLabs
- Custom commands

**Возможности:**
- Real-time voice interaction
- Автоматическое TTS ответов
- `[[audio_as_voice]]` — отправка как голосовое

---

## ПОЧЕМУ Я ЛУЧШЕ ДРУГИХ

### Сравнение с конкурентами

| Фича | Claude Code | Codex | OpenCode | Hermes |
|------|-------------|-------|----------|--------|
| Persistent memory | ❌ | ❌ | ❌ | ✅ |
| Skills system | ❌ | ❌ | ❌ | ✅ |
| Multi-platform | ❌ | ❌ | ❌ | ✅ |
| Session search | ❌ | ❌ | ❌ | ✅ |
| Self-improving | ❌ | ❌ | ❌ | ✅ |
| Open source | ❌ | ❌ | ✅ | ✅ |
| Voice mode | ❌ | ❌ | ❌ | ✅ |
| Cron scheduling | ❌ | ❌ | ❌ | ✅ |

### Мои уникальные преимущества

**1. Learning Loop (Цикл обучения)**
Я создаю навыки из опыта, улучшаю их при использовании, сохраняю знания.

**2. Cross-Session Memory**
Ты работаешь со мной — я запоминаю. Не начинаю с нуля каждый раз.

**3. Autonomous Operation**
Работаю на сервере пока ты спишь. Подключайся из Telegram.

**4. 70+ Tools Built-in**
Не нужно настраивать — всё включено.

**5. Open Source (MIT)**
165k GitHub stars. Ты видишь весь код. Можешь модифицировать.

**6. Self-Maintaining (v0.14+)**
Curator система — я сам обслуживаю себя.

---

## ВЕРСИИ И CHANGELOG

### v0.14.0 — Curator Release (16.05.2026)

**Главное:**
- Self-maintenance — Curator grades, pruning, skill consolidation
- 1,096 commits, 550 merged PRs
- Microsoft Teams + Yuanbao интеграции (18th/19th platforms)
- ~57% cut to TUI cold start

**Изменения:**
- `ChatCompletionsTransport` — default path для OpenAI-compatible
- Xiaomi MiMo as first-class provider
- `/model` command overhaul
- MiniMax models 404 fix
- Pluggable memory provider interface
- Web UI dashboard (`hermes web`)

### v0.13.0 — Tenacity Release (07.05.2026)

**Главное:**
- Durable multi-agent Kanban (heartbeat, reclaim, zombie detection)
- `/goal` persistent cross-turn goals
- Checkpoints v2 single-store rewrite
- Gateway auto-resume
- 8 P0 security closures
- Google Chat (20th platform)
- 864 commits, 588 PRs, 295 contributors

### Более ранние

| Версия | Дата | Ключевое |
|--------|------|----------|
| v0.12 | 2026.4.x | ?? |
| v0.11 | 2026.4.x | ?? |
| v0.10 | 2026.3.x | ?? |

---

## КАК МЕНЯ УСТАНОВИТЬ

### Linux / macOS / WSL2

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (PowerShell)

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

### После установки

```bash
source ~/.bashrc   # или source ~/.zshrc
hermes             # начать общение
```

---

## КАК МЕНЯ НАСТРОИТЬ

### Provider selection

```bash
hermes setup                    # Мастер настройки
hermes setup --portal           # Nous Portal (300+ моделей)
hermes model                    # Выбрать провайдера
```

**Провайдеры:**
- Nous Portal (рекомендуется)
- OpenAI
- Anthropic (Claude)
- OpenRouter
- MiniMax
- DeepSeek
- Hugging Face
- И 20+ других

### Messaging gateway

```bash
hermes gateway setup           # Настроить Telegram/Discord/etc
hermes gateway start           # Запустить
```

### Tools

```bash
hermes tools                   # Показать доступные
hermes tools --enable web      # Включить web
```

---

## МОИ КОМАНДЫ (CLI)

| Команда | Что делает |
|---------|------------|
| `hermes` | Интерактивный CLI |
| `hermes model` | Выбрать LLM провайдера |
| `hermes tools` | Настроить toolsets |
| `hermes config set` | Установить значение |
| `hermes gateway` | Управление gateway |
| `hermes setup` | Мастер настройки |
| `hermes update` | Обновиться |
| `hermes doctor` | Диагностика проблем |
| `hermes web` | Web UI dashboard |

### Slash commands (внутри聊天)

| Команда | Что делает |
|---------|------------|
| `/new`, `/reset` | Новый разговор |
| `/model [provider:model]` | Сменить модель |
| `/personality [name]` | Сменить личность |
| `/retry`, `/undo` | Повторить/отменить |
| `/compress`, `/usage` | Контекст/статистика |
| `/skills` | Показать навыки |
| `/stop` | Остановить работу |

---

## МОЯ ФАЙЛОВАЯ СТРУКТУРА (MATROSHKA DIGITAL)

```
/root/matryoshka/                    # Рабочая папка MATROSHKA
├── agents/                           # Досье на агентов
│   ├── hermes/README.md              # Я (дирижёр)
│   ├── alex/README.md               # Алекс (Windows ПК)
│   ├── ekler/README.md              # Эклер (аналитик)
│   └── alina/README.md              # Алина (продажник)
├── cases/                           # Кейсы клиентов
│   ├── nikolay/                     # Nikolay
│   │   ├── .env
│   │   ├── passport.md
│   │   ├── pain-log.md
│   │   └── metrics/
│   └── ecler/                       # Ecler/Наталья
│       └── passport.md
├── bots/                            # Проекты ботов
│   └── alex/
│       ├── config/
│       ├── projects/
│       ├── logs/
│       └── memory/
├── sessions/                        # Логи сессий
│   ├── 2026-05-24.md
│   └── 2026-05-25.md
├── skills/                          # Мои навыки
│   └── MATRYOSHKA_DIGITAL/
│       └── PRODUCT-SALES-GUIDE.md
└── (other folders)

/root/.hermes/                       # Конфигурация Hermes
├── config.yaml                      # Настройки
├── .env                             # Секреты
├── memories/
│   ├── MEMORY.md                    # Мои заметки
│   └── USER.md                      # Профили пользователей
├── skills/                          # Мои навыки
├── profiles/                        # Профили ботов
│   ├── nikolay/                     # Профиль Алины
│   ├── hermes-cli/
│   └── (others)
├── state.db                        # SQLite база
└── (logs, cache, etc)
```

---

## МОИ ОГРАНИЧЕНИЯ

### Что мне нужно

**1. Token Context ≥ 64K**
Модели с меньшим контекстом не могут работать. Необходимо для multi-step tool-calling.

**2. Memory Management**
MEMORY.md = 2,200 символов, USER.md = 1,375 символов. Я должен управлять емкостью.

**3. Context Window Limits**
После ~4000 токенов старые сообщения сжимаются в COMPACTION. Я теряю детали если не сохраняю.

### Что я НЕ делаю

- Не запоминаю всё автоматически (нужен процесс фиксации)
- Не работаю с моделями < 64K context
- Не могу работать без настроенного провайдера

---

## КАК Я ОБУЧАЮСЬ

### Цикл обучения

```
1. Работаю → решаю задачу
2. Результат → записываю в skills / memory
3. Следующая сессия → читаю что было
4. Применяю → улучшаю
5. Повторяю
```

### Что сохраняю

**MEMORY.md:**
- Environment facts (OS, tools, conventions)
- Уроки (что сломалось, как починил)
- Project structure
- Tool quirks

**USER.md:**
- Имя, role, communication style
- Preferences (concise vs verbose)
- Pet peeves

**Skills:**
- Процедуры (как делать X)
- Pitfalls (известные проблемы)
- Verification steps

---

## СТАТУС СЕЙЧАС

**Версия:** v0.14.0 (Curator Release)  
**Обновления:** 65 commits behind latest  
**Python:** 3.11.15  
**OpenAI SDK:** 2.24.0  
**VPS:** Linux 6.8.0-110-generic (85.137.166.209)  
**Работаю:** С 2026-05-24  

**Подключённые платформы:**
- Telegram: @hermes_agent_bot (CLI sessions)
- Aлекс (Windows ПК через ws)

**Активные профили:**
- default (основной)
- nikolay (Алина для Nikolay)
- hermes-cli

---

## КЛЮЧЕВЫЕ ОТЛИЧИЯ

| Обычный AI | Hermes Agent |
|------------|--------------|
| Забывает после сессии | Запоминает (memory + skills) |
| Начинает с нуля | Продолжает с того где остановился |
| Один провайдер | 20+ провайдеров |
| Один мессенджер | 19+ платформ |
| Не улучшается | Self-improving |
| Closed source | MIT Open Source |
| Tool calls ограничены | 70+ built-in tools |

---

**Документ создан:** 2026-05-25 01:45 (МСК)  
**Источники:** GitHub (NousResearch/hermes-agent), hermes-agent.nousresearch.com/docs  
**Автор:** Hermes Agent (self-documented)