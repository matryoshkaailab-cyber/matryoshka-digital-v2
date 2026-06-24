# ALF (Strategic Analyst) — полный технический документ v4.2
**Версия:** 2026-06-24 | **Автор:** HERMES (live-check) | **Статус:** ✅ Active (отдельный systemd процесс)
**Предыдущая версия:** v4.1 (20.06.2026, live-checked by HERMES)

---

## 🔄 LIVE-CHECK 24.06.2026 15:40 (важно — обновление v4.1 → v4.2)

**Сделано сегодня (24.06.2026):**
- **12:30** — patch config: M3 → Nemotron 550B через NVIDIA API
- **13:30** — patch config: Nemotron → Kimi K2.6 (Олег мандат 24.06: «убери Nemotron, поставь Kimi K2.6»)
- **14:30** — patch SOUL.md (8KB → 2.3KB; после patch config v7.0 → 2.8KB)
- **14:35** — patch config: `providers.nvidia.default_model: nvidia/nemotron-3-ultra-550b-a55b` → `moonshotai/kimi-k2.6` (исправляет Hermes Agent игнорирование model.default)
- **15:25** — **patch `alf_filewatcher.py:50-55`**: убран `break` в `call_alf()` (баг: брал только ПЕРВУЮ строку stdout = 27 chars). Теперь собирает ВСЕ строки через `"\n".join()`. **Filewatcher отвечает полно (200-2000 chars).**
- **15:40** — patch systemd unit: `Restart=always` → `Restart=on-failure` (стабильность, нет бесконечного цикла рестартов)

**Текущее состояние (24.06.2026 15:40):**
- **Модель:** `moonshotai/kimi-k2.6` (через прямой NVIDIA API)
- **Context:** 131072 (128K)
- **Temperature / Top_p:** 1 / 0.95 (Олег мандат)
- **Провайдер:** nvidia (NVIDIA NIM, бесплатно)
- **Patch'и:** config.yaml, SOUL.md v7.0, alf_filewatcher.py v3.1, systemd unit
- **Healthcheck :8452:** OK, gateway uptime 44+ мин
- **Filewatcher:** отвечает полно (не 27 chars заголовок)

**История изменений (24.06.2026):**
- v1-v5: M3, OpenRouter Nemotron, MiMo план (отменён, нет ключа)
- v6 (12:30): Nemotron 550B → M3 (обрезка длинных задач)
- v7 (14:30): **Kimi K2.6 через NVIDIA NIM** (текущая, актуальная)
- v7.1 (15:25): filewatcher call_alf() fix (полные ответы)
- v7.2 (15:40): Restart=on-failure (стабильность)

---

## ⚠️ LIVE-CHECK 20.06.2026 23:13 (v4.1, устаревшая инфа — см. v4.2 выше)

**НАЙДЕН КРИТИЧЕСКИЙ БАГ** (починен сменой модели):
- ALF gateway ПАДАЛ с **19:31 20.06.2026** (~4 часа даунтайм)
- Причина: `model: openrouter/deepseek/deepseek-v4-flash` = **40K context**, Hermes Agent требует **минимум 64K**
- `ValueError: Model openrouter/deepseek/deepseek-v4-flash has a context window of 40,000 tokens, which is below the minimum 64,000 required`
- **Фикс:** default → `openrouter/nvidia/nemotron-3-ultra-550b-a55b` (128K context, $0.00007/вызов)
- **24.06.2026:** ALF переключён на `nvidia/nemotron-3-ultra-550b-a55b` через **прямой NVIDIA API** (`https://integrate.api.nvidia.com/v1`), **НЕ OpenRouter**. Бесплатный ключ, reasoning включён (enable_thinking), 12 сек на ответ. Общий token pool с HERMES устранён.
- **ALF сейчас ЗАПУЩЕН с Nemotron Ultra 550B через ПРЯМОЙ NVIDIA API (24.06.2026) — НЕ OpenRouter**

---

## 1. ИДЕНТИЧНОСТЬ

| Параметр | Значение |
|---|---|
| **Имя** | ALF (Analyst, Logician, Forecaster) |
| **Прежние имена** | АЛАН (до 17.05.2026) |
| **Роль** | Стратег, библиотекарь, аналитик рынка, архитектор планов |
| **Рой** | ⚪ Белый (Мозг) |
| **Назначение** | Аналитика, стратегия, планирование, стратегические insights, страховка от галлюцинаций (NotebookLM) |
| **Пользователь** | Олег (Telegram ID `1951845052`) |
| **Telegram-бот** | `@IlonAnalyticBot` (через Hermes gateway) |

---

## 2. ГДЕ ЖИВЁТ (v4.1, обновлено 20.06.2026)

| Компонент | Расположение |
|---|---|
| **Архитектура** | **Отдельный systemd процесс** (НЕ persona внутри Hermes Agent) |
| **systemd unit** | `hermes-gateway-alf.service` (system-wide, НЕ user) |
| **Venv** | `/opt/alf-hermes/venv` |
| **Config** | `/root/.hermes/profiles/alf/config.yaml` (Nemotron 550B, OpenRouter) |
| **Env** | `/root/.hermes/profiles/alf/.env` (TELEGRAM_BOT_TOKEN, NVIDIA_API_KEY, OPENROUTER_API_KEY, MINIMAX_API_KEY) |
| **SOUL** | `/root/.hermes/profiles/alf/SOUL.md` (требует обновления — см. ниже) |
| **Skills** | `/root/.hermes/profiles/alf/skills/` + symlink на `/root/.hermes/skills/notebooklm` |
| **Memory** | `/root/.hermes/profiles/alf/state.db` (holographic memory) |
| **PID** | 3119831 (live 20.06.2026, 18ч running) |
| **Логи** | `journalctl -u hermes-gateway-alf -f` |
| **Telegram token** | В `.env` (@IlonAnalyticBot, token 8941776316:...) |
| **VPS** | 85.137.166.209 (root) |

### ❌ DEPRECATED в v4.0 (НЕ ИСПОЛЬЗУЕТСЯ)
- ❌ `alf_server.py` :8451 (standalone HTTP API) — DEPRECATED 18.06.2026
- ❌ `alf_telegram_bot.py` (отдельный Telegram polling) — заменён на Hermes gateway
- ❌ HTTP-stub на :8453 (proxy на мёртвый 10.8.1.4:8446) — DEPRECATED, target мёртв с 15.06

> ⚠️ **ВНИМАНИЕ:** В ALF_FULL.md v4.0 (17.06) написано "persona в Hermes Agent, systemd user" — ЭТО УСТАРЕЛО. Реально: отдельный systemd system-wide процесс с 18.06.2026.

---

## 3. МОДЕЛЬ И ПРОВАЙДЕРЫ (v4.1, 20.06.2026)

| Параметр | Значение |
|---|---|
| **Default model** | `nvidia/nemotron-3-ultra-550b-a55b` через **прямой NVIDIA API** (`integrate.api.nvidia.com/v1`) |
| **Provider primary** | `openrouter` (https://openrouter.ai/api/v1) |
| **Provider NVIDIA direct** | `nvidia` (https://integrate.api.nvidia.com/v1) — GeForce Account, бесплатно (если работает) |
| **API keys** | `OPENROUTER_API_KEY`, `NVIDIA_API_KEY`, `MINIMAX_API_KEY` в `.env` |
| **Fallback** | отключён (24.06.2026 — больше не нужен, своя модель) |
| **Temperature** | 0.7 (default) |
| **Context length** | 128K (override 40K минимум Hermes) |

**Правило v4.1 (20.06):** Использовать **NVIDIA Nemotron Ultra 550B** через **прямой NVIDIA API** (24.06.2026) как primary. Это reasoning-модель (550B params, 55B active, отлично для стратегии, **БЕСПЛАТНАЯ**). DeepSeek-v4-flash больше НЕ использовать (40K context, несовместим с Hermes).

### Почему Nemotron 550B
- **Reasoning model** (как o1) — лучше для стратегий и аналитики
- **128K context** (бывший deepseek имел 40K → ALF падал)
- **$0.00007/вызов** через OpenRouter DeepInfra provider (дёшево)
- **Бесплатно** через NVIDIA GeForce Account (если rate limit не превышен)

---

## 4. TELEGRAM ИНТЕГРАЦИЯ

| Параметр | Значение |
|---|---|
| **Bot username** | @IlonAnalyticBot |
| **Token** | `8941776316:***` (в `.env`) |
| **Allowed users** | `1951845052` (только Олег) |
| **Home channel** | `1951845052` (Олег в личке) |
| **Polling** | Через Hermes gateway (long polling) |
| **Webhook** | НЕТ (используется polling) |
| **Commands** | 30 видимых + 165 скрытых (через `/commands`) |

---

## 5. БАЗА ЗНАНИЙ

### 5.1. NotebookLM (основная)
- **Notebook ID:** `38d2a04f-9f73-49c7-baf7-0a289eecfa8a`
- **Название:** "Matryoshka Digital: The Russian AI Business Operating System"
- **Источников:** 34 (MATRYOSHKA DIGITAL knowledge base)
- **URL:** https://notebooklm.google.com/notebook/38d2a04f-9f73-49c7-baf7-0a289eecfa8a
- **Auth:** `~/.notebooklm/profiles/default/storage_state.json` (живёт недолго)
- **Proxy:** `45.83.11.211:8000` (USA, не VPS IP) с auth `gusQy8:gUs0gA`
- **Загрузка источников:** `C:\Scripts\alex_nb_v9.py` (на ПК) — Playwright bundled chromium + прокси
- **Skill:** `/root/.hermes/skills/notebooklm` (symlink из основной папки)
- **ОБЯЗАТЕЛЬНАЯ интеграция с ALF** (Олег мандат 20.06.2026) — ALF может индексировать NotebookLM, выдавать срезы знаний

### 5.2. Knowledge base (локально)
- `/root/matryoshka/alf/knowledge/` — 33 файла, 1.7 MB
  - changelog/ analytics/ clients/ wiki/ daily/ research/
- `/root/obsidian-vault/` — mirror на WebDAV

### 5.3. Holographic memory
- Хранится в `state.db` профиля
- Запоминает контекст пользователя, проекты, контакты

---

## 6. ЧТО ДЕЛАЕТ (Council #1, 20.06.2026)

1. **Анализ рынка** — конкуренты, тренды, ниши
2. **Стратегия** — долгосрочные планы MATRYOSHKA
3. **Архитектура планов** — декомпозиция задач, roadmaps
4. **Стратегические insights** — для решений Олега
5. **Библиотекарь** — точная выдача знаний с цитированием (NotebookLM + knowledge/)
6. **Страховка от галлюцинаций** — проверка фактов через source list
7. **Подмена HERMES** в простых задачах (когда не нужно дирижировать)
8. **Контент-стратегия** — для ALISA (отложена)

---

## 7. КОМАНДЫ TELEGRAM

### 7.1. Основные
- `/start` — приветствие
- `/help` — список команд
- `/status` — состояние ALF
- `/new` — новая сессия
- `/clear` — очистить контекст
- `/ask "..."` — задать вопрос (Олег 20.06)

### 7.2. NotebookLM (skill: notebooklm)
- `/notebooklm ask "..."` — задать вопрос notebook
- `/notebooklm list` — список notebooks
- `/notebooklm source list` — источники в активном notebook
- `/notebooklm generate audio "..."` — подкаст
- `/notebooklm generate report` — отчёт
- `/notebooklm generate quiz` — квиз

### 7.3. Skills (auto-loaded)
- `research` — веб-поиск
- `browser` — Playwright MCP
- `file` — работа с файлами
- `terminal` — выполнение команд
- `memory` — holographic memory
- `notebooklm` — NotebookLM API

---

## 8. СВЯЗЬ С ДРУГИМИ АГЕНТАМИ

| Агент | Роль | Связь с ALF |
|---|---|---|
| **HERMES** | Дирижёр, оркестратор | Управляет ALF как одним из роя |
| **ALEX (Аликс)** | Тех инженер | Только через HERMES (file-queue `.hermes_task_alf.json`) |
| **ALISA** (@AlisaMatBot) | Маркетинг/контент | Отложена, ALF может помочь когда запустится |
| **ALINA** (@NikolaAlinaBot) | Клиентский кейс Николая | ❌ НЕ часть роя Олега (изоляция v3.2) |

---

## 9. СТЕК

- **Hermes Agent** (open-source от Nous Research, профиль `alf`)
- **NVIDIA Nemotron Ultra 550B** (через OpenRouter) — primary
- **MiniMax-M3** (через провайдер `minimax`) — fallback
- **NotebookLM MCP** (knowledge base) — обязательно
- **Telegram Bot API** (UI)
- **Holographic memory** (контекст)
- **systemd** (system-wide service) — не user

---

## 10. ИСТОРИЯ ВЕРСИЙ

| Версия | Дата | Изменения |
|---|---|---|
| **v1.0** | май 2026 | Standalone server `alf_server.py` :8451, прямой Telegram polling |
| **v2.0** | 06.06.2026 | Переход на MiniMax-M3 primary, Qwen убран |
| **v3.0** | 15.06.2026 | Telegram bot `alf_telegram_bot.py` с прямым вызовом `alf_server.py` |
| **v4.0** | 17.06.2026 | Persona в Hermes, gateway через systemd user, NotebookLM `38d2a04f` |
| **v4.0 (real)** | 18.06.2026 | Реально: отдельный systemd system-wide процесс, не persona |
| **v4.1** | **20.06.2026** | **Модель: NVIDIA Nemotron Ultra 550B (через OpenRouter)**. **ИСПРАВЛЕН БАГ: deepseek-v4-flash 40K context → ALF падал с 19:31**. ALF_FULL.md обновлён под реальность. |

---

## 11. КАК УПРАВЛЯТЬ

### Проверить статус
```bash
systemctl status hermes-gateway-alf.service
curl -sS http://localhost:8453/health  # HTTP stub, target мёртв
journalctl -u hermes-gateway-alf -n 50 -f
```

### Перезапустить
```bash
systemctl restart hermes-gateway-alf.service
```

### Обновить конфиг
```bash
nano /root/.hermes/profiles/alf/config.yaml
systemctl restart hermes-gateway-alf.service
```

### Сменить модель
```yaml
# В config.yaml:
model:
  default: openrouter/nvidia/nemotron-3-ultra-550b-a55b  # primary
  # или
  default: openrouter/deepseek/deepseek-v4-flash  # 40K context — НЕ ИСПОЛЬЗОВАТЬ (ALF падает)
  # или
  default: minimax-coding-plan/MiniMax-M3  # fallback
```

### Обновить SOUL.md
```bash
nano /root/.hermes/profiles/alf/SOUL.md
systemctl restart hermes-gateway-alf.service
```

---

## 12. ПРОБЛЕМЫ И РЕШЕНИЯ (обновлено 20.06)

| Проблема | Решение |
|---|---|
| **Telegram polling conflict** | Убить старые процессы: `pkill -f alf_telegram_bot.py` |
| **ALF не отвечает** | `journalctl -u hermes-gateway-alf -f` — смотреть логи |
| **NotebookLM auth слетел** | Залогиниться через `notebooklm login` с прокси или через `alex_nb_v9.py` на ПК |
| **storage_state.json не создаётся** | Playwright Chromium не установлен на VPS: `playwright install chromium` |
| **Model context <64K → ALF падает** | Использовать Nemotron 550B (128K) или MiniMax-M3 (200K) |
| **ALF не реагирует на `inbox/alf/` файлы** | Только Telegram. Либо cron → ALF, либо использовать Telegram-мост |

---

## 13. ССЫЛКИ

- **Telegram bot:** @IlonAnalyticBot
- **NotebookLM notebook:** https://notebooklm.google.com/notebook/38d2a04f-9f73-49c7-baf7-0a289eecfa8a
- **Hermes skill:** `/root/.hermes/skills/notebooklm/SKILL.md`
- **Council #1 (20.06.2026):** `/root/matryoshka/COUNCIL_ALF_2026-06-20.md`

---

*ALF v4.1 · 2026-06-20 23:13 · MATRYOSHKA DIGITAL · NVIDIA Nemotron Ultra 550B + NotebookLM обязательно · Live-checked by HERMES*
