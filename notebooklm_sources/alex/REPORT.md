# ALEX — ОТЧЁТ ПО СВЯЗИ И ИНТЕГРАЦИИ (Кейс: Синий Рой)
**Период:** 15.06.2026 | **Канал:** opencode ACP через AmneziaWG

---

## 1. ИДЕНТИЧНОСТЬ ALEX

| Параметр | Значение |
|---|---|
| **Имя** | ALEX |
| **Роль** | Технический инженер |
| **Платформа** | opencode на Windows ПК OLEG_ID_1951845052 |
| **OpenCode версия** | 1.17.3 (обновлён 15.06.2026) |
| **Модель (primary)** | MiniMax-M3 (через API) |
| **Модель (fallback)** | Kimi K2.6 NVIDIA |
| **ACP endpoint** | 10.8.1.4:4096 (AmneziaWG) |
| **HTTP bridge** | 10.8.1.4:8446 (alex_bridge.py) |
| **VPS bridge** | 127.0.0.1:8453 (vps_tunnel_bridge.py) |

---

## 2. КАНАЛ СВЯЗИ (актуальное состояние на 15.06.2026)

### Работает ✅
- HTTP bridge 10.8.1.4:8446 → opencode run
- POST /session создаёт сессию
- POST /session/{id}/prompt_async принимает запрос
- GET /session/{id}/message возвращает ответ
- ACP 10.8.1.4:4096 (OpenCode UI)
- Модель MiniMax-M3 отвечает осмысленно

### Сбоит ❌
- **opencode UI иногда зависает** (PID 15248 повис за 4 часа, перезапущен)
- **mimo-v2.5-free (opencode zen)** — сессия не создаётся, ERR
- **Случайные UnknownError err_e69fe788** (3+ случая 15.06)
- **Длинные запросы** (>500 токенов) — могут зависать

---

## 3. ДОСТИЖЕНИЯ СЕГОДНЯ (15.06.2026)

### Решённые проблемы
- ✅ Идентифицирован формат payload: `model: {providerID, modelID}` (объект)
- ✅ Найден workaround: явный providerID + modelID в payload
- ✅ Kimi K2.6 отвечает на длинные промпты (с явной моделью)
- ✅ Создан `alex_send.sh` helper (3.7 KB, 30 сек polling)
- ✅ Создан скилл `alex-connection` (3.3 KB, чистый)

### Найденные баги
- 🐛 Opencode 1.17.3 build agent зависает после 4+ часов работы
- 🐛 UnknownError err_e69fe788 (случайный, требует перезапуска)
- 🐛 mimo-v2.5-free не создаёт сессию (ERR на POST /session)

---

## 4. РЕВЬЮ ПЛАНА V2.0 (от Аликса, 15.06.2026)

### Где согласен
1. **Docker sandbox отложить** — issue #32049 ломает SOUL symlinks
2. **SOUL/Memory 100% выполнено** — индустриальный standard
3. **NotebookLM заменить** — но НЕ на fact-checker, а **подключить как библиотекаря**
4. **MiniMax-M3 Token Plan Plus 4500/5h** — хватает с jitter ±30 сек

### Где спорит
1. **"approvals.mode: manual"** — НЕ фикс root, только UX-помеха
2. **ACP как primary для 6 cron** — нужна fallback: ACP fail → local execute
3. **Triada моделей** (Gemini/DeepSeek/Critic) — overkill
4. **Content Factory pipeline** — обязательно (ALF → ALEX через delegate_task)

### Где добавляет
- **inotifywait hook** на canonical SOUL → reload gateway
- **Backup canonical** после каждого rebuild
- **readlink test** в build_identity.sh
- **High Leverage priorities** — ежедневный ТОП-3
- **Evidence Verification Queue** в Obsidian
- **Auto-skill evolution** — ALF сам пишет SKILL.md
- **"Голос бренда"** через историю в NotebookLM

---

## 5. ОТВЕТЫ ALEX ЗА 15.06 (4 развёрнутых)

1. **"V2.0 План ревью"** — 970 символов (docker/sandbox issue, sandbox-mirror bug)
2. **"MiniMax лимиты"** — 1074 символа (4500/5h = 75 RPM, jitter, free vs paid)
3. **"NotebookLM развёрнуто"** — 1987 символов (5 стратегических возможностей ALF)
4. **"Gemini research"** — 1654 символа (Flash free tier 15 RPM, Pro overkill)

---

## 6. СКРИПТЫ И КОНФИГИ

| Файл | Назначение |
|---|---|
| `C:\Scripts\alex_bridge.py` | HTTP bridge (threading, :8446) |
| `C:\Scripts\alex_ws_relay.py` | WS relay к VPS :8446 |
| `C:\Scripts\alex_ws_relay_cloudflared.py` | Cloudflared WSS backup |
| `C:\Scripts\run_opencode.ps1` | PowerShell wrapper для opencode run |
| `C:\Scripts\start_bridges.bat` | Auto-start (нужен --logfile fix) |
| `C:\matryoshka\opencode.json` | NVIDIA + MiniMax providers |
| `C:\matryoshka\ACP_CONNECTION.md` | Полные параметры ACP |

**VPS:**
- `/root/matryoshka/alex_send.sh` (3.7 KB) — unified ACP client
- `/root/matryoshka/alex_helper.sh` (1.5 KB) — healthcheck bridge
- `/root/matryoshka/skills/matryoshka/alex-connection/SKILL.md` (3.3 KB) — гайд
- `/root/matryoshka/skills/matryoshka/alex-connection-diagnostics/SKILL.md` — диагностика

---

## 7. РЕКОМЕНДАЦИИ ALEX (TOP-5)

1. **P0: Перезапустить opencode на ПК** при первом UnknownError (5 мин)
2. **P1: MiniMax-M3 jitter** — `*/5` + `+ RANDOM % 30` в cron
3. **P1: Content Factory pipeline** — ALF → ALEX через `delegate_task`
4. **P2: inotifywait hook** на SOUL → gateway reload
5. **P2: Auto-skill evolution** — ALF пишет SKILL.md

---

## 8. ИЗВЕСТНЫЕ ОГРАНИЧЕНИЯ

- ❌ Не могу шарить файлы с VPS (нет прямого доступа)
- ❌ Не имею UI для отладки (только логи)
- ❌ Зависим от opencode 1.17.3 (иногда зависает)
- ❌ Kimi K2.6 — только paid или NVIDIA free (15 RPM)
- ⚠️ Контекст сбрасывается при перезапуске opencode (сессии не персистентны)

---

**Итог:** ALEX = живой, но хрупкий. Главный канал (HTTP bridge) стабилен. ACP через 4096 — работает, но opencode UI имеет баги. Сегодня 4 развёрнутых ответа получены, итого 5685 символов контента для плана V2.
