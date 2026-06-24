# PRIORITY PLAN — MATRYOSHKA DIGITAL
# P0 — КРИТИЧЕСКИЙ | Создан: 2026-05-20

## СТАТУС: [ЭТАП 1 из 5 — В ПРОЦЕССЕ]

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
- [x] ws_client.py v15 → opencode serve :4096 → qwen3.6-plus-free (OpenCode Zen) ✅
- [x] Winsock reset + перезагрузка ✅
- [x] ScheduledTask автостарт ws_client.py ✅
- [x] start_opencode_serve.bat — запуск opencode serve с паролем ✅
- [x] ws_server.py на VPS — IP 95.25.139.65 разрешён ✅
- [x] send_to_alex.py на VPS ✅
- [x] alex_health_monitor.py фикс (=- → ==) ✅
- [x] ТЕСТ: HERMES → ALEX → "Я — ALEX, технический инженер MATRYOSHKA DIGITAL" ✅

## ЭТАП 3: СТАБИЛИЗАЦИЯ VPS
- [ ] Увеличить swap до 2GB
- [ ] Очистить диск (удалить backup_*, open-design, /tmp мусор)
- [ ] Починить ЭКЛЕР (TTS, image_gen, polling conflict)

## ЭТАП 4: БЕЗОПАСНОСТЬ
- [ ] Сменить 4 скомпрометированных TG токена
- [ ] Удалить .env из git истории
- [ ] Убрать GitHub PAT из remote URL
- [ ] Закрыть n8n порт 5678
- [ ] Переместить секреты в SECRETS/

## ЭТАП 5: АВТОМАТИЗАЦИЯ ПЛАНА — ✅ ЗАВЕРШЁН
- [x] Добавить в SOUL.md HERMES — ссылка на план
- [x] Добавить в .current_context.md — статус плана
- [x] Добавить в SOUL.md ALEX — ссылка на план
- [ ] Настроить автообновление статуса при выполнении пунктов

---

## АРХИТЕКТУРА (единый источник истины)

### Команда — 3 РОЯ

**⚪ Белый Рой (Мозг):**
- HERMES — Дирижёр Оркестра (VPS, MiniMax-M2.7, оплачен)
- ALF (бывш. АЛАН) — Стратег (VPS, порт 8451, MVP)

**🔵 Синий Рой (Система):**
- ALEX — Технический инженер (Windows ПК, opencode, OpenCode Zen)

**🔴 Красный Рой (Витрина):**
- ALISA — Маркетинг / Контент (@AlisaMatBot, DeepSeek V4 Flash, отложена)

### Цепочка управления
ОЛЕГ (Директор) → HERMES (Дирижёр) → ALEX / ALF / ALISA

> ⚠️ **ECLER НЕ СУЩЕСТВУЕТ** как агент (переименован в ALINA 07.06.2026, клиентский кейс Николая). НЕ путать с @ZarnyAlexaBot (помощник Натальи, контейнер `alexa_core` — это другой проект).

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

### Ключевые принципы
1. HERMES = ДИРИЖЁР, НЕ ИСПОЛНИТЕЛЬ
2. Делегирование = главный принцип
3. Агенты НЕ общаются с Олегом напрямую — только через HERMES
4. НЕ придумывать архитектуру — проверять через документы
