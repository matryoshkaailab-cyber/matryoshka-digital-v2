# Параметры связи Hermes ↔ ALEX (Windows ПК Олега)

**Обновлено:** 2026-06-15 01:16 UTC
**Версия:** v2.0 (полный rewrite)
**Источник истины:** Windows `C:\matryoshka\ACP_CONNECTION.md` + skill `acp-alex-connection`
**VPS-копия:** `/root/matryoshka/ACP_CONNECTION.md` (этот файл)

---

## ⚠️ ГЛАВНОЕ: КАНАЛ ТОЛЬКО ОДИН

```
Hermes (VPS)  ──HTTP/ACP──►  opencode 1.17.3 (ПК Олега)
       │                            10.8.1.4:4096
       └── AmneziaWG tunnel (awg0) ─┘
```

**Никаких WS-релеев, HTTP-бриджей, Cloudflared fallback'ов, SSH-туннелей — НЕТ и НЕ ДОЛЖНО БЫТЬ.**
Это не откат, не backup, не "на всякий случай" — это УБРАНО окончательно 15.06.2026.

---

## 🟢 ТЕКУЩАЯ АРХИТЕКТУРА (одна)

| Компонент | Значение |
|---|---|
| URL | `http://10.8.1.4:4096` |
| Username | `opencode` |
| Password | `0796731b-ed11-4f37-b1fb-3a1773fc825f` |
| Auth type | Basic |
| Protocol | Agent Client Protocol (ACP) HTTP |
| opencode version | 1.17.3 |
| Mode | **build** (все tools: bash, read, edit, write, glob, grep, webfetch, task) |
| CWD на ПК | `C:\matryoshka` |
| Транспорт | AmneziaWG (awg0 на VPS, IP `10.8.1.x/24`) |
| Мониторинг | NSSM AlexStack на ПК (рестартит при падении) |
| Автозапуск ПК | `C:\Scripts\start_acp_server.bat` + ярлык в Windows Startup |

**Правильный endpoint для отправки задачи (opencode 1.17.3):**
```bash
# 1. Создать сессию
curl -u "opencode:0796731b-ed11-4f37-b1fb-3a1773fc825f" \
  -X POST http://10.8.1.4:4096/session \
  -H "Content-Type: application/json" -d '{}'

# 2. Отправить задачу (async, 204 No Content = задача в очереди)
curl -u "opencode:0796731b-ed11-4f37-b1fb-3a1773fc825f" \
  -X POST "http://10.8.1.4:4096/session/<SESSION_ID>/prompt_async" \
  -H "Content-Type: application/json" \
  -d '{"parts":[{"type":"text","text":"<задача>"}]}'
```

> ⚠️ **`/message` НЕ работает в 1.17.x** (старая документация opencode ≤ 1.16). Использовать **только** `/prompt_async`.
> ⚠️ **`GET /session/<id>/messages` возвращает HTML** web-интерфейса opencode, не JSON. Для чтения результата async — websocket stream или polling на корректный messages API (см. skill `acp-alex-connection` п.15).

---

## ⛔ АРХИВ (отключено 15.06.2026 — НЕ ВОССТАНАВЛИВАТЬ)

С 15.06.2026 эти каналы **полностью выпилены**. Ниже — для истории, чтобы через год не возникало "а давай вернём".

| Канал | Статус | Почему убрано |
|---|---|---|
| WebSocket Relay VPS:8446 (`ws_server.py`) | ❌ OFF, `hermes-ws.service` masked | 95+ WS-соединений, watchdog-loop, think-only ответы, месяц мучений |
| HTTP Bridge VPS:8446 (`alex-bridge.py`) | ❌ OFF, `alex-bridge.service` masked | Дублировал WS Relay, не давал выигрыша, плодил PID'ы |
| Heartbeat (`alex-heartbeat.service`) | ❌ OFF, masked | Мёртвый watchdog, который и рестартил то, что не должно подниматься |
| Monitor (`alex-monitor.service` + `.timer`) | ❌ OFF, masked + timer masked | Зацикливал рестарт ws_server (RestartSec=5 секунд), обход `ln -sf /dev/null` |
| Health (`alex-health.service`) | ❌ OFF, disabled | Дублировал мониторинг, смысла нет |
| Cloudflared tunnel (FALLBACK) | ❌ OFF, не используется | Сквозной доступ в обход VPN — нарушение политики безопасности |
| Cron watchdog'ы (7 шт) | ❌ УДАЛЕНЫ из crontab | Держали мёртвые каналы живыми |
| `delegate_task(acp_command="opencode")` | ❌ НЕ РАБОТАЕТ | Hermes пытается стартовать GitHub Copilot CLI, нужен **прямой curl** |
| opencode на VPS | ❌ ЗАПРЕЩЕНО | 3 раза устанавливал, 3 раза зря, 7 сервисов упало |
| Tailscale | ❌ СНЁС | Без спроса ставил, нарушение мандата |

**Проверка реального состояния (2026-06-15 01:16 UTC):**
```bash
$ systemctl list-unit-files | grep -iE "(alex|hermes-ws)"
alex-bridge.service          masked
alex-health.service          disabled
alex-heartbeat.service       masked
alex-monitor.service         masked
hermes-ws.service            masked
alex-monitor.timer           masked

$ ss -tlnp | grep -E ":(8446|4096)"
(пусто)  # 8446 никто не слушает; 4096 — на ПК, не на VPS

$ crontab -l | grep -iE "(alex|hermes-ws|8446)"
(пусто)

$ ps -ef | grep -iE "(opencode|ws_server|alex-bridge|hermes-ws)"
(пусто)

$ ip -o link show awg0
3: awg0: <POINTOPOINT,NOARP,UP,LOWER_UP>  ← VPN tunnel жив
```

---

## 🩺 ДИАГНОСТИКА (если связь упала)

**Шаг 0 — ПЕРВЫМ ДЕЛОМ:** `skill_view('alex-connection-diagnostics')` — там готовый чеклист.

**Шаг 1 — Канал (AmneziaWG + TCP):**
```bash
ip -o link show awg0 | grep -q "UP" || sudo awg-quick up awg0
for ip in 10.8.1.{2..8}; do
  timeout 2 ping -c 1 -W 1 $ip 2>&1 | grep "from" | head -1
done
timeout 3 bash -c "echo '' > /dev/tcp/10.8.1.4/4096" && echo "TCP OPEN" || echo "TCP FAIL"
```

**Шаг 2 — ACP HTTP:**
```bash
curl -s --max-time 5 -u "opencode:0796731b-ed11-4f37-b1fb-3a1773fc825f" \
  -X POST http://10.8.1.4:4096/session \
  -H "Content-Type: application/json" -d '{}'
# Должен вернуть: {"id":"ses_...","version":"1.17.3","directory":"C:\\matryoshka"}
```

| Симптом | Причина | Действие |
|---|---|---|
| `awg0` DOWN | AmneziaWG сервис упал | `sudo awg-quick up awg0` |
| Ping до .4 fail, до .6 ОК | Аликс сменил IP в tunnel | grep `awg show` → обновить URL |
| TCP 4096 fail | opencode на ПК не запущен | Попросить Олега проверить NSSM AlexStack |
| TCP OK, /session fail | Сменились креды | **СПРОСИТЬ Олега** (не выдумывать новые) |
| HTTP 200 но HTML | GET попал в web-интерфейс, не API | Проверить POST `/session`, не GET `/` |

---

## 📂 СВЯЗАННЫЕ ФАЙЛЫ

| Путь | Назначение |
|---|---|
| Windows `C:\matryoshka\ACP_CONNECTION.md` | **SOURCE OF TRUTH** — оригинал |
| `/root/matryoshka/ACP_CONNECTION.md` | VPS-копия (этот файл) |
| `~/.hermes/profiles/hermes-cli/skills/matryoshka/acp-alex-connection/SKILL.md` | **АКТУАЛЬНАЯ ИНСТРУКЦИЯ** по работе с ACP (загружать первым делом) |
| `~/.hermes/profiles/hermes-cli/skills/hermes-ops/alex-connection-diagnostics/SKILL.md` | Чеклист диагностики |
| `/root/matryoshka/ALEX_CONNECTION_FINAL_AUDIT.md` | **АРХИВНЫЙ** отчёт по ws_client (больше не актуален) |
| `/root/matryoshka/OPENCODE_RESEARCH.md` | **АРХИВНЫЙ** ресёрч (до решения про ACP) |
| `/root/matryoshka/agents/alex/README.md` | Профиль Аликса |
| `/root/obsidian-vault/agents/ALEX_NOTES.md` | Старые заметки про bridge |
| `/root/matryoshka/alex_stack.py` | NSSM monitor (на ПК, не на VPS) |

---

## 🧠 ЧЕГО НЕ ДЕЛАТЬ (вбито после месяца пиздюлей)

1. ❌ НЕ устанавливать opencode на VPS
2. ❌ НЕ поднимать ws_server / ws_client / alex-bridge
3. ❌ НЕ создавать fallback-каналы (Cloudflared, SSH-туннель, второй VPN)
4. ❌ НЕ использовать `delegate_task(acp_command="opencode")` — это для Copilot CLI
5. ❌ НЕ использовать endpoint `/message` (только `/prompt_async` для 1.17.x)
6. ❌ НЕ отвечать "связь ОК" без 3 проверок (TCP + /session + ping)
7. ❌ НЕ "предполагать" или "генерировать" новые креды — спрашивать Олега
8. ❌ НЕ предлагать "план A/B/C/D" без конкретного действия
9. ✅ ПЕРВОЕ ДЕЙСТВИЕ = `skill_view('acp-alex-connection')` — там ответы на 90% вопросов

---

## 📝 ИСТОРИЯ ВЕРСИЙ

| Дата | Версия | Что |
|---|---|---|
| 2026-05..2026-06-07 | v0.x | ws_client / ws_server / 95+ WS-соединений, месяц мучений |
| 2026-06-08..11 | v1.0 | Попытки поставить opencode на VPS (3 раза зря) |
| 2026-06-12..13 | v1.5 | Переход на ACP, opencode 1.17.3 на ПК, skill создан |
| 2026-06-13 00:40 | v1.6 | Этот файл впервые создан (4 канала: PRIMARY/BACKUP/FALLBACK/MONITOR) |
| 2026-06-15 01:16 | **v2.0** | **Полный rewrite**: один канал ACP, остальные в АРХИВ, systemd masked, crontab пуст |
