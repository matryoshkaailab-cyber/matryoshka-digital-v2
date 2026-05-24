#!/usr/bin/env python3
"""ws_server.py v9 — HERMES WebSocket Bridge + HTTP fallback
WS: 8446  HTTP: 8450  Auth: hermes-ws-secret-2026
CH1: VPS :8446 WS ↔ ws_client ↔ opencode :5001
CH2: VPS :8450 → :9000(ssh) → alex_router :4000 → opencode :5001
"""
import asyncio, json, uuid, threading, urllib.request, sqlite3, time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from websockets import serve
from threading import Thread

AUTH_TOKEN = "hermes-ws-secret-2026"
WS_PORT = 8446
HTTP_PORT = 8450

alex_connected = False
alex_lock = threading.Lock()
connected_websockets = set()

def ts():
    return datetime.now().isoformat()

async def ws_handler(websocket):
    global alex_connected
    peer = websocket.remote_address
    client_id = id(websocket)
    auth_ok = False
    print(f"[{ts()}] WS connect: {peer}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue
            if not auth_ok:
                token = data.get("token", "")
                msg_type = data.get("type", "")
                action = data.get("action", "")
                if token == AUTH_TOKEN and (msg_type == "register" or action == "connect"):
                    auth_ok = True
                    with alex_lock:
                        alex_connected = True
                        connected_websockets.add(websocket)
                    print(f"[{ts()}] ALEX registered: {peer[0]}")
                    await websocket.send(json.dumps({
                        "type": "auth_ok", "status": "authenticated",
                        "agent": "HERMES", "alex_connected": True
                    }))
                else:
                    print(f"[{ts()}] ALEX rejected: {peer[0]}")
                    await websocket.send(json.dumps({"error": "Unauthorized"}))
                continue
            msg_type = data.get("type", "")
            if msg_type == "task_result":
                print(f"[{ts()}] Task result: {data.get('task_id','')[:20]}")
                try:
                    res_data = data.get("result", {})
                    res_output = res_data.get("output", "")[:10000]
                    res_ok = res_data.get("ok", False)
                    tid = data.get("task_id", "")
                    now_ts = int(time.time())
                    kb = sqlite3.connect("/root/.hermes/kanban.db"); kb.execute("PRAGMA journal_mode=WAL"); kb.execute("PRAGMA busy_timeout=5000")
                    kb.execute("UPDATE tasks SET status=?, result=?, completed_at=?, claim_lock=NULL, claim_expires=NULL WHERE id=?",
                               ("done" if res_ok else "failed", res_output[:5000], now_ts, tid))
                    if kb.total_changes == 0:
                        kb.execute("INSERT OR IGNORE INTO tasks (id, title, body, assignee, status, priority, created_by, created_at, completed_at, result, max_runtime_seconds) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                   (tid, "API: " + tid[:16], res_output[:300], "alex", "done" if res_ok else "failed", 0, "hermes", now_ts, now_ts, res_output[:5000], 300))
                    kb.execute("INSERT INTO task_events (task_id, kind, payload, created_at) VALUES (?,?,?,?)",
                               (tid, "result_from_alex", json.dumps({"ok": res_ok, "output": res_output[:5000], "output_len": len(res_output)}), now_ts))
                    try:
                        with open("/root/matryoshka/.hermes_result.json", "w", encoding="utf-8") as rf:
                            json.dump({"task_id": tid, "status": "done", "result": {"output": res_output[:10000], "ok": res_ok}}, rf, indent=2, ensure_ascii=False)
                    except:
                        pass
                    kb.commit()
                    kb.close()
                    print(f"[{ts()}] WRITTEN to kanban.db + result file: {tid}")
                except Exception as kbe:
                    print(f"[{ts()}] kanban write error: {kbe}")
            elif msg_type == "pong":
                pass
            elif msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong", "timestamp": ts()}))
            elif msg_type == "status":
                with alex_lock:
                    count = len(connected_websockets)
                await websocket.send(json.dumps({
                    "type": "status", "alex_connected": alex_connected,
                    "client_count": count, "timestamp": ts()
                }))
    except Exception as e:
        print(f"[{ts()}] WS error {client_id}: {e}")
    finally:
        with alex_lock:
            connected_websockets.discard(websocket)
            alex_connected = bool(connected_websockets)
        print(f"[{ts()}] Client gone: {client_id}")

async def broadcast_task(task_data):
    with alex_lock:
        for ws in list(connected_websockets):
            try:
                await ws.send(json.dumps(task_data))
            except Exception as e:
                print(f"[{ts()}] Broadcast error: {e}")
                connected_websockets.discard(ws)

class HTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def check_fallback(self):
        try:
            fb = urllib.request.urlopen("http://127.0.0.1:9000/health", timeout=3)
            d = json.loads(fb.read().decode())
            return "ok" if d.get("status") == "ok" else "error"
        except:
            return "down"

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/api/status", "/api/health", "/health"):
            fb = self.check_fallback()
            self.send_json({
                "status": "ok", "service": "hermes-ws", "version": 9,
                "alex_connected": alex_connected,
                "channels": {
                    "ws": {"port": 8446, "status": "ok" if alex_connected else "no_client", "alex_connected": alex_connected},
                    "http_fallback": {"port": 9000, "target": "alex_router:4000 via ssh -R", "status": fb}
                },
                "timestamp": ts()
            })
        else:
            self.send_json({"error": "Not found"}, 404)

    def insert_kanban_task(self, task_id, command, text, channel):
        try:
            kb = sqlite3.connect("/root/.hermes/kanban.db"); kb.execute("PRAGMA journal_mode=WAL"); kb.execute("PRAGMA busy_timeout=5000")
            kb.execute("INSERT OR IGNORE INTO tasks (id, title, body, assignee, status, priority, created_by, created_at, max_runtime_seconds) VALUES (?,?,?,?,?,?,?,?,?)",
                       (task_id, "ALEX: " + command[:50], text[:500], "alex", "processing", 0, "hermes", int(time.time()), 300))
            kb.execute("INSERT INTO task_events (task_id, kind, payload, created_at) VALUES (?,?,?,?)",
                       (task_id, "dispatched", json.dumps({"channel": channel, "command": command[:200], "text_len": len(text)}), int(time.time())))
            kb.commit()
            kb.close()
        except:
            pass

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/delegate":
            self.send_json({"error": "Not found"}, 404)
            return
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8", errors="replace")
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON"}, 400)
            return
        command = request.get("command", "")
        text = request.get("text", "")
        timeout = int(request.get("timeout", 300))
        task_id = f"api_{uuid.uuid4().hex}"
        if not command:
            self.send_json({"error": "No command"}, 400)
            return

        if not connected_websockets:
            try:
                fb = urllib.request.Request(
                    "http://127.0.0.1:9000/task",
                    data=json.dumps(request).encode(),
                    headers={"Content-Type": "application/json"}
                )
                fb_resp = urllib.request.urlopen(fb, timeout=15)
                fb_body = json.loads(fb_resp.read().decode())
                self.send_json({"ok": fb_body.get("ok", False), "task_id": task_id, "fallback": "http"})
                print(f"[{ts()}] HTTP fallback via tunnel: {task_id}")
                return
            except Exception as e:
                self.send_json({"error": "ALEX not connected, fallback failed: " + str(e)}, 503)
                return

        ws_msg = {"type": "task", "task_id": task_id,
                  "task": {"command": command, "text": text, "timeout": timeout}}
        asyncio.run_coroutine_threadsafe(broadcast_task(ws_msg), loop)
        self.send_json({"ok": True, "task_id": task_id, "timestamp": ts()})
        self.insert_kanban_task(task_id, command, text, "ws")

def run_http():
    server = HTTPServer(("0.0.0.0", HTTP_PORT), HTTPHandler)
    print(f"[{ts()}] HTTP API on :{HTTP_PORT}")
    server.serve_forever()

loop = None

async def main():
    global loop
    loop = asyncio.get_running_loop()
    http_thread = Thread(target=run_http, daemon=True)
    http_thread.start()
    print(f"[{ts()}] WS Server v9 on :{WS_PORT}")
    async with serve(ws_handler, "0.0.0.0", WS_PORT):
        print(f"[{ts()}] Auth: {AUTH_TOKEN}")
        await asyncio.Future()

if __name__ == "__main__":
    print(f"[{ts()}] Starting WS Server v9 on :{WS_PORT}")
    print(f"[{ts()}] HTTP API on :{HTTP_PORT}")
    asyncio.run(main())
