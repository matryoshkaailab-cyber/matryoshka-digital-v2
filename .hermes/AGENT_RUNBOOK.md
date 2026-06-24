# 🔧 AGENT RUNBOOK — как дёргать каждого агента

> **Когда нужно:** ALF/ALEX не отвечают, или нужно их пнуть
> **Кто делает:** HERMES (дирижёр)
> **Обновлено:** 2026-06-19 (после инцидента с ALF memory overflow)

## 1. Проверить что агент жив

```bash
# ALF (VPS)
systemctl is-active hermes-gateway-alf.service
ps -ef | grep "hermes.*alf" | grep -v grep
journalctl -u hermes-gateway-alf --no-pager -n 5

# ALEX (ПК Олега, через ACP)
curl -sS --max-time 5 -o /dev/null -w "%{http_code}" http://10.8.1.4:4096/health
curl -sS --max-time 5 http://10.8.1.4:4096/session?limit=1 | head -c 200
```

## 2. ALF застрял (memory overflow / loop)

**Симптом:** ALF gateway active, но не отвечает в Telegram >30 мин. Логи показывают "memory exceeds limit" warnings.

**Действия (по шагам):**
```bash
# Шаг 1: Проверить memory
sqlite3 /root/.hermes/profiles/alf/memory_store.db "SELECT * FROM memory;"

# Шаг 2: Рестартнуть gateway (ОСВОБОЖДАЕТ memory)
systemctl restart hermes-gateway-alf.service
sleep 2
systemctl is-active hermes-gateway-alf.service

# Шаг 3: Дождаться первого ответа ALF (10-30 сек)
tail -f /root/.hermes/profiles/alf/logs/agent.log

# Шаг 4: Если не отвечает — послать Telegram пинок
# Токен в /root/matryoshka/alf/.env (ALF_TG_TOKEN, ALF_OWNER_ID)
curl -sS -X POST "https://api.telegram.org/bot${ALF_TG_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{"chat_id": "${ALF_OWNER_ID}", "text": "ALF, ты нужен. Задача: ..."}"
```

## 3. ALEX не отвечает

**Симптом:** curl http://10.8.1.4:4096/session — работает, но POST /message — timeout.

**Действия:**
```bash
# Шаг 1: Создать новую сессию
SESSION=$(curl -sS -X POST http://10.8.1.4:4096/session -H 'Content-Type: application/json' -d '{}' | python3 -c "import sys,json;print(json.load(sys.stdin).get('id',''))")

# Шаг 2: Отправить prompt (с таймаутом 120s)
PROMPT=$(echo '...' | python3 -c "import json,sys;print(json.dumps({'model':{'providerID':'opencode','modelID':'deepseek-v4-flash-free'},'parts':[{'type':'text','text':sys.stdin.read()}]}))")
curl -sS --max-time 120 -X POST "http://10.8.1.4:4096/session/$SESSION/message" \
  -H "Content-Type: application/json" -d "$PROMPT" >/dev/null

# Шаг 3: Polling /message (singular! не /messages)
for i in 1 2 3 4 5 6; do
  sleep 10
  RESP=$(curl -sS --max-time 10 "http://10.8.1.4:4096/session/$SESSION/message")
  # Парсить assistant message с text
  echo "$RESP" | python3 -c "..."  # см. scripts/
done
```

## 4. ALEX и shared_brain

**Проблема:** ALEX не знает про shared_brain (у него устаревший SOUL.md на ПК).

**Решение:** В каждой задаче ALEX указывать путь явно:
```
В задаче указывать: "Прочти /root/matryoshka/shared_brain/DIGEST.md на VPS через SSH 
(если не можешь — попроси HERMES прочитать и переслать тебе)"
```

## 5. Watchdog (auto-restart при memory overflow)

```bash
cat > /etc/cron.d/agent_memory_watchdog <<'EOF'
*/5 * * * * root /opt/hermes-bin/check_memory.sh >> /var/log/agent_watchdog.log 2>&1
EOF

cat > /opt/hermes-bin/check_memory.sh <<'EOF'
#!/bin/bash
# Проверяет memory каждого агента
for profile in alf hermes-cli alina-prod; do
  size=$(stat -c %s /root/.hermes/profiles/$profile/memory_store.db 2>/dev/null || echo 0)
  # Hermes лимит 2500
  if [ "$size" -gt 3000 ]; then
    logger "WATCHDOG: $profile memory overflow ($size) — restarting gateway"
    systemctl restart hermes-gateway-$profile.service 2>/dev/null
  fi
done
EOF
chmod +x /opt/hermes-bin/check_memory.sh
```


## 6. ALEX — НЕ МОЖЕТ читать VPS-файлы

**Это ФАКТ (по ALEX 13:03):**
- ACP endpoint — это opencode web UI, не SSH
- WebDAV :8181 есть, но 401 без пароля
- SSH port 22 на VPS — DEAD
- ALEX не может сам прочитать `/root/matryoshka/shared_brain/DIGEST.md`

**Что это значит:**
- ALEX принимает решения на основе своих ЛОКАЛЬНЫХ .md (устаревших)
- Документы на ПК ≠ документы на VPS
- ALEX не знает про shared_brain (хотя он на VPS)

**Решение:**
В КАЖДОЙ задаче ALEX либо:
- (а) **Пересылать содержимое файла в prompt**: `cat /root/matryoshka/shared_brain/DIGEST.md | base64 | head -c 5000`
- (б) Делать задачу ТОЛЬКО с ПК-стороны (Windows, Docker, SSH на другие хосты)
- (в) Указать что задача не требует VPS-данных

## 7. Штатные ситуации (что делать СРАЗУ)

| Ситуация | Действие | Скрипт |
|---|---|---|
| ALF не отвечает >30 мин | `systemctl restart hermes-gateway-alf.service` | см. RUNBOOK §2 |
| ALF memory overflow | watchdog рестартит автоматически | `/opt/hermes-bin/check_memory.sh` |
| ALEX POST timeout | polling /message ещё 60 сек | см. RUNBOOK §3 |
| ALEX не знает про shared_brain | Переслать ему DIGEST.md в prompt | см. RUNBOOK §6 |
| HERMES сам застрял | НЕ рестартить gateway (убьёт сессию) | watchdog skip self |
