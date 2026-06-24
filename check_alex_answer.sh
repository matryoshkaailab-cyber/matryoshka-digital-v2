#!/bin/bash
# Cron-check: if Alex answered, send to Telegram (one-shot via flag)
TASK=/root/matryoshka/alex_tasks/2026-06-08_1205_audit_fixes.md
TOK=$(grep "^TELEGRAM_BOT_TOKEN=*** /root/.hermes/.env | cut -d= -f2)
OLEG=1951845052
SENT_FLAG=/tmp/alex_answer_sent_1205

if [ -f "$TASK" ] && [ ! -f "$SENT_FLAG" ]; then
  SIZE=$(stat -c%s "$TASK")
  if [ "$SIZE" -gt 100 ]; then
    echo "[$(date)] Alex answered" > "$SENT_FLAG"
    curl -s -X POST "https://api.telegram.org/bot${TOK}/sendMessage" \
      -d "chat_id=${OLEG}" \
      --data-urlencode "text=ALEX ANSWERED audit task. File: $TASK Size: $SIZE bytes" \
      >/dev/null
    curl -s -X POST "https://api.telegram.org/bot${TOK}/sendDocument" \
      -F "chat_id=${OLEG}" \
      -F "document=@${TASK}" >/dev/null
    cat "$TASK" | head -80
    exit 0
  fi
fi
exit 0
