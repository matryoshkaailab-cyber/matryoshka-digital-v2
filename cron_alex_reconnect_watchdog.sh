#!/bin/bash
# HERMES watchdog: детектит WS reconnect-loop Аликса
# Если за последние 30 мин было 5+ переподключений — алерт Олегу

LOG="/var/log/hermes_ws.log"
ALERT="/var/log/hermes_alex_reconnect_alert.log"

# Считаем ALEX registered за последние 30 мин
RECENT=$(grep "ALEX registered" "$LOG" 2>/dev/null | tail -20 | awk -F'T' '{print $1}' | awk -F']' '{print $1}' | tr -d '[')
NOW=$(date +%s)
COUNT=0
while IFS= read -r ts; do
    [ -z "$ts" ] && continue
    TS_EPOCH=$(date -d "$ts" +%s 2>/dev/null || echo 0)
    DIFF=$(( (NOW - TS_EPOCH) / 60 ))
    if [ $DIFF -lt 30 ]; then
        COUNT=$((COUNT + 1))
    fi
done <<< "$RECENT"

if [ $COUNT -ge 5 ]; then
    # Проверяем, не алертили ли мы в последний час
    if [ -f "$ALERT" ]; then
        LAST_ALERT=$(stat -c %Y "$ALERT" 2>/dev/null)
        LAST_DIFF=$(( (NOW - LAST_ALERT) / 60 ))
        if [ $LAST_DIFF -lt 60 ]; then
            exit 0
        fi
    fi
    echo "[$(date)] ALERT: $COUNT reconnects in 30 min" >> "$ALERT"
    curl -s "http://localhost:8450/api/send" -X POST \
      -H "Content-Type: application/json" \
      -d "{\"message\":\"⚠️ Аликс reconnect-loop: $COUNT переподключений за 30 мин. Открой на ПК Task Manager → Services → AlexStack → Restart.\"}" >/dev/null 2>&1
fi
