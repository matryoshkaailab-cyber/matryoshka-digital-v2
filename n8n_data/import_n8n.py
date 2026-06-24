import urllib.request
import json
import http.cookiejar
import sys

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cj)
)

# Try different emails
for email in ["admin@matryoshka-digital.ru", "admin", "admin@localhost"]:
    data = json.dumps({"email": email, "password": "matryoshka2026"}).encode()
    req = urllib.request.Request(
        "http://localhost:5678/rest/login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = opener.open(req)
        body = json.loads(resp.read().decode())
        print(f"Login OK with {email}: {body.get('data', {}).get('id', 'no id')}")
        break
    except Exception as e:
        print(f"Login failed with {email}: {e}")
else:
    print("All login attempts failed")
    sys.exit(1)

# Import workflow
with open("/root/matryoshka/n8n_data/payment_webhook.json") as f:
    workflow = json.load(f)

req2 = urllib.request.Request(
    "http://localhost:5678/rest/workflows",
    data=json.dumps(workflow).encode(),
    headers={"Content-Type": "application/json"},
)
try:
    resp2 = opener.open(req2)
    result = json.loads(resp2.read().decode())
    wid = result.get("data", {}).get("id", "?")
    wname = result.get("data", {}).get("name", "?")
    print(f"Workflow imported: ID={wid}, Name={wname}")
except Exception as e:
    print(f"Import error: {e}")
    # Try reading error body
    try:
        print(e.read().decode()[:500])
    except:
        pass
