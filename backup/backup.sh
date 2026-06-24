#!/bin/bash
DATE=$(date +"%Y-%m-%d")
BACKUP_DIR="/root/matryoshka/backup/$DATE"
mkdir -p "$BACKUP_DIR"/{profiles,agents,projects,sessions}
# SOUL.md profiles
cp /root/.hermes/profiles/*/SOUL.md "$BACKUP_DIR/profiles/" 2>/dev/null
# Agent dossiers
cp /root/matryoshka/agents/*/README.md "$BACKUP_DIR/agents/" 2>/dev/null
# Projects
find /root/matryoshka/cases -name "*.md" -path "*/docs/*" -exec cp {} "$BACKUP_DIR/projects/" \; 2>/dev/null
# Sessions
cp /root/matryoshka/sessions/*.md "$BACKUP_DIR/sessions/" 2>/dev/null
# Archive
cd /root/matryoshka
tar -czf "backup/matryoshka_$DATE.tar.gz" backup/$DATE/
rm -rf "$BACKUP_DIR"
# Keep 30 days
cd /root/matryoshka/backup/
ls -t | tail -n +31 | xargs -r rm -f
echo "Backup done: matryoshka_$DATE.tar.gz"
