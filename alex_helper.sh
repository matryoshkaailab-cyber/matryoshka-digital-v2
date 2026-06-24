#!/bin/bash
BRIDGE_URL="${1:-http://127.0.0.1:8453}"
TASK="${2:-ping}"
case "$TASK" in
  ping)
    echo "=== bridge health ==="
    curl -sf "$BRIDGE_URL/health" 2>/dev/null || echo "unreachable"
    echo "=== direct test ==="
    curl -sf -X POST "http://10.8.1.4:8446/" -H "Content-Type: application/json" -d '{"task":"say OK_ALEX"}' --max-time 30 2>/dev/null || echo "fail"
    ;;
  *)
    curl -sf -X POST "$BRIDGE_URL/" -H "Content-Type: application/json" -d "{\"task\":\"$TASK\"}" --max-time 120 2>/dev/null || echo '{"ok":false,"error":"timeout"}'
    ;;
esac