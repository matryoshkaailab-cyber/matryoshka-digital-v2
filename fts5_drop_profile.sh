#!/bin/bash
# FTS5 Drop — для hermes-cli profile state.db
# 15.06.2026 — повторяем на активной DB
set -e

DB="/root/.hermes/profiles/hermes-cli/state.db"
TS=$(date +%Y%m%d_%H%M%S)
LOG=/var/log/fts5_drop_profile.log

log() { echo "$(date '+%F %T') $1" | tee -a "$LOG"; }

log "=== FTS5 drop на profile DB: $DB ==="
log "Pre-state:"
SIZE_PRE=$(stat -c%s "$DB")
log "  size: ${SIZE_PRE} bytes"

# Бэкап
cp "$DB" "${DB}.bak.${TS}.pre-fts5"
cp "${DB}-shm" "${DB}-shm.bak.${TS}" 2>/dev/null || true
cp "${DB}-wal" "${DB}-wal.bak.${TS}" 2>/dev/null || true
log "Backup: ${DB}.bak.${TS}.pre-fts5"

# Стоп gateway если ещё не остановлен
if systemctl is-active --quiet hermes-cli-gateway 2>/dev/null; then
    log "Gateway is active. Will close DB via sqlite3 (online op)."
fi

# Список FTS таблиц
log "FTS5 tables before:"
sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE name LIKE '%fts%' ORDER BY name;" 2>&1 | tee -a "$LOG"

# DROP всех FTS объектов (включая триггеры)
for obj in $(sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE name LIKE '%fts%' ORDER BY name;" 2>/dev/null); do
    case "$obj" in
        *_insert|*_delete|*_update)
            log "DROP TRIGGER $obj"
            sqlite3 "$DB" "DROP TRIGGER IF EXISTS $obj;" 2>&1 | tee -a "$LOG"
            ;;
        *)
            log "DROP TABLE $obj"
            sqlite3 "$DB" "DROP TABLE IF EXISTS $obj;" 2>&1 | tee -a "$LOG"
            ;;
    esac
done

# Создание простого индекса
log "CREATE INDEX idx_messages_content"
sqlite3 "$DB" "CREATE INDEX IF NOT EXISTS idx_messages_content ON messages(content);" 2>&1 | tee -a "$LOG"

# Integrity
log "PRAGMA integrity_check:"
sqlite3 "$DB" "PRAGMA integrity_check;" 2>&1 | tee -a "$LOG"

# VACUUM
log "VACUUM:"
sqlite3 "$DB" "VACUUM;" 2>&1 | tee -a "$LOG"

# Тест LIKE
log "LIKE speed test:"
time sqlite3 "$DB" "SELECT COUNT(*) FROM messages WHERE content LIKE '%VPN%' ESCAPE '\\';" 2>&1 | tee -a "$LOG"

# Post-state
SIZE_POST=$(stat -c%s "$DB")
log "Post-state size: ${SIZE_POST} bytes (saved $((SIZE_PRE - SIZE_POST)) bytes)"
log "FTS5 tables after:"
sqlite3 "$DB" "SELECT COUNT(*) AS fts5_remaining FROM sqlite_master WHERE name LIKE '%fts%';" 2>&1 | tee -a "$LOG"
log "=== DONE ==="
