# MATRYOSHKA DIGITAL — Архитектура агентов

## Команда — 3 РОЯ

### ⚪ Белый Рой (Мозг)
- **HERMES** — Дирижёр Оркестра (VPS, MiniMax-M2.7, оплачен)
- **ALF** (бывш. АЛАН) — Стратег (VPS, порт 8451, MVP)

### 🔵 Синий Рой (Система)
- **ALEX** — Технический инженер (Windows ПК OLEGа, opencode, OpenCode Zen)

### 🔴 Красный Рой (Витрина)
- **ALINA** (бывш. ECLER) — Подопытный бот для НИКОЛАЯ (VPS, @NikolaAlinaBot, MiniMax-M2.7, проект НИКОЛАЙ)
- **ALISA** — Маркетинг / Контент (@AlisaMatBot, DeepSeek V4 Flash, отложена)

### ❌ НЕ СУЩЕСТВУЕТ
- ECLER / Ecler / ecler — переименована в ALINA, передана НИКОЛАЮ 07.06.2026
- ILON / TOLIK — не существует
- OpenClaw — заменён на HERMES
- ALEX в облаке — ALEX только на ПК

## Цепочка управления
ОЛЕГ (Директор, @OLEG_USER, ID: 1951845052) → HERMES (Дирижёр, VPS) → ALEX / ALINA / ALF / ALISA

## Инфраструктура
- VPS: 85.137.166.209 (root/Jktu22051987) — Чехия, SmartApe
- ALEX: opencode на Windows ПК OLEGа (ACP-канал)
- Связь: Telegram → HERMES → **opencode ACP :10.8.1.4:4096** → ALEX (ЕДИНСТВЕННЫЙ канал)
- ~~Старый канал ws_server:8446 + alex-bridge + 100.100.206.112:8446~~ — ОТКЛЮЧЕНЫ 15.06.2026
- Порты: 4096 (opencode ACP), 8448 (ALISA API), 5678 (n8n)
- Systemd: hermes-ws.service, alex-bridge.service, alex-heartbeat.service, alex-monitor.service — ВСЕ **masked** (не запустятся)
- Cron watchdog'и (cron_check_alex, alex_active_monitor, cron_check_alex_restart, cron_alex_reconnect, hermes_active_monitor, cron_check_sync_response, alex_smoke_test) — УДАЛЕНЫ из crontab

## Ключевые принципы
1. HERMES = ДИРИЖЁР, НЕ ИСПОЛНИТЕЛЬ
2. Делегирование = главный принцип
3. Агенты НЕ общаются с OLEGом напрямую — только через HERMES
4. НЕ придумывать архитектуру — проверять через документы

## Приоритетный план (P0)
Файл: /root/matryoshka/PRIORITY_PLAN.md
При каждом старте — проверять статус выполнения.
