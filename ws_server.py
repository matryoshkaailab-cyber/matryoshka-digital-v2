#!/usr/bin/env python3
"""
ws_server.py v8 — HERMES WebSocket Bridge
=========================================
WS: 8446  HTTP API: 8450  Auth: hermes-ws-secret-2026
"""

import asyncio
import json
import uuid
import threading
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

# ========== WS HANDLER ==========

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

# ========== TASK BROADCAST ==========

async def broadcast_task(task_data):
    with alex_lock:
        for ws in list(connected_websockets):
            try:
                await ws.send(json.dumps(task_data))
            except Exception as e:
                print(f"[{ts()}] Broadcast error: {e}")
                connected_websockets.discard(ws)

# ========== HTTP API ==========

class HTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/api/status", "/api/health", "/health"):
            self.send_json({
                "status": "ok", "service": "hermes-ws",
                "alex_connected": alex_connected,
                "timestamp": ts()
            })
        else:
            self.send_json({"error": "Not found"}, 404)

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
            self.send_json({"error": "ALEX not connected"}, 503)
            return

        ws_msg = {
            "type": "task", "task_id": task_id,
            "task": {"command": command, "text": text, "timeout": timeout}
        }
        asyncio.run_coroutine_threadsafe(broadcast_task(ws_msg), loop)
        self.send_json({"ok": True, "task_id": task_id, "timestamp": ts()})

def run_http():
    server = HTTPServer(("0.0.0.0", HTTP_PORT), HTTPHandler)
    print(f"[{ts()}] HTTP API on :{HTTP_PORT}")
    server.serve_forever()

# ========== MAIN ==========

loop = None

async def main():
    global loop
    loop = asyncio.get_running_loop()

    http_thread = Thread(target=run_http, daemon=True)
    http_thread.start()

    print(f"[{ts()}] WS Server v8 on :{WS_PORT}")
    async with serve(ws_handler, "0.0.0.0", WS_PORT):
        print(f"[{ts()}] Auth: {AUTH_TOKEN}")
        await asyncio.Future()

if __name__ == "__main__":
    print(f"[{ts()}] Starting WS Server v8 on :{WS_PORT}")
    print(f"[{ts()}] HTTP API on :{HTTP_PORT}")
    asyncio.run(main())
