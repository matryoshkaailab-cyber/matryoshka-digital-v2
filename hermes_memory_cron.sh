#!/bin/bash
F=/root/matryoshka/HERMES_MEMORY.md
TS=$(date '+%Y-%m-%d %H:%M:%S')
GATE=$(systemctl is-active hermes-cli-gateway 2>/dev/null || echo "unknown")
DBSIZE=$(du -h /root/.hermes/state.db 2>/dev/null | cut -f1)
COUNT=$(sqlite3 /root/.hermes/state.db "SELECT COUNT(*) FROM messages;" 2>/dev/null || echo "n/a")
LAST=$(sqlite3 /root/.hermes/state.db "SELECT substr(content, 1, 200) FROM messages ORDER BY id DESC LIMIT 1;" 2>/dev/null | tr '\n' ' ' | head -c 200)
{
  echo ""
  echo "## $TS"
  echo "- gateway: $GATE"
  echo "- state.db: $DBSIZE, messages: $COUNT"
  echo "- last: $LAST"
} >> "$F"
