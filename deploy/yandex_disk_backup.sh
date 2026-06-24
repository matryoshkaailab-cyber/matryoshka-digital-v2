#!/bin/bash
# MATRYOSHKA Yandex.Disk backup via WebDAV
set -e
LOG="/var/log/yandex_backup.log"
SRC="/root/matryoshka/backup"
DEST_BASE="https://webdav.yandex.ru/matryoshka-backups"
TS=$(date +%Y-%m-%d)
echo "=== Yandex WebDAV backup $TS ===" >> "$LOG"

# Load WebDAV creds
USER=$(grep '^YANDEX_WEBDAV_USER=' /root/matryoshka/.env | cut -d= -f2-)
PASS=$(grep '^YANDEX_WEBDAV_PASSWORD=' /root/matryoshka/.env | cut -d= -f2-)
[ -z "$USER" ] || [ -z "$PASS" ] && { echo "NO CREDS" >> "$LOG"; exit 1; }

# Ensure remote folder exists
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -u "$USER:$PASS" -X MKCOL "$DEST_BASE")
echo "MKCOL: HTTP $HTTP" >> "$LOG"
# 201 created, 405 already exists, anything else fail
[ "$HTTP" != "201" ] && [ "$HTTP" != "405" ] && { echo "MKCOL FAILED" >> "$LOG"; exit 1; }

# Push latest archive
LATEST=$(ls -t "$SRC"/matryoshka_*.tar.gz 2>/dev/null | head -1)
[ -z "$LATEST" ] && { echo "NO ARCHIVES" >> "$LOG"; exit 1; }
NAME=$(basename "$LATEST")
echo "Push: $NAME" >> "$LOG"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" -u "$USER:$PASS" -T "$LATEST" "$DEST_BASE/$NAME")
if [ "$HTTP" = "201" ] || [ "$HTTP" = "204" ]; then
  echo "OK $HTTP: $NAME uploaded" >> "$LOG"
else
  echo "FAIL $HTTP for $NAME" >> "$LOG"
  exit 1
fi