#!/bin/bash
# Cron-job 10 min: proverka statusa Aliksa, esli molchit - pinguem cherez /api/delegate
STATE_FILE=/tmp/alex_audit_monitor
TASK_SENT=1779897900   # 12:05:00 08.06
MAX_SILENT=900         # 15 min

# Esli uzhe otvetil - nichego ne delaem
if [ -f /root/matryoshka/alex_tasks/2026-06-08_1205_audit_fixes.md ]; then
  echo "$(date) Alex uzhe otvetil" > $STATE_FILE
  exit 0
fi

# Schitaem skolko molchit
NOW=$(date +%s)
SILENT=$((NOW - TASK_SENT))

if [ "$SILENT" -gt "$MAX_SILENT" ]; then
  # Esli net sent_flaga - shlem ping
  if [ ! -f "${STATE_FILE}.pinged" ]; then
    curl -s -X POST http://127.0.0.1:8450/api/delegate \
      -H "Content-Type: application/json" \
      -d "{\"command\":\"reminder\",\"text\":\"REMINDER: audit task 2026-06-08_1205_audit_fixes.md - ${SILENT}s tishiny. Otvechai.\"}" \
      > /tmp/ping_alex.log 2>&1
    touch "${STATE_FILE}.pinged"
    echo "$(date) Ping otpravlen, silent=${SILENT}s" > $STATE_FILE
  fi
fi

# Olega uvedomlyaem cherez 30 min
if [ "$SILENT" -gt 1800 ] && [ ! -f "${STATE_FILE}.warned" ]; then
  TOK=$(grep TELEGRAM_BOT_TOKEN /root/.hermes/.env | head -1 | cut -d= -f2)
  curl -s -X POST "https://api.telegram.org/bot${TOK}/sendMessage" \
    -d chat_id=1951845052 \
    --data-urlencode "text=ALEX MOLCHIT ${SILENT}s. Audit task ne poluchena. Mozhet ne u PK. Predlozhi: vzyat zadachu na sebya ili zhdat esche?" \
    > /tmp/warn_oleg.log 2>&1
  touch "${STATE_FILE}.warned"
  echo "$(date) Oleg warned, silent=${SILENT}s" > $STATE_FILE
fi
exit 0
