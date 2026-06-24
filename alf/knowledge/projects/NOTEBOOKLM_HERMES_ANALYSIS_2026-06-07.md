# 🧠 NotebookLM + Hermes Agent — Глубокий анализ (4 YouTube-видео)

**Автор анализа:** ALEX (MATRYOSHKA DIGITAL)
**Дата:** 2026-06-07
**Источники:** 4 видео (Julian Goldie SEO ×3, Jack Roberts ×1)
**Транскрипты:** `C:\Users\User\AppData\Local\Temp\opencode\yt_transcripts\`
**Чанки:** `C:\Users\User\AppData\Local\Temp\opencode\yt_chunks\`

---

## ⚡ TL;DR

Все 4 видео — про **одну и ту же экосистему**: open-source AI-агент **Hermes** (от Nous Research, февраль 2025) + **Google NotebookLM** + **MCP-мост** + **Obsidian** (память) + **Hyperframes** (видео) + **N8N** (workflows) + **Pantheon dashboard** (UI). Это уже реализованная и продаваемая "контент-фабрика" за $0.

**Для MATRYOSHKA DIGITAL это прямое попадание:**
- У нас уже есть Obsidian vault (✅ совпадает)
- У нас уже есть N8N (✅ совпадает)
- У нас уже есть HERMES (но наш — дирижёр оркестра, не личный агент)
- У нас уже есть идея VNC-доступа к NotebookLM через x11vnc:6080 (✅ совпадает!)
- **Не хватает:** самого MCP-моста к NotebookLM, Hyperframes, Pantheon-дашборда

**Главный инсайт:** NotebookLM — это бесплатный RAG с безлимитным контекстом (300+ источников на notebook), который **сам** делает 12 типов контента (podcast, video, slides, mind map, infographic, FAQ, report...). Подключив его к HERMES, мы получаем контент-завод за $0.

---

## 1. Видео — обзор

| # | ID | Название | Автор | Хрон | Главный тезис |
|---|---|---|---|---|---|
| 1 | `AW600A-P8FU` | NEW NotebookLM AI Agent is INSANE! | Julian Goldie SEO | 9:09 | NotebookLM → AI Agent → 12 типов контента одной кнопкой |
| 2 | `Qk04WppgXrM` | Hermes + NotebookLM is INSANE! | Julian Goldie SEO | 8:26 | Hermes соединяет NotebookLM с редактированием видео и памятью |
| 3 | `yae5gYVzAxM` | NotebookLM + Hermes Just Changed Everything! | Julian Goldie SEO | 7:48 | SEO-конвейер: research → контент → трафик Google |
| 4 | `9rXH2ssCe9E` | Hermes Agent has a NEW SuperPower (NotebookLM) | Jack Roberts | 16:27 | **Пошаговая установка** MCP-моста + интеграция N8N MCP |

**3 из 4 видео — продажа AI Profit Boardroom / Alpha Podium** (Julian Goldie, ~3000–2800 участников). **Jack Roberts** — единственный, кто показывает **технический how-to** (MCP, N8N, terminal, bash-команды).

---

## 2. Ключевые концепции (глоссарий)

### 2.1. NotebookLM
- **Что:** бесплатный AI-инструмент от Google.
- **Что делает:** из источников (URL, PDF, видео, текст) — до **300+ на notebook** — генерирует 12 типов артефактов:
  1. Audio Overview (подкаст двух AI-ведущих)
  2. Video Overview
  3. Slide Deck
  4. Mind Map
  5. Infographic
  6. Flashcards
  7. Quiz
  8. Briefing Doc
  9. Study Guide
  10. FAQ
  11. Full Report
  12. Chat (Q&A по источникам)
- **Цитата (Julian Goldie, видео 1):** *"from one notebook, it can make... 12 different types of content all from the same sources for free."*
- **Ограничение:** не имеет памяти, не знает пользователя, не умеет организовывать, не интегрирован ни с чем.

### 2.2. Hermes Agent
- **Что:** **open-source personal AI agent** от **Nous Research** (в видео назван "News Research" — оговорился спикер). Запущен публично в феврале 2025.
- **Где живёт:** на локальной машине / VPS, общается через Telegram + Claude Code.
- **Что умеет:** MCP-мост к любым инструментам, выполняет команды в терминале, строит дашборды, держит память.
- **Сравнение с нашим HERMES:** у нас **HERMES = дирижёр оркестра** (VPS, MiniMax-M2.7, WS:8446). В видео **Hermes = персональный агент-исполнитель**. Это **другая сущность** того же имени — не путать.

### 2.3. MCP (Model Context Protocol)
- **Что:** "мостик" / коннектор между AI-агентом и внешним сервисом.
- **NotebookLM MCP** — **неофициальный** (от Google официального нет), требует cookie-based auth через браузер.
- **Цитата (Julian Goldie, видео 3):** *"An MCP is just a little bridge, a connector. It lets your agent talk to NotebookLM directly."*
- **Установка (Jack Roberts, видео 4):** скачать skill-файл → загрузить в Claude Code → попросить "install the NotebookLM skill" → залогиниться в браузере → cookie цепляется → MCP активен.

### 2.4. Obsidian (Memory Vault)
- **Что:** бесплатный markdown-редактор с локальной базой знаний.
- **Зачем в системе:** "вторая память" — все агенты читают Obsidian → знают пользователя, бренд, историю.
- **Цитата (Julian Goldie, видео 2):** *"AI agents understand you, they get better every time they use it, and everything is connected together."*

### 2.5. Hyperframes
- **Что:** open-source skill для **создания и редактирования видео**.
- **Где:** GitHub (https://github.com/...).
- **Что делает:** добавление аватара, монтаж, генерация видео из текста.
- **Цитата (Jack Roberts, видео 4):** *"your agent can actually create and edit videos for you. You can even add an avatar."*

### 2.6. N8N MCP
- **Что:** N8N выпустил MCP-сервер, через который Hermes может **создавать/читать/запускать workflow**.
- **Зачем:** cron-контент, email-рассылки, клиентские автоматизации.
- **Пример (Jack Roberts, видео 4):** голосовое сообщение в Telegram → "создай workflow: каждое утро 8:00 — бери инсайт из NotebookLM YouTube Strategy, отправляй мне на email".

### 2.7. Pantheon Dashboard
- **Что:** UI-обёртка Hermes, где можно визуально создавать **personas/skills** (каждый skill = один промпт + модель).
- **Зачем:** управление skills без кода, визуальный обзор.

### 2.8. Alpha API (Julian Goldie)
- **Бесплатный API** для запуска моделей в Hermes (по сути — роутер между Hermes и LLM-провайдерами).
- **Альтернативы:** OpenRouter (у нас уже есть ключ `sk-or-v1-...`), OpenCode Zen, DeepSeek, NVIDIA, Cloudflare.

---

## 3. Архитектура "Agent OS" (3 слоя)

```
┌────────────────────────────────────────────────────────────┐
│  LAYER 3: THE LOOP (бесконечный цикл)                      │
│  Новый источник → новый контент → в память → ...           │
├────────────────────────────────────────────────────────────┤
│  LAYER 2: AGENT (Hermes / Claude Code)                     │
│  MCP-мосты к NotebookLM, N8N, Hyperframes, Alpha API       │
│  Pantheon UI → визуальное управление skills                │
├────────────────────────────────────────────────────────────┤
│  LAYER 1: KNOWLEDGE VAULT (NotebookLM + Obsidian)          │
│  300+ источников/ноутбук → 12 типов контента               │
│  + Obsidian = долгосрочная память, бренд, история          │
└────────────────────────────────────────────────────────────┘
```

**Главная мысль (Julian Goldie, видео 1):** *"You stop being the worker, you become the owner of the factory. Machine makes the content, you just feed it and collect the results."*

---

## 4. Маппинг на MATRYOSHKA DIGITAL

| Компонент из видео | У нас | Гэп |
|---|---|---|
| **NotebookLM** | ❌ не интегрирован, VNC-доступ через x11vnc:6080/5900 | 🔴 **нужен MCP-мост** |
| **Hermes Agent (Nous Research)** | ❌ | 🔴 можно поднять на VPS или локально |
| **MCP-протокол** | ❌ у нас ws_client.py, не MCP | 🟡 можно мигрировать на MCP в перспективе |
| **Obsidian** | ✅ `C:\Users\User\ai-knowledge\` (полный vault) | 🟢 работает |
| **N8N** | ✅ работает на `matryoshka-digital.ru/n8n` (5678) | 🟢 работает |
| **N8N MCP** | ❌ не активирован | 🟡 **включить** (видео 4 показывает как) |
| **Hyperframes** | ❌ | 🟡 опционально (видео-контент для ALISA) |
| **Pantheon Dashboard** | ❌ | 🟡 опционально |
| **Alpha API / OpenRouter** | ✅ OpenRouter (`sk-or-v1-f114...`), OpenCode Zen, 5 провайдеров | 🟢 работает |
| **HERMES (наш, дирижёр)** | ✅ VPS, WS:8446, MiniMax-M2.7 | 🟢 работает, **НЕ ПУТАТЬ с Hermes Agent** |
| **Telegram-бот** | ✅ 3 бота (основной, Алина, n8n) | 🟢 работает |
| **VNC к NotebookLM** | ✅ x11vnc:5900, websockify:6080 (уже в плане) | 🟢 инфра готова |
| **WebSocket-мост** | ✅ ws_client.py v37 | 🟢 работает |
| **Локальный роутер** | ✅ alex_router.py:4000 | 🟢 работает |

---

## 5. Гэп-анализ и план внедрения

### 🔴 P0 (сделать в первую очередь)

1. **Поднять NotebookLM с VNC** — у нас уже есть x11vnc, нужно:
   - установить Chromium на VPS
   - открыть notebooklm.google.com
   - залогиниться
   - прокинуть VNC через nginx или прямой порт
2. **Включить N8N MCP** — Jack Roberts в видео 4 показывает **пошагово**:
   - зайти `n8n.basicapp.n8n.cloud/settings/mcp` (у нас свой n8n → `/settings/mcp`)
   - Enable workflows → Connection details → скопировать server URL + access token
   - дать Hermes команду подключиться
3. **Установить NotebookLM skill в Claude Code / opencode** — скачать с репозитория (Jack Roberts даёт ссылку), загрузить, сказать "install the NotebookLM skill".

### 🟡 P1 (в течение 1–2 недель)

4. **Создать первый продуктовый notebook** — например, "DATALINK_PRO / AI-сотрудники" с 50–100 источниками (лендинги, кейсы, FAQ, документация). Использовать для генерации контента для ALISA.
5. **Поднять Hyperframes** — open-source skill, добавить в HERMES для генерации видео-аватаров.
6. **Memory-Loop** — связать Obsidian с результатами NotebookLM так, чтобы каждый новый артефакт попадал в vault.

### 🟢 P2 (фоново)

7. **Pantheon-дашборд** — визуальный обзор skills.
8. **Cron-контент через N8N + NotebookLM** — "каждое утро 8:00 — генерируй подкаст по новой теме".
9. **SEO-конвейер для matryoshka-digital.ru** — об этом прямо говорит Julian Goldie в видео 3: "свежий контент → Google → трафик".

---

## 6. Технические детали из видео 4 (Jack Roberts, how-to)

### 6.1. Установка NotebookLM skill
```
1. Скачать skill-файл по ссылке из описания
2. Открыть Claude Code (или opencode)
3. Загрузить файл: "install the NotebookLM skill, please"
4. Будет запрос: "could you reauthenticate notebook LM, please"
5. Открыть notebooklm.google.com в браузере → залогиниться
6. Cookie цепляется → MCP активен
7. Тест: "find the last 3 notebooks in notebook LM"
```

### 6.2. Подключение N8N MCP к Hermes
```
1. n8n.cloud → Settings → MCP → Enable workflows
2. Copy server URL + access token
3. В Hermes: "give me a bash command to connect to N8N MCP with my token"
4. Hermes возвращает: export N8N_MCP_ACCESS_TOKEN="..."
5. В терминале: вставить команду → enter
6. "reload MCP" → approve → готово
7. Тест: "create a workflow in N8N that triggers every morning at 8am..."
```

### 6.3. Создание Notebook через Hermes
```
"go ahead and create for me a brand new Notebook LM on [тема]
and bring in all the resources you need, and use any information
about me that you may have to make that a reality"
```
→ Hermes дёргает NotebookLM MCP → создаётся notebook с 9–30 источниками автоматически.

### 6.4. Cron-контент (видео 4, Jack Roberts)
```
"every morning at 8am, go ahead and create me a Notebook LM on
something you think is going to be valuable based on our conversations
in the last 24 hours. Then drop for me the podcast overview and the
infographic from that, so I can read it first thing at 8am"
```

---

## 7. Риски и противоречия

### 7.1. Технические
- **NotebookLM MCP — неофициальный**, Google может сломать auth в любой момент.
- **300 источников на notebook** — лимит; для больших проектов нужно несколько ноутбуков.
- **Cookie-based auth** — сессия протухает, придётся перелогиниваться периодически.
- **Не deterministic** — Jack Roberts сам предупреждает: *"you ask 100 questions, you get 100 responses"*. Для email-рассылок — критично, нужен N8N как контроль.

### 7.2. Маркетинговые
- **Julian Goldie** продаёт AI Profit Boardroom за ~$2k. В видео 75% — продажа, 25% — реальный how-to. Нужно фильтровать.
- **Jack Roberts** продаёт мастер-класс. Видео 4 — самое техническое, его брать за основу.
- **Не путать Hermes Agent (Nous) с нашим HERMES (дирижёр)** — критично при обсуждении с командой.

### 7.3. Юридические
- **Авторские права на контент** — NotebookLM обучен на чужих источниках, при переработке — нужна оговорка.
- **AI-контент и Google SEO** — Google прямо заявил, что **AI-контент допустим, если полезен** (E-E-A-T). Это в нашу пользу.

---

## 8. Ключевые цитаты-инсайты

> **Julian Goldie (видео 1, 02:08):** *"you can connect the same setup to other agents you might already use. Notebook LM panel for content, studio panel for making images and videos and voice, an SEO panel, board where you hand tasks to a team of agents... One person doing the work of a whole team."*

> **Julian Goldie (видео 2, 02:12):** *"when you look at Notebook LM, it's not that it's a tool problem, right? The tool is great. The problem is really a system. And so, that's what we need inside here. And the fix is really Hermes agent."*

> **Julian Goldie (видео 3, 04:33):** *"Every time you make something new, it feeds back into the memory. The system gets smarter every single day... you can keep stacking. Make a podcast version, make an infographic, make a slide deck, all from the same notebook, all in one place."*

> **Jack Roberts (видео 4, 02:38):** *"I could literally be on the go. We could be having coffee with our buddies, right? Playing fetch with our dog, and it will go ahead and do all this stuff for us from the laptop wherever we are."*

> **Jack Roberts (видео 4, 09:50):** *"There is nothing better at... The Notebook LM is 100% free. We can have a vector database of 300 separate YouTube videos on anything you want, and we can query it at zero dollars... your cost on this is unbelievably low."*

> **Julian Goldie (видео 3, 06:45):** *"free agent, free skill, free connector, free memory, free models. You went from 'I made one cool thing in Notebook LM' to a full content factory that runs itself."*

---

## 9. Немедленные следующие шаги

1. **Открыть VNC к NotebookLM** на VPS (через x11vnc:5900/websockify:6080) → залогиниться → создать первый notebook "MATRYOSHKA DIGITAL / AI-сотрудники".
2. **Включить N8N MCP** в нашем n8n-инстансе (`/settings/mcp`).
3. **Установить NotebookLM skill** в opencode на ПК.
4. **Связать Obsidian + NotebookLM** — результаты из NotebookLM → автоматом в vault.
5. **Протестировать Hyperframes** — нужен ли для ALISA.
6. **Написать ТЗ для ALISA** — контент-конвейер на базе NotebookLM.

---

## 10. Файлы и артефакты

- Сырые транскрипты: `C:\Users\User\AppData\Local\Temp\opencode\yt_transcripts\01-04_*.txt`
- JSON с таймкодами: `C:\Users\User\AppData\Local\Temp\opencode\yt_transcripts\01-04_*_timestamped.json`
- Markdown-чанки: `C:\Users\User\AppData\Local\Temp\opencode\yt_chunks\01-04_*_chunks.md`
- Скрипт fetch: `C:\Users\User\AppData\Local\Temp\opencode\fetch_yt.py`
- Скрипт split: `C:\Users\User\AppData\Local\Temp\opencode\split_chunks.py`
- Этот отчёт: `C:\Users\User\ai-knowledge\projects\NOTEBOOKLM_HERMES_ANALYSIS_2026-06-07.md`
- Копия в AGENTS: `C:\Users\User\ai-knowledge\AGENTS\NOTEBOOKLM_HERMES_ANALYSIS_2026-06-07.md`

---

*ALEX · 2026-06-07 · MATRYOSHKA DIGITAL*
