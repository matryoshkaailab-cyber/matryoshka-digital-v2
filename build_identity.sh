#!/bin/bash
# build_identity.sh — собирает SOUL.md из канонических источников
# Один источник истины: /root/matryoshka/HERMES_IDENTITY_FULL.md (657KB)
# На выходе: /root/matryoshka/SOUL.md (компактный 334 строки)
# Затем 3 symlink на этот файл.
#
# Использование:
#   ./build_identity.sh            # собрать + symlink
#   ./build_identity.sh --check    # только проверить целостность

set -e
CANONICAL=/root/matryoshka/HERMES_IDENTITY_FULL.md
SOUL=/root/matryoshka/SOUL.md
TS=$(date +%Y%m%d_%H%M%S)
LOG=/var/log/build_identity.log

log() { echo "[$(date '+%F %T')] $1" | tee -a "$LOG"; }

if [ ! -f "$CANONICAL" ]; then
    log "ERROR: canonical not found: $CANONICAL"
    exit 1
fi

log "Source: $CANONICAL ($(wc -l < $CANONICAL) строк, $(stat -c%s $CANONICAL) байт)"

# Извлечь ядро SOUL из полного файла (раздел "## Идентичность" до "## КЕЙСЫ")
python3 << PYEOF
import re
with open("$CANONICAL", "r", encoding="utf-8") as f:
    full = f.read()
# Ищем блок SOUL (метаданные + идентичность + правила)
# Берём секцию от "# SOUL" до "## КЕЙСЫ" или "## КОНСТАНТЫ"
m = re.search(r'(# SOUL.*?)(?=^## (?:КЕЙСЫ|КОНСТАНТЫ|УРОКИ))', full, re.DOTALL | re.MULTILINE)
if m:
    soul = m.group(1).rstrip() + "\n"
else:
    # fallback: первые 350 строк
    soul = "\n".join(full.splitlines()[:350]) + "\n"
with open("$SOUL", "w", encoding="utf-8") as f:
    f.write(soul)
print(f"SOUL.md written: {len(soul)} bytes, {len(soul.splitlines())} lines")
PYEOF

log "Built: $SOUL ($(wc -l < $SOUL) строк)"

if [ "${1:-}" = "--check" ]; then
    log "CHECK mode — symlinks not touched"
    for L in /root/.hermes/SOUL.md /root/.hermes/profiles/hermes-cli/SOUL.md /root/.hermes/profiles/hermes-orchestrator/SOUL.md; do
        if [ -L "$L" ]; then
            target=$(readlink "$L")
            if [ "$target" = "$SOUL" ]; then
                log "  OK  $L -> $target"
            else
                log "  BAD $L -> $target (expected $SOUL)"
            fi
        elif [ -f "$L" ]; then
            log "  WARN $L is a regular file (should be symlink)"
        fi
    done
    exit 0
fi

# Бэкап старых копий
for F in /root/.hermes/SOUL.md /root/.hermes/profiles/hermes-cli/SOUL.md /root/.hermes/profiles/hermes-orchestrator/SOUL.md; do
    if [ -f "$F" ] && [ ! -L "$F" ]; then
        cp "$F" "${F}.bak.${TS}"
        log "Backup: ${F}.bak.${TS}"
        rm -f "$F"
    fi
done

# Создаём symlinks
ln -sf "$SOUL" /root/.hermes/SOUL.md
ln -sf "$SOUL" /root/.hermes/profiles/hermes-cli/SOUL.md
ln -sf "$SOUL" /root/.hermes/profiles/hermes-orchestrator/SOUL.md
log "Symlinks created:"
ls -la /root/.hermes/SOUL.md /root/.hermes/profiles/hermes-cli/SOUL.md /root/.hermes/profiles/hermes-orchestrator/SOUL.md | tee -a "$LOG"

log "=== DONE ==="
