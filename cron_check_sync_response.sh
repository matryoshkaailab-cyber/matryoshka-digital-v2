#!/bin/bash
# Мониторинг ответа от Аликса на SYNC_20260609_1330
RESPONSE_FILE="/root/matryoshka/alex_tasks/SYNC_RESPONSE_20260609_1330.md"
TASK_FILE="/root/matryoshka/alex_tasks/SYNC_20260609_1330.md"
FLAG="/tmp/sync_20260609_1330_alex_responded"

if [ -f "$RESPONSE_FILE" ] && [ ! -f "$FLAG" ]; then
  SIZE=$(stat -c%s "$RESPONSE_FILE")
  if [ "$SIZE" -gt 200 ]; then
    TOK=$(grep TELEGRAM_BOT_TOKEN /root/.hermes/.env | head -1 | cut -d= -f2)
    OLEG_ID="1951845052"
    curl -s -X POST "https://api.telegram.org/bot${TOK}/sendMessage" \
      -d "chat_id=${OLEG_ID}" \
      --data-urlencode "text=✅ Аликс ответил на SYNC_20260609_1330! Файл: ${RESPONSE_FILE} (${SIZE} байт). HERMES начинает сравнение." \
      >/dev/null
    touch "$FLAG"
  fi
fi
