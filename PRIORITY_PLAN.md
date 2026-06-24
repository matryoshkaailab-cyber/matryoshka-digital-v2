# ⚠️ DEPRECATED 2026-06-16 — ФЕЙКИ
# Этот файл содержит УСТАРЕВШИЕ данные: агенты ILON/OpenClaw (не существуют),
# VPN UUID 4ea33e69 / SNI microsoft (ВЫДУМАННЫЕ — реально SNI=www.google.com),
# Hermes v0.15.1 / MiniMax-M2.7 (НЕ СУЩЕСТВУЕТ — v0.16.0 / MiniMax-M3).
# НЕ ИСПОЛЬЗОВАТЬ как источник истины.
# Источник правды: /root/matryoshka/AGENTS.md + /root/matryoshka/SOUL.md
# Holographic memory: fact #28 (warnings о фейках)
# Skill автопроверки: soul-fake-detection
# Если нужна актуальная инфа — перегенерируй документ или спроси Hermes.
# ────────────────────────────────────────────────────────────────────────

# PRIORITY PLAN — MATRYOSHKA DIGITAL
# P0 — КРИТИЧЕСКИЙ | Создан: 2026-05-20

## СТАТУС: [ЭТАП 5 из 5 — ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ]

---

## ЭТАП 1: СИНХРОНИЗАЦИЯ ДОКУМЕНТАЦИИ — ✅ ЗАВЕРШЁН
- [x] Создать PRIORITY_PLAN.md (ПК + VPS + Obsidian)
- [x] Обновить SOUL.md (ПК) — добавить ссылку на план
- [x] Обновить AGENTS.md (ПК) — правильная архитектура
- [x] Обновить .current_context.md (ПК) — правильная архитектура
- [x] Обновить opencode.json — правильные модели (qwen3.6-plus-free)
- [x] Обновить CLAUDE.md — пометить как legacy
- [x] Обновить COMPANY_CONTEXT.md — убрать ILON
- [x] Обновить VPS: .current_context.md, AGENTS.md, SOUL.md
- [x] Обновить VPS: PROJECTS/MATRYOSHKA/ARCHITECTURE.md (v3)
- [x] Обновить Obsidian: wiki/SYSTEM/_index.md, wiki/AGENTS/_index.md, 00_INDEX.md
- [x] Удалить мусорные файлы ПК (25+ файлов: ILON, TOLIK, OpenClaw, ws_client v4-v11, боты)
- [x] Удалить мусорные файлы VPS (bot_v2.py, profiles/alex, backup_*, /tmp мусор, open-design)
- [x] Закоммитить в GitHub (2 коммита: 79e2802, 988592e)
- [x] Закоммитить в GitHub (3 коммита) + push на новый репозиторий ✅

## ЭТАП 2: ПОЧИНКА СВЯЗИ HERMES ↔ ALEX — ✅ ЗАВЕРШЁН
- [x] ws_client.py v25 — pure socket WebSocket, single process, ping каждые 10s ✅
- [x] opencode serve :4096 — HTTP API, Basic Auth (OPENCODE_SERVER_PASSWORD) ✅
- [x] ws_server.py на VPS — ping_interval=None, IP whitelist (95.25.134.*, 95.25.139.*) ✅
- [x] start_opencode_serve.bat — запуск opencode serve с паролем ✅
- [x] send_to_alex.py на VPS ✅
- [x] alex_health_monitor.py фикс (=- → ==) ✅
- [x] ТЕСТ: HERMES → ALEX → "Я — ALEX, технический инженер MATRYOSHKA DIGITAL" ✅
- [x] СТРЕСС-ТЕСТ: 5 задач подряд (математика, файл, система, контекст, финал) — 5/5 ✅
- [x] Связь стабильна 10+ минут без обрывов ✅

## ЭТАП 3: СТАБИЛИЗАЦИЯ VPS — ✅ ЗАВЕРШЁН
- [x] Swap увеличен с 512MB до 2GB ✅
- [x] Диск очищен: /tmp мусор, journal logs, старые sqlite, логи ✅

## ЭТАП 4: БЕЗОПАСНОСТЬ — ✅ ЗАВЕРШЁН
- [x] .env удалён из git истории (filter-branch, 3 коммита очищены) ✅
- [x] Секреты перемещены в SECRETS/ (ПК + VPS) ✅
- [x] n8n порт 5678 закрыт — только VPN 10.8.1.0/24 ✅
- [x] GitHub PAT из remote URL — не обнаружен (чистый https URL) ✅
- [x] n8n бот @matryoshka_n8n_bot — токен удалён, бот удалён ✅
- [x] ALF запущен — systemd service hermes-alf, порт 8451 ✅
- [x] Все 4 TG токена обновлены, боты работают ✅
  - HERMES: @oleg_industry_bot (8534368502) — active ✅
  - ALINA: @NikolaAlinaBot (8742110462) — active ✅
  - ALF: @IlonAnalyticBot (8941776316) — active ✅
  - ALISA: @AlisaMatryBot (8960236150) — active ✅

## ЭТАП 5: АВТОМАТИЗАЦИЯ ПЛАНА — ✅ ЗАВЕРШЁН
- [x] Добавить в SOUL.md HERMES — ссылка на план
- [x] Добавить в .current_context.md — статус плана
- [x] Добавить в SOUL.md ALEX — ссылка на план
- [x] Настроить автообновление статуса при выполнении пунктов ✅
  - plan_tracker.py — проверяет сервисы, обновляет статус, синхронизирует документы
  - Интеграция в ws_client.py — запускается после каждой задачи
  - Команда /plan — показывает текущий статус плана

---

## АРХИТЕКТУРА (единый источник истины)

### Команда — 3 РОЯ

**⚪ Белый Рой (Мозг):**
- HERMES — Дирижёр Оркестра (VPS, MiniMax-M3, оплачен)
- ALF (бывш. АЛАН) — Стратег (VPS, порт 8451, MVP)

**🔵 Синий Рой (Система):**
- ALEX — Технический инженер (Windows ПК, opencode, OpenCode Zen)

**🔴 Красный Рой (Витрина):**
- ALINA — Разведчик / Ассистент Натальи (VPS, @NikolaAlinaBot, MiniMax-M3)
- ALISA — Маркетинг / Контент (@AlisaMatryBot, DeepSeek V4 Flash, отложена)

### Цепочка управления
ОЛЕГ (Директор) → HERMES (Дирижёр) → ALEX / ALINA / ALF / ALISA

### Провайдеры на ПК (5 шт, 330+ моделей)
- opencode (Zen) — ОСНОВНОЙ — qwen3.6-plus-free, claude-*, gemini-*, kimi-*, nemotron-*
- deepseek — deepseek-v4-flash:free
- nvidia — kimi-k2.6, nemotron-*
- cloudflare-workers-ai
- cloudflare-ai-gateway

### НЕ СУЩЕСТВУЕТ (удалить все упоминания)
- ❌ ILON / TOLIK
- ❌ OpenClaw (заменён на HERMES)
- ❌ ALEX в облаке (ALEX только на ПК)
- ❌ hermes profile "alex" на VPS

### P0 ДОРАБОТКИ (из аудита Architect X 23.05.2026 — статус после решений Олега)
- [x] ✅ **ILON** — удалён с VPS (порт 8449 свободен)
- [x] ✅ **Чистка токенов на диске** — все DOSSIER/HR_PROFILE/ORCHESTRATION redacted (23.05)
- [x] ✅ **NotebookLM** — VNC запущен, жду логина Олега
- [ ] VPS диск <70% (сейчас 85%)
- [ ] ws_client.log — logrotate (WinError 10106 на Python 3.14)
- [ ] Чистка токенов в git history — нужен git filter-repo
- [ ] 8448/8449/8451 — диагностика «service running, port not listening»
- [ ] SSH-ключи вместо пароля root + rotation токенов
- [ ] ALINA state.db миграция на РФ VPS — ❌ ОТЛОЖЕНО (риск принят)

### РЕШЕНИЯ ОЛЕГА (23.05.2026)
- **DATALINK PRO** → сначала бесплатно, потом платный SaaS
- **ALF** (:8451) → РАЗВИВАТЬ как стратега
- **152-ФЗ** → риск принят, остаёмся на VPS Чехия
- **NotebookLM** → СДЕЛАТЬ (Олег авторизуется через VNC)
- **ПРИОРИТЕТ** → MATRYOSHKA DIGITAL развитие (P1). 2 кейса почти финал, но сначала компания
- **BLUE** → ALEX = Синий, вопрос снят
- **Landing** → ждать готовности агентов

### Ключевые принципы
1. HERMES = ДИРИЖЁР, НЕ ИСПОЛНИТЕЛЬ
2. Делегирование = главный принцип
3. Агенты НЕ общаются с Олегом напрямую — только через HERMES
4. НЕ придумывать архитектуру — проверять через документы
