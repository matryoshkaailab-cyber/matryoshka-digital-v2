#!/bin/bash
# alf_watchdog.sh v3 — Watchdog для ALF gateway (ALEX ACCEPTANCE 5 блокеров)
# Запускается через alf-watchdog.timer каждые 60 секунд
# 23.06.2026 — Фаза 1 ALF_ROLE_PROPOSAL + ALEX review fixes
# v3: timeout на каждую проверку + улучшенный alert

set -u

SERVICE="hermes-gateway-alf.service"
LOG="/var/log/matryoshka/alf_watchdog.log"
ALERT_LOG="/var/log/matryoshka/alf_alerts.log"
STATE_FILE="/var/log/matryoshka/alf_watchdog.state"
TELEGRAM_BOT_TOKEN=$(grep ^TELEGRAM_BOT_TOKEN= /root/.hermes/profiles/alf/.env | cut -d= -f2)
TELEGRAM_CHAT_ID="1951845052"
MEMORY_LIMIT_MB=1200
MAX_RESTARTS_PER_HOUR=5
STARTUP_GRACE_SEC=45
LOG_MAX_LINES=2000

# Per-check timeout (в секундах) — не даём одной проверке заблокировать всё
CHECK_TIMEOUT=10

mkdir -p "$(dirname "$LOG")"

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG"
}

alert_telegram() {
    local msg="$1"
    log "ALERT: $msg"
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] ALERT: $msg" >> "$ALERT_LOG"
    curl -sS --max-time "$CHECK_TIMEOUT" \
        -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=🚨 ALF WATCHDOG: ${msg}" \
        -d "parse_mode=HTML" \
        > /dev/null 2>&1 || log "telegram send failed (offline?)"
}

# Ротация лога
if [ -f "$LOG" ]; then
    lines=$(wc -l < "$LOG")
    if [ "$lines" -gt "$LOG_MAX_LINES" ]; then
        tail -n 1000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
        log "log rotated (was $lines lines, kept 1000)"
    fi
fi

# Self-monitor timestamp
date +%s > "$STATE_FILE"

# LOCK: защита от concurrent запусков
LOCKFILE="/var/lock/alf_watchdog.lock"
exec 9>"$LOCKFILE"
if ! flock -n 9; then
    log "another watchdog instance running, exit"
    exit 0
fi

# Установить trap для cleanup lockfile на exit
trap "rm -f $LOCKFILE" EXIT

# Helper: проверка с timeout
check_with_timeout() {
    local cmd="$1"
    timeout "$CHECK_TIMEOUT" bash -c "$cmd" 2>/dev/null
    return $?
}

# 0. Startup grace period
active_since_epoch=$(systemctl show "$SERVICE" --property=ActiveEnterTimestampMonotonic --value 2>/dev/null | tr -d ' ')
if [ -n "$active_since_epoch" ] && [ "$active_since_epoch" -gt 0 ]; then
    now_monotonic=$(awk '{print int($1 * 1000000)}' /proc/uptime)
    age_sec=$(( (now_monotonic - active_since_epoch) / 1000000 ))
    if [ "$age_sec" -lt "$STARTUP_GRACE_SEC" ]; then
        log "ALF started ${age_sec}s ago — grace period (${STARTUP_GRACE_SEC}s)"
        exit 0
    fi
fi

# 1. systemd status
status=$(check_with_timeout "systemctl is-active $SERVICE")
if [ "$status" != "active" ]; then
    log "ALF not active (status=$status) — restart"
    alert_telegram "ALF inactive (status=$status) — restarting"
    systemctl restart "$SERVICE"
    sleep 5
    new_status=$(check_with_timeout "systemctl is-active $SERVICE")
    log "after restart: $new_status"
    exit 0
fi

# 2. PID + memory
PID=$(check_with_timeout "systemctl show $SERVICE --property=MainPID --value")
if [ -z "$PID" ] || [ "$PID" = "0" ]; then
    log "ALF PID not found"
    exit 0
fi

MEMORY_KB=$(check_with_timeout "ps -p $PID -o rss=" | tr -d ' ')
MEMORY_MB=$((MEMORY_KB / 1024))
log "ALF PID=$PID memory=${MEMORY_MB}MB"

# 3. OOM killer (1h window, НЕ вечный trigger)
if check_with_timeout "dmesg --since='1 hour ago'" | grep -qiE "killed process.*(python|alf)|invoked oom-killer"; then
    alert_telegram "OOM killer сработал (последний час) — restart ALF (PID=$PID)"
    log "OOM killer detected (1h window) — restart"
    systemctl restart "$SERVICE"
    exit 0
fi

# 4. Memory limit
if [ "$MEMORY_MB" -gt "$MEMORY_LIMIT_MB" ]; then
    log "memory ${MEMORY_MB}MB > ${MEMORY_LIMIT_MB}MB — graceful restart"
    alert_telegram "memory ${MEMORY_MB}MB превысила лимит ${MEMORY_LIMIT_MB}MB — graceful restart"
    systemctl restart "$SERVICE"
    exit 0
fi

# 5. Telegram rate-limit detection
if check_with_timeout "journalctl -u $SERVICE --since '5 min ago' --no-pager" | grep -qiE "429|Too Many Requests|RetryAfter|retry after"; then
    alert_telegram "ALF rate-limited by Telegram API (429 в последние 5 мин)"
    log "Telegram rate-limit detected"
fi

# 6. Zombies
zombie_raw=$(check_with_timeout "ps --ppid $PID -o stat=" | grep -c "Z" 2>/dev/null || true)
zombie_count=${zombie_raw:-0}
zombie_count=$(echo "$zombie_count" | head -1 | tr -dc '0-9')
if [ -n "$zombie_count" ] && [ "$zombie_count" -gt 0 ] 2>/dev/null; then
    alert_telegram "ALF has ${zombie_count} zombie child process(es)"
    log "${zombie_count} zombies detected"
fi

# 7. Disk space
disk_free=$(check_with_timeout "df $(dirname $LOG) --output=pcent" | tail -1 | tr -d ' %\n' | head -1)
if [ -n "$disk_free" ] && [ "$disk_free" -gt 90 ] 2>/dev/null; then
    alert_telegram "Диск /var/log/matryoshka заполнен на ${disk_free}%"
    log "disk ${disk_free}% full"
fi

# 8. Restart-loop protection
# Считаем ТОЛЬКО реальные restart события (не ручные watchdog вызовы)
HOUR_AGO=$(date -u -d '1 hour ago' +%Y-%m-%dT%H 2>/dev/null || echo "")
if [ -n "$HOUR_AGO" ]; then
    # Считаем "RESTART" и "not active" записи (реальные рестарты), не "ALF OK"
    restarts_count=$(grep -E "RESTART|not active|killed process|memory.*MB.*MB" "$LOG" 2>/dev/null | grep -c "$HOUR_AGO" 2>/dev/null || echo 0)
else
    restarts_count=0
fi
restarts_last_hour=$(echo "${restarts_count:-0}" | head -1 | tr -dc '0-9')
restarts_last_hour=${restarts_last_hour:-0}
if [ "$restarts_last_hour" -gt "$MAX_RESTARTS_PER_HOUR" ] 2>/dev/null; then
    alert_telegram "ALF restart-loop detected ($restarts_last_hour за час) — manual intervention needed"
    log "RESTART LOOP — manual intervention needed"
    exit 1
fi

log "ALF OK (PID=$PID, mem=${MEMORY_MB}MB)"
exit 0