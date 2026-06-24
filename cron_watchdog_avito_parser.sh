#!/bin/bash
# HERMES watchdog: проверяет статус задачи avito_parser (отправлена 09.06 23:35)
# Если Аликс не отвечает 12+ часов — алерт Олегу в Telegram

TASK_DIR="/root/matryoshka/alex_tasks"
INBOX="$TASK_DIR/inbox/2026-06-09_2335_AVITO_PARSER.md"
OUTBOX="$TASK_DIR/outbox"
STATUS_DIR="$OUTBOX/2026-06-09_avito_parser"
ALERT_LOG="/var/log/hermes_avito_watchdog.log"

mkdir -p "$OUTBOX" "$STATUS_DIR"

# 1. Задача всё ещё в inbox? (Аликс не взял)
if [ -f "$INBOX" ]; then
    AGE_HOURS=$(( ($(date +%s) - $(stat -c %Y "$INBOX")) / 3600 ))
    if [ $AGE_HOURS -gt 12 ]; then
        echo "[$(date)] ALERT: avito_parser task unclaimed for ${AGE_HOURS}h" >> "$ALERT_LOG"
        curl -s "http://localhost:8450/api/send" -X POST \
          -H "Content-Type: application/json" \
          -d "{\"message\":\"⚠️ Аликс не взял задачу avito_parser уже ${AGE_HOURS}ч. Надо напомнить или взять самому.\"}" >/dev/null 2>&1
    fi
fi

# 2. Есть свежий статус? (Аликс работает)
LATEST_STATUS=$(ls -t "$STATUS_DIR"/STATUS_*.md 2>/dev/null | head -1)
if [ -n "$LATEST_STATUS" ]; then
    AGE_HOURS=$(( ($(date +%s) - $(stat -c %Y "$LATEST_STATUS")) / 3600 ))
    if [ $AGE_HOURS -gt 24 ]; then
        echo "[$(date)] WARN: avito_parser no status update for ${AGE_HOURS}h" >> "$ALERT_LOG"
    fi
fi

# 3. Avito_parser готов? (файлы на месте)
if [ -f "$STATUS_DIR/DONE.md" ]; then
    exit 0  # всё готово, молчим
fi
