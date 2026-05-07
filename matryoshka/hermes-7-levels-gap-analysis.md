# HERMES 7 LEVELS — ГЛУБИЙ АНАЛИЗ
## MATRYOSHKA DIGITAL vs. Video David Andre
**Дата:** 07.05.2026  
**Источник:** [7 Levels of Hermes Agent](https://www.youtube.com/watch?v=G47mnkGkYwQ)  
**Аналитик:** Hermes (VPS инстанс)

---

## ОБЩИЙ СТАТУС

| Компонент | Статус MATRYOSHKA | Рекомендация |
|-----------|-------------------|--------------|
| VPS (Hostinger) | ✅ VPS 85.137.166.209 | — |
| Hermes v0.12 | ✅ Установлено | Обновить до latest |
| Telegram подключение | ✅ Работает | Расширить на Discord |
| Curator | ✅ ENABLE | — |
| GitHub Autosync | ❌ Отсутствует | Настроить |
| Kanban | ✅ База есть | Multi-agent pipeline |
| Holographic Memory | ❌ Отсутствует | Установить |
| MCP Server | ❌ Отсутствует | Настроить |

---

## УРОВЕНЬ 1: FUNDAMENTALS (VPS + Hermes Install)

### Что в видео:
- VPS на Hostinger (рекомендовано KVM2, 24 месяца)
- Одна строка установки: `curl -Ls https://... | bash`
- Выбор провайдера: OpenRouter (универсальный доступ)
- API ключ OpenRouter + модель Opus 4.7
- Тест чата — работает

### Что имеет MATRYOSHKA:
```
✅ VPS: 85.137.166.209 (Host-Telecom CZ, Ubuntu 24.04)
✅ Hermes: v0.12.0 (2026.4.30)
✅ Модель: MiniMax-M2.7 (Token Plan Plus) — НЕ OpenRouter
✅ Установка: root level ( НЕ docker)
✅ Gateway: /usr/local/lib/hermes-agent/venv/bin/gateway.run
✅ Dashboard: http://85.137.166.209:9119
```

### РАЗНИЦА:
- Используем **MiniMax-M2.7** вместо OpenRouter + Opus 4.7
- MiniMax — платная модель (Token Plan Plus)
- Видео рекомендует **НЕ ЭКОНОМИТЬ** на моделях

### ВЕРДИКТ: ✅ Полностью рабочий Level 1

---

## УРОВЕНЬ 2: MESSAGING PLATFORM (Discord/Telegram/etc)

### Что в видео:
- Подключение к Discord серверу
- Создание Discord bot через Developer Portal
- Настройка gateway intents (presence, members, message content)
- OAuth2 invite URL для добавления бота на сервер
- Копирование Discord Bot Token в Hermes
- Copy User ID для авторизации
- systemd service для gateway

### Что имеет MATRYOSHKA:
```
✅ Telegram: @oleg_industry_bot (основной)
✅ Telegram: @ZarnyAlexaBot (Эклер для Натальи)
✅ Профили: hermes-cli, ecler
⚠️ Discord: НЕ подключено
⚠️ WhatsApp: НЕ подключено
⚠️ Slack: НЕ подключено
⚠️ Microsoft Teams: НЕ подключено
```

### Команда для подключения:
```bash
hermes gateway setup
# Выбрать номер Discord (или Telegram)
```

### ВЕРДИКТ: ⚠️ Частично — есть Telegram, но нет Discord/multiple platforms

---

## УРОВЕНЬ 3: HERMES CURATOR

### Что в видео:
- Автоматическая очистка unused skills
- Stale after 30 days → marked
- Archive after 90 days → deleted
- Экономит tokens (тысячи $ в месяц для power users)
- `hermes curator status` — проверка

### Что имеет MATRYOSHKA:
```
✅ CURATOR: ENABLED
   runs:           2
   last run:       1d ago
   last summary:   auto: no changes
   interval:       every 7d
   stale after:    30d unused
   archive after:  90d unused

agent-created skills: 23 total
  active     23
  stale      0
  archived   0
```

### ВЕРДИКТ: ✅ Полностью настроен

---

## УРОВЕНЬ 4: CRON JOBS / AUTOMATIONS

### Что в видео:
- `hermes cron` для настройки scheduled tasks
- Автоматический backup в GitHub каждый день
- Примеры: ежедневный backup, еженедельный health check
- Не полагаться на ручное выполнение

### Что имеет MATRYOSHKA:
```
✅ Crontab:
   0 3 * * 0 /root/.hermes/scripts/weekly_cache_clean.sh

❌ GitHub Autosync: НЕ настроен
❌ Scheduled backups: ОТСУТСТВУЮТ
❌ Health check cron: НЕТ
```

### Файлы GitHub которые есть:
```
/root/.hermes/github-credentials
/root/.hermes/github_cred.sh
/root/.hermes/github_sync.py
/root/.hermes/github_token
/root/.hermes/github-token.txt
/root/.hermes/github_token.txt
```
Есть скрипты, но **автозапуск не настроен**.

### ВЕРДИКТ: ❌ Нужна настройка autosync в GitHub

---

## УРОВЕНЬ 5: KANBAN + MULTI-AGENT

### Что в видео:
- Встроенный Kanban board (Hermes v0.12+)
- Визуальный view прогресса тасков
- Multi-agent pipeline: Researcher → Analyst → Writer
- Drag & drop таски между колонками
- Параллельная работа агентов
- Dashboard с сессиями, automations, logs

### Что имеет MATRYOSHKA:
```
✅ Kanban DB: /root/.hermes/kanban.db (существует)
⚠️ Multi-agent pipeline: НЕ настроен
⚠️ Specialist profiles: НЕТ (researcher, writer, reviewer)
⚠️ Parallel agent dispatch: НЕ настроен
```

### Как настроить (из видео):
```bash
# Способ 1: Через чат
/new
"Set up multi-agent kanban workflow with codex so I can build and deploy apps on Vercel by itself"
/remember to use kanban create

# Способ 2: Через terminal
hermes kanban
```

### Пример pipeline из видео:
```
[Researcher] → Что нового по теме на этой неделе? (parallel)
[Researcher] → Что на YouTube о теме за последние 30 дней? (parallel)
[Analyst] → Ждёт обоих → Найти gap/угол
[Writer] → Черновик 3 видео-концептов
```

### ВЕРДИКТ: ⚠️ Kanban есть, но multi-agent pipeline не настроен

---

## УРОВЕНЬ 6: HOLOGRAPHIC MEMORY

### Что в видео:
- `hermes memory setup`
- Holographic — полностью локальный, бесплатный, данные не утекают
- Near-infinite memory
- Автоматическое сохранение важных фактов
- SQLite database path
- Auto extract facts at session end: ENABLE
- Default trust score: 0.4
- Dimensions: по умолчанию

### Преимущества (из видео):
1. **Ошибка новичков:** не говорят "remember this" — всё теряется
2. **Больше контекста ≠ лучше память:** семантический slop
3. **RAG по настроению:** vector similarity не понимает структуру tasks/responsibilities
4. **Embeddings стоят денег + текут данные** (Google Gemini embeddings)
5. **Сжатие со временем стирает факты**

### Что имеет MATRYOSHKA:
```
❌ Holographic memory: НЕ установлено
❌ Факты сохраняются только в chat session
❌ Межсессионная память: ОГРАНИЧЕНА
```

### Как настроить:
```bash
hermes memory setup
# Выбрать: holographic (1)
# SQL database path: default
# Auto extract facts: enable
# Trust score: 0.4
# Dimensions: default

hermes gateway restart
hermes memory check
```

### Нужные команды для активации:
```bash
hermes memory setup
# Пройти wizard
hermes gateway restart
# Потом в чате:
"Read all previous sessions and user.md and memory.md and seed the holographic fact store"
```

### ВЕРДИКТ: ❌ Критически нужно установить

---

## УРОВЕНЬ 7: MCP SERVER

### Что в видео:
- `hermes mcp` для настройки
- Экспозиция Hermes как MCP server
- Подключение Claude Code / Cloud Code к Hermes
- 3 use cases:
  1. **Remote approval gate** — risky operations требуют разрешения на телефоне
  2. **Walk away mode** — запустить refactoring, закрыть laptop, получать progress pings
  3. **Analysis** — Cloud Code использует Hermes tools для анализа пользователя

### Пример (из видео):
```
Cloud Code → Hermes MCP tools:
- mcp_hermes_attachment_fetch
- mcp_hermes_channel_list
- mcp_hermes_conversations_get
- mcp_hermes_messages_read

Результат: "You're a content creator. Vectal. Power users self-host AI infra.
Delegates fully. Low tolerance for verbosity."
```

### Что имеет MATRYOSHKA:
```
❌ MCP servers: НЕ настроены
❌ Hermes → Cloud Code integration: НЕТ
❌ Remote approval gates: НЕТ
```

### Как настроить:
```bash
# В чате Hermes:
/new
"Expose your Hermes to Claude Code via MCP. Cloud can read and send messages 
across your connected messaging platforms, Telegram, Discord, Slack, while 
you code in editor."

# Или через CLI:
hermes mcp setup
```

### ВЕРДИКТ: ❌ Не настроено — большой потенциал для продуктивности

---

## ПРИОРИТЕТЫ РЕАЛИЗАЦИИ

### 🔴 КРИТИЧНО (Влияние на продуктивность):
1. **Holographic Memory** — сейчас Hermes забывает всё между сессиями
2. **GitHub Autosync** — риск потери данных

### 🟡 ВАЖНО (Улучшение workflow):
3. **Multi-agent Kanban pipeline** — параллельная работа агентов
4. **Discord platform** — alternate messaging

### 🟢 ПОЛЕЗНО (Максимизация potential):
5. **MCP Server** — интеграция с Claude Code
6. **Update Hermes** — 613 commits behind

---

## НУЖНЫЕ ДЕЙСТВИЯ (ONE COMMAND = ONE RESULT)

### 1. Holographic Memory (КРИТИЧНО):
```bash
hermes memory setup
# Interactive wizard
```

### 2. GitHub Autosync:
```bash
hermes github-autosync enable
# Или через уже существующий скрипт
```

### 3. Multi-agent Pipeline:
```bash
/new
"Set up kanban with default researcher, writer, reviewer profiles"
```

### 4. Discord (если нужно):
```bash
hermes gateway setup
# Выбрать Discord
```

### 5. Hermes Update:
```bash
hermes update
```

### 6. MCP Server:
```bash
hermes mcp setup
# Выбрать Claude Code / Cloud Code
```

---

## СРАВНИТЕЛЬНАЯ ТАБЛИЦА

| Level | Video (David Andre) | MATRYOSHKA | Gap |
|-------|---------------------|------------|-----|
| 1. VPS + Hermes | ✅ Hostinger + OpenRouter | ✅ VPS + MiniMax | Модель |
| 2. Messaging | Discord integration | Telegram | Platform |
| 3. Curator | ✅ Enabled | ✅ Enabled | — |
| 4. Cron/Auto-Backup | GitHub autosync daily | Cache clean only | Backup |
| 5. Kanban | Multi-agent pipeline | Kanban DB only | Pipeline |
| 6. Holographic Memory | ✅ Setup | ❌ Missing | Memory |
| 7. MCP Server | ✅ Exposed | ❌ Missing | Integration |

---

## ВЫВОД

**MATRYOSHKA DIGITAL** имеет рабочую базу Hermes (Level 1-3), но отстаёт от потенциала видео на **4 критических уровнях**:

1. ❌ **Memory** — Hermes забывает всё между сессиями
2. ❌ **Backup** — нет автоматического GitHub sync
3. ⚠️ **Pipeline** — Kanban есть, но multi-agent не настроен
4. ❌ **MCP** — нет интеграции с Claude Code

**Рекомендация:** Начать с Level 6 (Holographic Memory) — это даст наибольший эффект продуктивности немедленно.

---

*Документ создан Hermes (VPS) 07.05.2026 на основе транскрипции видео David Andre "7 Levels of Hermes Agent"*
