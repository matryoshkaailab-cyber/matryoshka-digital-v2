#!/bin/bash
# MATRYOSHKA Kanban Archiver
# Архивирует выполненные swarm_executor + hermes done задачи в Obsidian vault
# и удаляет из kanban.db (оставляет ~200-300 актуальных)
#
# Использование: ./archive_kanban.sh [--dry-run] [--days N]
#   --dry-run  - только показать что будет архивировано
#   --days N   - архивировать задачи старше N дней (default: 0 = все done)

set -e

DRY_RUN=false
DAYS=0
VAULT_DIR="/root/obsidian-vault"
ARCHIVE_DIR="$VAULT_DIR/agents/kanban_archive"
BACKUP_DIR="/root/matryoshka/backup"
DB="/root/.hermes/kanban.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/kanban_archive.log"

# Args
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --days) DAYS="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "=== Kanban Archive Run ==="
log "Mode: $([ "$DRY_RUN" = true ] && echo 'DRY-RUN' || echo 'REAL')"
log "Days filter: $DAYS"

# Создаём директории
mkdir -p "$ARCHIVE_DIR" "$BACKUP_DIR"

# 1. Бэкап БД
BACKUP_FILE="$BACKUP_DIR/kanban_pre_archive_${TIMESTAMP}.db"
if [ "$DRY_RUN" = false ]; then
  cp "$DB" "$BACKUP_FILE"
  log "Backup created: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | awk '{print $1}'))"
fi

# 2. Считаем сколько задач к архивации
COUNT_QUERY="SELECT COUNT(*) FROM tasks WHERE status IN ('done', 'archived') AND (assignee = 'swarm_executor' OR (assignee = 'hermes' AND status = 'done'))"
if [ "$DAYS" -gt 0 ]; then
  COUNT_QUERY="$COUNT_QUERY AND completed_at < strftime('%s', 'now', '-${DAYS} days')"
fi
COUNT=$(sqlite3 "$DB" "$COUNT_QUERY")
log "Tasks to archive: $COUNT"

# 3. Сколько останется
REMAIN=$(sqlite3 "$DB" "SELECT COUNT(*) FROM tasks WHERE NOT (status IN ('done', 'archived') AND (assignee = 'swarm_executor' OR (assignee = 'hermes' AND status = 'done')))")
log "Tasks remaining: $REMAIN"

if [ "$COUNT" -eq 0 ]; then
  log "Nothing to archive. Exiting."
  exit 0
fi

# 4. Dry-run: показать что будет
if [ "$DRY_RUN" = true ]; then
  log "DRY-RUN: Would export $COUNT tasks to $ARCHIVE_DIR/"
  sqlite3 "$DB" "SELECT id, assignee, status, datetime(created_at, 'unixepoch'), title FROM tasks WHERE status IN ('done', 'archived') AND (assignee = 'swarm_executor' OR (assignee = 'hermes' AND status = 'done')) LIMIT 5"
  exit 0
fi

# 5. Экспорт в Obsidian markdown
EXPORT_FILE="$ARCHIVE_DIR/kanban_archive_${TIMESTAMP}.md"
log "Exporting to $EXPORT_FILE..."

sqlite3 -header -csv "$DB" "SELECT id, assignee, status, priority, datetime(created_at, 'unixepoch') as created, datetime(completed_at, 'unixepoch') as done, title, body FROM tasks WHERE status IN ('done', 'archived') AND (assignee = 'swarm_executor' OR (assignee = 'hermes' AND status = 'done')) ORDER BY created_at DESC" > "$EXPORT_FILE.tmp"

# Конвертируем CSV в markdown table
python3 << PYEOF > "$EXPORT_FILE"
import csv, sys
with open("$EXPORT_FILE.tmp", 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)
    if not rows:
        print("Empty")
        sys.exit(0)
    headers = rows[0]
    print(f"# Kanban Archive — {len(rows)-1} tasks archived on $TIMESTAMP")
    print()
    print(f"**Archived:** {len(rows)-1} tasks (swarm_executor + hermes done)")
    print()
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join("---" for _ in headers) + "|")
    for row in rows[1:]:
        # Escape pipe in title/body
        row = [c.replace('|', '\\|').replace('\n', ' ')[:200] for c in row]
        print("| " + " | ".join(row) + " |")
PYEOF

rm -f "$EXPORT_FILE.tmp"
log "Exported to: $EXPORT_FILE ($(wc -l < "$EXPORT_FILE") lines)"

# 6. Удаляем из БД
log "Deleting archived tasks from DB..."
DELETED=$(sqlite3 "$DB" "DELETE FROM tasks WHERE status IN ('done', 'archived') AND (assignee = 'swarm_executor' OR (assignee = 'hermes' AND status = 'done'))" && echo "ok")
log "Deleted. New count: $(sqlite3 "$DB" 'SELECT COUNT(*) FROM tasks')"

# 7. VACUUM (уменьшает размер файла)
log "Running VACUUM..."
sqlite3 "$DB" "VACUUM"
NEW_SIZE=$(du -h "$DB" | awk '{print $1}')
log "DB size after VACUUM: $NEW_SIZE"

log "=== Done ==="
log "Remaining tasks: $(sqlite3 "$DB" 'SELECT COUNT(*) FROM tasks')"
log "Archive file: $EXPORT_FILE"
log "Backup: $BACKUP_FILE"
