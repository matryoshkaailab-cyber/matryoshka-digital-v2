#!/bin/bash
set -e
ACP_URL="http://10.8.1.4:4096"
AUTH="opencode:0796731b-ed11-4f37-b1fb-3a1773fc825f"

echo "[ACP] Creating session..."
SES_RESPONSE=$(curl -s -u "$AUTH" -X POST "$ACP_URL/session" -H "Content-Type: application/json" -H "Accept: application/json" -d '{}')
SES_ID=$(echo "$SES_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "[ACP] Session: $SES_ID"

echo "[ACP] Sending prompt: $1"
PAYLOAD=$(python3 -c "import sys, json; print(json.dumps({'parts': [{'type': 'text', 'text': sys.argv[1]}]}))" "$1")
curl -sf -u "$AUTH" -X POST "$ACP_URL/session/$SES_ID/prompt_async" -H "Content-Type: application/json" -H "Accept: application/json" -d "$PAYLOAD"
echo "[ACP] Prompt sent. Waiting for response..."

for i in {1..30}; do
  sleep 2
  RESP=$(curl -sf -u "$AUTH" -H "Accept: application/json" "$ACP_URL/session/$SES_ID/prompts" || echo "")
  if [ -n "$RESP" ] && [ "$RESP" != "{}" ] && [ "$RESP" != "[]" ]; then
    echo "[ACP] Got response:"
    echo "$RESP"
    exit 0
  fi
done
echo "Timeout waiting for response" >&2
exit 1
