#!/bin/bash
# ACP-делегация к ALEX (opencode 1.17.3) — фикс от 18.06.2026
# ROOT CAUSE прошлых 500: shell-интерпретация ломала JSON. payload через --data-binary @file.json
# AUTH берётся из ~/.netrc (machine 10.8.1.4, login opencode, password ...)
# Stack: opencode 1.17.3, model minimax/MiniMax-M3, agent "build", port 4096, AmneziaWG
# НЕ ТРОГАТЬ alex_stack.py / MCP / opencode.json без согласования
#
# Использование:
#   ./alex_acp.sh "Get-Date"
#   ./alex_acp.sh "прочитай C:\path\to\file.txt" 60

set -e

ACP_URL="http://10.8.1.4:4096"

if [ -z "$1" ]; then
  echo "Usage: $0 <prompt> [timeout_sec]" >&2
  exit 1
fi
PROMPT="$1"
TIMEOUT="${2:-60}"

echo "[ACP] target: $ACP_URL (opencode 1.17.3, agent=build)"

# 1. Создать session
echo "[ACP] Creating session..."
SES_JSON=$(curl -sf --netrc --max-time 10 \
  -X POST "$ACP_URL/session" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data-binary '{}')
SES_ID=$(echo "$SES_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "[ACP] Session: $SES_ID"

# 2. Подготовить payload в ФАЙЛ (избегаем shell-квотинга кавычек)
PAYLOAD_FILE=$(mktemp /tmp/acp_payload.XXXXXX.json)
python3 -c "
import json, sys
print(json.dumps({'parts': [{'type': 'text', 'text': sys.argv[1]}]}))
" "$PROMPT" > "$PAYLOAD_FILE"

# 3. Отправить prompt_async (только parts, БЕЗ model)
echo "[ACP] Sending prompt (timeout ${TIMEOUT}s)..."
curl -sf --netrc --max-time 10 \
  -X POST "$ACP_URL/session/$SES_ID/prompt_async" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data-binary "@$PAYLOAD_FILE" > /dev/null
rm -f "$PAYLOAD_FILE"

# 4. Ждать ответа (polling /prompts)
WAIT_ITERS=$((TIMEOUT / 2))
for i in $(seq 1 $WAIT_ITERS); do
  sleep 2
  RESP=$(curl -sf --netrc --max-time 5 \
    -H "Accept: application/json" \
    "$ACP_URL/session/$SES_ID/prompts" 2>/dev/null || echo "")
  if [ -n "$RESP" ] && [ "$RESP" != "{}" ] && [ "$RESP" != "[]" ]; then
    echo "[ACP] Got response after ${i}x2s:"
    echo "$RESP" | python3 -m json.tool 2>/dev/null || echo "$RESP"
    exit 0
  fi
done

echo "[ACP] TIMEOUT after ${TIMEOUT}s" >&2
exit 1
