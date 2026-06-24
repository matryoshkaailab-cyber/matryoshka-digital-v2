
# Council #4 (Этап 2-3) — ФИКС ALF — 21.06.2026

**Тема:** ALF @IlonAnalyticBot не отвечает 5+ часов (с 20.06 22:42)

## УЧАСТНИКИ
- ✅ Аликс ИИ (deepseek-v4-flash-free, session=quiet-otter) — ОТВЕТИЛ
- ❌ ALF (Telegram + chat timeout) — МОЛЧИТ (предмет фикса)
- ✅ Hermes (дирижёр) — диагностика + synthesis

## ЭТАП 1: ОТВЕТ АЛИКСА ИИ (2208 chars JSON)

**Гипотеза:** 2 процесса ALF polling одновременно (alf-telegram.service + hermes-gateway-alf.service)
**Fix (8 шагов):** SSH → systemctl status → stop alf-telegram → restart gateway → install --replace → journalctl → getUpdates → test
**Риски:** alf-telegram.service может быть inactive (тогда hypothesis неверна)

## ЭТАП 2: VERIFY (live-check) — ГИПОТЕЗА АЛИКСА **НЕ ПОДТВЕРЖДЕНА**

**alf-telegram.service НЕ СУЩЕСТВУЕТ** (returncode=4, "Unit not found")

**НО! Альтернативная гипотеза:**

| Факт | Значение |
|------|----------|
| systemd WARNING в 03:02:45 | "TimeoutStopSec=90s < drain_timeout=180s (expected >=210s). systemd may SIGKILL gateway mid-drain" |
| 2 restart'а подряд (03:02:31, 03:02:52) | Оба "Deactivated successfully" + "Consumed 11.7s CPU" — НЕ graceful |
| Telegram conflict в 03:16:54 | "previous session still held open" — после рестарта polling |
| Текущий PID 3256365 (uptime ~1.5h) | gateway запущен 03:02:53, но polling висит с 03:16:54 |
| Telegram state в gateway_state.json | "connected" — TCP OK, polling ЗАСТРЯЛ |
| PID 3254688 (2 Telegram sockets) | **МОЙ** `hermes gateway run --profile hermes-cli` — НЕ конкурент |

## 🎯 РЕАЛЬНАЯ КОРНЕВАЯ ПРИЧИНА

**systemd unit stale (TimeoutStopSec=90s < drain_timeout=180s)**
↓
**systemd SIGKILL** при restart (не graceful shutdown)
↓
**Telegram polling сессия не закрыта** (long-poll getUpdates)
↓
**Следующий gateway polling = Conflict** (1/5 retry)
↓
**ALF бот висит в retry loop** 1+ час (03:16:54 — 04:30)

**Цепочка:**
```
20.06 22:42: Council 4 попытка переключить model → перезагрузка ALF
20.06 22:42: Первый restart → SIGKILL → polling не закрыт
20.06 22:42+: ALF пытается polling → Conflict
20.06 22:42 - 21.06 03:00: бот молчит (polling в retry loop)
21.06 03:00: ALF librarian v1.1 file-queue создан (alf-task watcher)
21.06 03:02: 2 restart подряд (SIGKILL × 2)
21.06 03:16: Telegram Conflict retry (1/5)
21.06 04:17: bridge отправил council2-stage1 → ALF polling видит сообщение, но response = timeout
21.06 04:30 (СЕЙЧАС): polling продолжает retry
```

**НЕ первопричина:** model timeout (Аликс упомянул "триггер первого рестарта" — но model это только триггер, не причина)
**НЕ первопричина:** alf-bridge.py (только sendMessage, не polling)
**НЕ первопричина:** 2 процесса (alf-telegram.service не существует)

## ЭТАП 3: SYNTHESIS — МИНИМАЛЬНЫЙ ФИКС (3 шага, 5 мин)

### ШАГ 1: Починить systemd unit (фикс TimeoutStopSec)
```bash
hermes gateway service install --replace
```
- Рекомендация из лога (line "Run `hermes gateway service install --replace`")
- TimeoutStopSec станет >= 210s
- Следующие restart'ы будут GRACEFUL → Telegram polling закроется корректно

### ШАГ 2: Restart ALF
```bash
systemctl restart hermes-gateway-alf.service
```
- Новый unit + чистый старт
- Telegram polling начнётся с offset=-1 (все апдейты)
- Если conflict — подождать 30 сек (Telegram expire)

### ШАГ 3: Тест
```bash
# Проверить polling OK
journalctl -u hermes-gateway-alf.service -n 30 | grep -i telegram
# Отправить тестовое сообщение через bridge
echo '{"task_id":"test-fix-001","question":"ping","from":"hermes"}' > /root/matryoshka/swarm/inbox/alf/test-fix-001.json
sleep 15
ls /root/matryoshka/swarm/outbox/alf/
```

## ДОПОЛНИТЕЛЬНО (опционально, через 1 день)

| # | Задача | Зачем |
|---|--------|-------|
| A | Сократить context_length=50000 (с 200000) | MiniMax-M3 может timeout'ить на длинных контекстах |
| B | Включить Exponential backoff для 429 | Council 2.0 P2, не критично сейчас |
| C | Watchdog: monitor ALF polling каждые 5 мин, alert если 0 updates > 30 мин | Предотвратить repeat |

## DISSENTING OPINIONS

- **Аликс ИИ:** hypothesis "2 процесса" — ❌ не подтвердилась
- **Hermes (я):** hypothesis "systemd SIGKILL → polling conflict" — ✅ подтвердилась логами
- **ALF:** нет ответа

## РЕШЕНИЕ (нуждается в одобрении Олега)
