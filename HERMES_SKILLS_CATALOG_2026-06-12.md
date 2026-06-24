# HERMES SKILLS CATALOG — все 108 активных скилов
**Дата:** 12.06.2026
**Версия Hermes:** v0.16.0
**Профиль:** hermes-cli
**Путь:** `/root/.hermes/profiles/hermes-cli/skills/`
**Всего скиллов:** 143 (108 активных + 35 в `.archive/`)

---

## КАТЕГОРИЯ 1: MATRYOSHKA (12 скилов) — МОИ проекты

| # | Скилл | Что делает | Когда использовать |
|---|-------|------------|---------------------|
| 1 | `matryoshka-connection` | Umbrella-скилл для всей архитектуры | Каждая сессия про MATRYOSHKA |
| 2 | `alex-connection` | Связь с ПК Олега (opencode), 5 причин зависания | Перед делегированием Аликсу |
| 3 | `acp-alex-connection` | ПРАВИЛЬНАЯ архитектура Hermes↔Аликс через ACP | Когда ACP не работает |
| 4 | `hermes-image-workflow` | End-to-end генерация картинок | По запросу Олега |
| 5 | `product-card-generator` | Финальный алгоритм XKIN карточек | Перед генерацией карточек |
| 6 | `xkin-cards` | Правила карточек и инфографики XKIN | Перед XKIN задачами |
| 7 | `deep-system-audit` | Паттерн "Олег в ярости" — 4 документа по 10-25 KB | Когда Олег требует "глубокий аудит" |
| 8 | `image-annotation-oleg` | Обводить красным детали на фото | Когда Олег "выдели это" |
| 9 | `seo-content-cron` | SEO контент через cron | Для автогенерации |
| 10 | `gateway-profile-daily-audit` | Daily health check профиля | Каждый день |
| 11 | `matryoshka-investigation` | Навигация + investigation | Когда непонятно где файл |
| 12 | `acp-alex-connection` | Альтернативный ACP протокол | Альтернатива alex-connection |

---

## КАТЕГОРИЯ 2: CREATIVE (28 скилов) — картинки, видео, дизайн

### 2.1. Картинки (через Gemini/ComfyUI)
| Скилл | Что делает |
|-------|------------|
| `gemini-image-specialist` | Специалист по генерации через Gemini |
| `gemini-image-workflow` | Workflow генерации |
| `gemini-product-card-workflow` | Карточки товара через Gemini |
| `gemini-product-infographic` | ⚠️ УСТАРЕЛ — Gemini заблокирован в РФ (2026-06-01) |
| `product-image-overlay-workflow` | Наложение текста на фото |
| `comfyui` | ComfyUI для продвинутой генерации |
| `baoyu-article-illustrator` | Иллюстрации к статьям |
| `baoyu-infographic` | 21 layout × 21 style |
| `baoyu-comic` | Knowledge comics (обучающие) |
| `baoyu-creative` | Базовая творческая генерация |
| `card-rules` | Инфографика карточек через Gemini + PIL |
| `claude-design` | One-off HTML артефакты |

### 2.2. Дизайн
| Скилл | Что делает |
|-------|------------|
| `architecture-diagram` | Dark-themed SVG архитектурные диаграммы |
| `excalidraw` | Hand-drawn Excalidraw диаграммы |
| `sketch` | Throwaway HTML mockups (2-3 варианта) |
| `design-md` | Google DESIGN.md token spec |
| `popular-web-designs` | 54 реальных design systems (Stripe, Linear, Vercel) |
| `pretext` | Browser demos с @chenglou/pretext |
| `humanizer` | Убрать AI-isms из текста, добавить голос |

### 2.3. Видео и спецэффекты
| Скилл | Что делает |
|-------|------------|
| `ascii-art` | pyfiglet, cowsay, image-to-ascii |
| `ascii-video` | Видео → colored ASCII MP4/GIF |
| `manim-video` | 3Blue1Brown математические видео |
| `p5js` | p5.js sketches (gen art, shaders) |
| `pixel-art` | Pixel art (NES, Game Boy, PICO-8) |
| `touchdesigner-mcp` | TouchDesigner через twozero MCP |
| `songwriting-and-ai-music` | Suno AI музыка |
| `creative-ideation` | Brainstorm проектов через ограничения |

---

## КАТЕГОРИЯ 3: AUTONOMOUS-AI-AGENTS (5 скилов) — делегирование

| Скилл | Что делает | Когда |
|-------|------------|-------|
| `claude-code` | Делегировать кодинг Claude Code CLI | Фичи, PR |
| `codex` | Делегировать OpenAI Codex CLI | Фичи, PR |
| `opencode` | Делегировать OpenCode CLI | Code review |
| `coding-agents` | Общий паттерн (Claude/Codex/Goose) | Выбор агента |
| `hermes-agent` | **Настройка Hermes Agent** (config, setup, troubleshoot) | Когда меняю себя |
| `kanban-codex-lane` | Kanban worker + Codex CLI | Внутри Kanban workflow |

---

## КАТЕГОРИЯ 4: DEVOPS (10 скилов)

| Скилл | Что делает |
|-------|------------|
| `kanban-orchestrator` | Оркестратор Kanban workflow |
| `kanban-worker` | Воркер Kanban |
| `kanban-workflow` | Multi-agent Kanban workflow |
| `nginx-webdav-vps` | WebDAV через nginx (Obsidian Sync) |
| `pc-hardware-diagnostics` | Диагностика перезагрузок/выключений ПК |
| `vps-disk-audit` | Глубокий аудит диска VPS |
| `webhook-subscriptions` | Event-driven agent runs |
| `ios-android-screenshot-diagnosis` | Помощь с iOS/Android формами |
| `vision-always-helper` | Анализ картинок через vision_helper.py |
| `hermes-s6-container-supervision` | Изменить s6-overlay (в .archive/) |

---

## КАТЕГОРИЯ 5: PRODUCTIVITY (9 скилов)

| Скилл | Что делает |
|-------|------------|
| `notion` | Notion API + ntn CLI |
| `airtable` | Airtable REST API |
| `google-workspace` | Gmail, Calendar, Drive через gws |
| `powerpoint` | .pptx редактирование |
| `linear` | Linear issues через GraphQL |
| `maps` | Геокодирование через OSM |
| `nano-pdf` | Edit PDF text через NL |
| `ocr-and-documents` | Extract text из PDF |
| `teams-meeting-pipeline` | Teams meeting summary |

---

## КАТЕГОРИЯ 6: MLOPS (12 скилов)

### 6.1. Inference
| Скилл | Что делает |
|-------|------------|
| `llama-cpp` | GGUF inference + HF Hub discovery |
| `vllm` | High-throughput LLM serving |
| `outlines` | Structured JSON/regex/Pydantic generation |
| `obliteratus` | Obliterate LLM refusals |

### 6.2. Training
| Скилл | Что делает |
|-------|------------|
| `unsloth` | 2-5x faster fine-tuning |
| `axolotl` | YAML LLM fine-tuning (LoRA, DPO, GRPO) |
| `trl-fine-tuning` | SFT, DPO, PPO, GRPO |

### 6.3. Evaluation & Models
| Скилл | Что делает |
|-------|------------|
| `lm-evaluation-harness` | Benchmarking MMLU, GSM8K |
| `weights-and-biases` | W&B experiments |
| `huggingface-hub` | HF hf CLI |
| `audiocraft-audio-generation` | MusicGen + AudioGen |
| `segment-anything` | SAM segmentation |
| `dspy` | Declarative LM programs |

---

## КАТЕГОРИЯ 7: HERMES (4 скила) — самообслуживание

| Скилл | Что делает |
|-------|------------|
| `voice-transcription` | STT через faster-whisper |
| `mcp-critical-setup` | Подключение MCP серверов |
| `never-lose-context` | Сохранение контекста между сессиями |
| `tupek-protocol` | Правило 2 попыток при тупике |

---

## КАТЕГОРИЯ 8: GITHUB (3 скила)

| Скилл | Что делает |
|-------|------------|
| `github-workflow` | PR lifecycle, branch, commit, open PR |
| `codebase-inspection` | Инспекция через pygount (LOC, языки) |
| `github` (umbrella) | Все GitHub операции |

**Под-скиллы:** github-auth, github-pr-workflow, github-issues, github-code-review, github-repo-management

---

## КАТЕГОРИЯ 9: SOFTWARE-DEVELOPMENT (4 скила)

| Скилл | Что делает |
|-------|------------|
| `plan` | Plan mode: markdown план в .hermes/ |
| `python-debugpy` | Python debug: pdb REPL + debugpy |
| `node-inspect-debugger` | Node.js debug через --inspect + CDP |
| `simplify-code` | 3-agent parallel cleanup (в .archive/) |

**В .archive/:** subagent-driven-development, test-driven-development, systematic-debugging, spike, requesting-code-review, writing-plans, hermes-agent-skill-authoring

---

## КАТЕГОРИЯ 10: RESEARCH (2 скила)

| Скилл | Что делает |
|-------|------------|
| `research` | Общий research workflow |
| `research-paper-writing` | Написание академических статей |

**В .archive/:** arxiv, blogwatcher, llm-wiki, polymarket, research-via-curl

---

## КАТЕГОРИЯ 11: MEDIA (5 скилов)

| Скилл | Что делает |
|-------|------------|
| `youtube-content` | YouTube transcripts → summaries |
| `gif-search` | GIF search через Tenor |
| `spotify` | Spotify playback |
| `songsee` | Audio spectrograms |
| `heartmula` | Suno-like song generation |

---

## КАТЕГОРИЯ 12: ОСТАЛЬНЫЕ (16 скилов)

| Категория | Скилы |
|-----------|-------|
| **ai-agent-with-pluggable-tools** | Архитектура AI-агента (Telegram-бот) |
| **alex-connection-diagnostics** | Чеклист диагностики Аликса |
| **apple-ecosystem** | Apple интеграции |
| **data-science** | Jupyter live kernel |
| **dogfood** | QA web apps (поиск багов) |
| **email** | Himalaya CLI (IMAP/SMTP) |
| **engineering-practices** | Практики разработки |
| **gaming** | Minecraft modpack, Pokemon player |
| **hermes-ops** | Эксплуатация Hermes |
| **mcp** | Native MCP client |
| **multi-agent-production-ops** | Multi-agent VPS обслуживание |
| **n8n-task-runners** | External task runner |
| **note-taking** | Obsidian vault |
| **oleg-11jun-mandate** | Подтверждённые правила поведения с Олегом |
| **oleg-communication-style** | Стиль общения с Олегом |
| **red-teaming** | godmode (jailbreak тесты) |
| **smart-home** | OpenHue (Philips Hue) |
| **social-media** | Xurl (X/Twitter) |
| **vps-ssh-hardening** | SSH защита от брутфорса |
| **yuanbao** | Yuanbao groups |

---

## 35 СКИЛЛОВ В `.archive/` (curator заархивировал)

| Категория | Скилы |
|-----------|-------|
| research | arxiv, blogwatcher, llm-wiki, polymarket, research-via-curl |
| software-development | systematic-debugging, hermes-agent-skill-authoring, hermes-s6-container-supervision, writing-plans, requesting-code-review, debugging-hermes-tui-commands, subagent-driven-development, test-driven-development, spike, simplify-code |
| hermes | hermes-recovery, hermes-file-delivery |
| matryoshka | matryoshka-alf-qwen-setup, matryoshka-full-state-audit |
| devops | kanban-worker |
| red-teaming | (все внутри) |

**Почему в архиве:** curator автоматически архивирует скилы, которые не используются >N дней (`stale_after_days`). Не удаляет — переносит в `.archive/` с префиксом.

**Как восстановить:** `mv .archive/skill-name ./skill-name` или создать заново через `skill_manage(action='create', ...)`.

---

## СТАТИСТИКА

| Метрика | Значение |
|---------|----------|
| Всего скиллов на диске | 143 |
| Активных | 108 |
| В .archive/ | 35 |
| Категорий | 21 |
| Самый большой категория | creative (28) |
| Самый важный для MATRYOSHKA | matryoshka/* (12) |
| Curator pinned | 0 (потенциально стоит запинить matryoshka-connection) |
