#!/bin/bash
# MATRYOSHKA — Ежедневный backup в Obsidian
# Запускать каждый день в 03:00

DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_DIR="/root/matryoshka/backup/$DATE"
OBSIDIAN_VAULT="/root/vaults/matryoshka"  # если есть

echo "=== MATRYOSHKA BACKUP $DATE ==="

# Создать папку backup
mkdir -p "$BACKUP_DIR"

# SOUL.md всех профилей
cp -r /root/.hermes/profiles/*/SOUL.md "$BACKUP_DIR/profiles/" 2>/dev/null

# Досье агентов
cp -r /root/matryoshka/agents/*/README.md "$BACKUP_DIR/agents/" 2>/dev/null

# Активные проекты
cp -r /root/matryoshka/cases/*/docs/*.md "$BACKUP_DIR/projects/" 2>/dev/null

# Сессии
cp -r /root/matryoshka/sessions/*.md "$BACKUP_DIR/sessions/" 2>/dev/null

# Конфиги
cp /root/matryoshka/hermes_task.json "$BACKUP_DIR/" 2>/dev/null

# Создать архив
cd /root/matryoshka
tar -czf "backup/matryoshka_$DATE.tar.gz" backup/$DATE/

# Удалить папку (архив足够了)
rm -rf "$BACKUP_DIR"

# Хранить последние 30 бэкапов
cd /root/matryoshka/backup
ls -t | tail -n +31 | xargs -r rm -f

echo "=== BACKUP DONE: matryoshka_$DATE.tar.gz ==="