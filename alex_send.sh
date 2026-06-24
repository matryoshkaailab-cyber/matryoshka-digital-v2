#!/bin/bash
# alex_send.sh — единственный способ общения VPS↔ALEX (через opencode ACP :4096)
# Usage: alex_send.sh "текст запроса" [таймаут_сек] [model]
#   model: <providerID>/<modelID>
#          дефолт: opencode/deepseek-v4-flash-free (единственный что РЕАЛЬНО работал 20.06.2026)
#          другие: NVIDIA/moonshotai/kimi-k2.6, opencode/qwen3.6-plus-free и т.д.
# БАГ-ФИКС 20.06.2026: дефолт был "deepseek-v4-flash-free" без провайдера →
#   providerID становился "deepseek-v4-flash-free" → модель не находилась → пустой ответ exit 1.
set -e

QUERY="${1:?Usage: alex_send.sh 'запрос' [timeout] [model]}"
TIMEOUT="${2:-60}"
MODEL="${3:-minimax-coding-plan/MiniMax-M3}"  # 20.06.2026: сменено с opencode/deepseek-v4-flash-free (платный $0.005/вызов → бесплатный $0 через coding plan)
ENDPOINT="http://10.8.1.4:4096"

# 1. Health check
if ! curl -s -m 5 -f "$ENDPOINT/health" > /dev/null; then
    echo "❌ $ENDPOINT/health не отвечает" >&2
    exit 1
fi

# 2. Создать сессию
SESSION_JSON=$(curl -s -X POST "$ENDPOINT/session" \
  -H 'Content-Type: application/json' -d '{}' -m 10)
SESSION=$(echo "$SESSION_JSON" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('id',''))" 2>/dev/null || true)
if [ -z "$SESSION" ]; then
    echo "❌ Не удалось создать сессию" >&2
    echo "Response: $SESSION_JSON" >&2
    exit 2
fi

# 3. Отправить через POST /session/<id>/message — СИНХРОННЫЙ ответ в теле
#    (Аликс подтвердил 20.06: /prompt_async НЕ работает для нарративов — модель
#     уходит в tool-calls и не возвращает финальный text. /message — синхронно.)
#    /messages?limit=1 (PLURAL) НЕ существует — возвращает SPA HTML fallback.
SESSION_JSON=$(curl -s "$ENDPOINT/session/$SESSION" -m 5)
PROVIDER_ID=$(echo "$SESSION_JSON" | python3 -c "
import sys,json
d=json.load(sys.stdin)
m=d.get('model') or {}
print(m.get('providerID',''))" 2>/dev/null || echo "")
[ -z "$PROVIDER_ID" ] && PROVIDER_ID="MiniMax"
if [[ "$MODEL" == *"/"* ]]; then
    PROVIDER_ID="${MODEL%%/*}"
    MODEL_ID="${MODEL#*/}"
else
    MODEL_ID="$MODEL"
fi
PAYLOAD=$(python3 -c "
import json,sys
print(json.dumps({
    'model': {'providerID': sys.argv[1], 'modelID': sys.argv[2]},
    'parts':[{'type':'text','text':sys.argv[3]}]
}))" "$PROVIDER_ID" "$MODEL_ID" "$QUERY")

# POST /message — синхронный ответ
# ВАЖНО: Accept: application/json обязателен, иначе opencode может вернуть
# streaming/event-stream или text/html SPA fallback → curl timeout
RESP=$(curl -s -m "$TIMEOUT" -X POST "$ENDPOINT/session/$SESSION/message" \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -d "$PAYLOAD")
TEXT=$(echo "$RESP" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    # opencode 1.17.8: ответ — dict с info+parts (НЕ список сообщений)
    if isinstance(d, dict):
        info = d.get('info') or {}
        # Извлекаем последний text part
        best = ''
        for p in d.get('parts', []):
            if p.get('type') == 'text' and p.get('text'):
                best = p['text']
        if best:
            print(best)
            sys.exit(0)
        # Если нет text — может быть только reasoning (застрял в thinking)
        if info.get('finish') == 'stop':
            sys.exit(2)  # finish но нет text = странно
        sys.exit(3)  # нет finish
    sys.exit(4)
except Exception as e:
    sys.exit(1)
" 2>/dev/null)
if [ -n "$TEXT" ]; then
    echo "$TEXT"
    exit 0
fi

# Fallback: если синхронно не сработало — polling /message (SINGULAR)
# ВАЖНО: Accept: application/json обязателен
echo "⚠️  синхронный ответ пустой, пробую polling..." >&2
ELAPSED=0
INTERVAL=3
while [ $ELAPSED -lt 30 ]; do
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    RESP=$(curl -s "$ENDPOINT/session/$SESSION/message" -m 5 \
        -H 'Accept: application/json')
    TEXT=$(echo "$RESP" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    if not isinstance(d, list): sys.exit(2)
    best = ''
    for m in d:
        info = m.get('info') or {}
        if info.get('finish') == 'stop' or m.get('role') == 'assistant':
            for p in m.get('parts', []):
                if p.get('type') == 'text' and p.get('text'):
                    best = p['text']
    print(best); sys.exit(0 if best else 1)
except: sys.exit(2)
" 2>/dev/null)
    if [ -n "$TEXT" ]; then
        echo "$TEXT"
        exit 0
    fi
done

echo "❌ Таймаут, ответа нет" >&2
echo "Сессия: $SESSION" >&2
exit 3
