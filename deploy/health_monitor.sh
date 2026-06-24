#!/bin/bash
# MATRYOSHKA Digital - Health Monitor
# Запускается каждый час через cron
# Шлёт алерт в Telegram если RAM>85% или Disk>80%

TELEGRAM_BOT_TOKEN="894177...RcSs"
ALERT_CHAT_ID="1951845052"

# Текущие значения
RAM_PCT=$(free | grep Mem | awk '{printf "%.0f", ($3/$2)*100}')
DISK_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

# Thresholds
RAM_THRESHOLD=85
DISK_THRESHOLD=80

# Check
ALERT=""
if [ "$RAM_PCT" -ge "$RAM_THRESHOLD" ]; then
  ALERT="${ALERT}🚨 RAM: ${RAM_PCT}% (порог ${RAM_THRESHOLD}%)\n"
fi
if [ "$DISK_PCT" -ge "$DISK_THRESHOLD" ]; then
  ALERT="${ALERT}💾 Disk: ${DISK_PCT}% (порог ${DISK_THRESHOLD}%)\n"
fi

# Send alert if needed
if [ -n "$ALERT" ]; then
  MSG="🚨 ALERT MATRYOSHKA @ $(date '+%Y-%m-%d %H:%M:%S')\n${ALERT}"
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${ALERT_CHAT_ID}" \
    -d "text=${MSG}" > /dev/null 2>&1
  echo "ALERT SENT: $MSG"
fi

