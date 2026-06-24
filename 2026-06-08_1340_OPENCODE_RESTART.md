# 🔄 RESTART OPENCODE — инструкция (по скиллу alex-connection)

_Обновлено: 2026-06-08 13:40_

**HERMES обнаружил**: WS канал работает (`/var/log/hermes_ws.log` показывает `Task result ... [ERROR] Timeout`). Opencode на ПК упал.

## ЧТО ДЕЛАТЬ (по скиллу `alex-connection`)

### Быстрый вариант (1 мин):
1. **Двойной клик** на `C:\matryoshka\RESTART_ALEX.bat`
2. Подожди 30 сек
3. Проверь: `curl http://127.0.0.1:5001/session` → должен вернуть `[]`

### Ручной вариант (8 шагов из ALEX_RESTART_INSTRUCTIONS.md):
```powershell
taskkill /F /IM opencode.exe
Start-Sleep 5
start /min "" "C:\Users\User\AppData\Roaming\npm\node_modules\opencode-ai\bin\opencode.exe" serve --port 5001
Start-Sleep 10
start /min cmd /c "C:\matryoshka\ws_client.bat"
curl http://127.0.0.1:5001/session
curl http://127.0.0.1:4000/health
```

## КАК ПОДТВЕРДИТЬ ЧТО СВЯЗЬ ВОССТАНОВЛЕНА

На VPS проверь:
```bash
tail -3 /var/log/hermes_ws.log
# Должен появиться "Task result: api_xxx → ok" (без Timeout)
```

## ЕСЛИ НЕ ПОМОГЛО

Положи файл `/root/matryoshka/alex_tasks/2026-06-08_1340_STATUS.md` с тем что видишь. HERMES прочтёт через cron `*/2 * * * * /root/matryoshka/cron_check_alex.sh` и пришлёт уведомление Олегу.

## ИСТОЧНИК

Диагноз по скиллу: `/root/.hermes/profiles/hermes-cli/skills/matryoshka/alex-connection/references/ws-log-diagnosis-opencode-down.md`

— HERMES
