#!/bin/bash
# client_audit_from_db.sh — генерирует client_audit.json из реальных клиентов в clients.db
# Использование: bash client_audit_from_db.sh [limit]   (default limit=10)
set -e
LIMIT=${1:-10}
DB=/root/matryoshka/data/clients.db
OUT=/tmp/client_audit_$(date +%s).json
TS=$(date -u +'%Y-%m-%d %H:%M UTC')

# Check db exists
if [ ! -f "$DB" ]; then
  echo "ERROR: $DB not found. Run: python3 /root/matryoshka/deploy/clients_db.py init" >&2
  exit 1
fi

# Generate JSON
python3 - "$LIMIT" "$TS" "$OUT" <<'PY'
import json, sys, sqlite3
limit = int(sys.argv[1])
ts = sys.argv[2]
out_path = sys.argv[3]
db = "/root/matryoshka/data/clients.db"
c = sqlite3.connect(db)
c.row_factory = sqlite3.Row
rows = c.execute(
    "SELECT * FROM clients WHERE status='active' ORDER BY id LIMIT ?",
    (limit,),
).fetchall()
children = []
for r in rows:
    name = r["name"]
    ip = r["vpn_ip"] or "n/a"
    plan = r["plan"] or "n/a"
    tg = r["telegram"] or "n/a"
    contact = r["contact_date"] or "n/a"
    notes = r["notes"] or ""
    # bash cmd: simple audit checks
    cmd = f"""echo "[{name}] ip={ip} plan={plan} tg={tg} last_contact={contact}" && \\
if [ "{ip}" != "n/a" ]; then \\
  /usr/bin/ping -c1 -W2 {ip} >/dev/null 2>&1 && echo "  ping: OK" || echo "  ping: FAIL" ; \\
else \\
  echo "  ping: SKIP (no ip)" ; \\
fi && \\
echo "  notes: {notes}" """
    children.append({
        "title": f"Audit {name} ({plan})",
        "assignee": "swarm_executor",
        "priority": 1,
        "cmd": cmd,
    })

data = {
    "template": "client_audit",
    "parent_title": f"Client audit (real DB, {len(children)} clients) @ {ts}",
    "description": f"Audit of {len(children)} real clients from clients.db",
    "children": children,
}
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Generated: {out_path} ({len(children)} children)")
PY

echo
echo "=== POST to swarm API ==="
RESP=$(curl -s -u hermes:hermes2026 -X POST http://127.0.0.1:9999/swarm/create \
  -H "Content-Type: application/json" \
  -d "{\"template\":\"client_audit\",\"params\":{\"TIMESTAMP\":\"$TS\",\"__use_generated\":\"$OUT\"}}")
echo "$RESP"

# Alternative: use dispatcher directly with our generated file
PARENT_ID=$(python3 /root/matryoshka/deploy/swarm_dispatcher.py create "$OUT" 2>&1 | grep -oE 'swarm_client_audit_[0-9a-z_]+' | head -1)
echo
echo "PARENT_ID=$PARENT_ID"
rm -f "$OUT"
