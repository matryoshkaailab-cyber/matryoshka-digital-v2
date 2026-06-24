#!/bin/bash
# Мониторинг Аликса (opencode на ПК Олега) — AmneziaWG → 10.8.1.4:4096
# Старый канал (Tailscale) УБИТ 14.06.2026 — выпилен из кода полностью.
# Кред берём из alex_helper.sh (single source of truth).

LOG=/var/log/alex-monitor.log
ALEX_STATUS_FILE=/tmp/alex_current_status
ALERT=/usr/local/lib/hermes-agent/venv/bin/python3
ALERT_SCRIPT=/root/matryoshka/send_alert.py

ping_alert() {
    "$ALERT" "$ALERT_SCRIPT" "$1" 2>/dev/null || echo "alert failed: $1" >> $LOG
}

prev() { cat "$ALEX_STATUS_FILE" 2>/dev/null; }

# 1) Реальная проверка: awg0 поднят И на нём есть 10.8.x адрес
AWG_ADDR=$(ip -4 -o addr show dev awg0 2>/dev/null | awk '{print $4}' | head -1)
if [ -z "$AWG_ADDR" ]; then
    P=$(prev)
    [ "$P" != "VPN_DOWN" ] && [ -n "$P" ] && ping_alert "🟡 VPN down (awg0 без IP) — связь с Аликсом потеряна ($(date '+%H:%M:%S'))"
    echo "$(date '+%Y-%m-%d %H:%M:%S') ALEX=VPN_DOWN (no addr on awg0)" >> $LOG
    echo "VPN_DOWN" > $ALEX_STATUS_FILE
    exit 0
fi
AWG_STATE=$(cat /sys/class/net/awg0/operstate 2>/dev/null)
# AmneziaWG часто пишет operstate=unknown при живом линке — это нормально.
# Реальный критерий — есть IP и пакеты ходят.

# 2) Кред берём из единого источника
if [ ! -r /root/matryoshka/alex_helper.sh ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ALEX=ERROR (alex_helper.sh missing)" >> $LOG
    exit 1
fi
. /root/matryoshka/alex_helper.sh
# Теперь: $ALEX_HOST $ALEX_PORT $ALEX_USER $ALEX_PASS

# 3) POST /session → {"id":"ses_..."}
RESP=$(curl -sS -m 5 -u "${ALEX_USER}:${ALEX_PASS}" \
    -X POST "http://${ALEX_HOST}:${ALEX_PORT}/session" \
    -H "Content-Type: application/json" -d '{}' 2>/dev/null)

if echo "$RESP" | grep -q '"id":"ses_'; then
    STATUS="UP"
else
    STATUS="DOWN"
fi

P=$(prev)
SAFE_RESP=$(echo "$RESP" | sed 's/"id":"[^"]*"/"id":"<redacted>"/')
echo "$(date '+%Y-%m-%d %H:%M:%S') ALEX=$STATUS prev=$P awg_state=$AWG_STATE addr=$AWG_ADDR resp=${SAFE_RESP:0:100}" >> $LOG

if [ "$STATUS" != "$P" ] && [ -n "$P" ]; then
    if [ "$STATUS" = "DOWN" ]; then
        ping_alert "🔴 АЛИКС УПАЛ: POST /session не вернул id ($(date '+%H:%M:%S'))"
    else
        ping_alert "🟢 АЛИКС ВЕРНУЛСЯ: ${ALEX_HOST}:${ALEX_PORT} отвечает ($(date '+%H:%M:%S'))"
    fi
fi
echo "$STATUS" > $ALEX_STATUS_FILE
