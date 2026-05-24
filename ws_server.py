#!/usr/bin/env python3
"""
ws_server.py — HERMES WebSocket Bridge (v7)
=============================================
WebSocket: port 8446 (accepts ALEX)
HTTP API:  port 8450 (task delegation)
Auth: hermes-ws-secret-2026
Protocol: compatible with ws_client v38 (type=register) and legacy (action=connect)
"""

import asyncio
import json
import threading
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from websockets import serve

AUTH_TOKEN = "hermes-ws-secret-2026"
WS_PORT = 8446
HTTP_PORT = 8450

alex_connected = False
alex_lock = threading.Lock()
pending_tasks = {}
tasks_condition = threading.Condition()
connected_websockets = set()

def get_timestamp():
    return datetime.now().isoformat()

async def ws_handler(websocket):
    """Handle WebSocket connections from ALEX"""
    global alex_connected

    client_id = id(websocket)
    auth_ok = False
    peer = websocket.remote_address

    print(f"[{get_timestamp()}] WS Client {client_id} from {peer}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON"}))
                continue

            if not auth_ok:
                token = data.get("token", "")
                # accept both type=register (v38) and action=connect (legacy)
                msg_type = data.get("type", "")
                action = data.get("action", "")
                if token == AUTH_TOKEN and (msg_type == "register" or action == "connect"):
                    auth_ok = True
                    with alex_lock:
                        alex_connected = True
                        connected_websockets.add(websocket)
                    print(f"[{get_timestamp()}] ALEX registered from {peer[0]}: {client_id}")
                    await websocket.send(json.dumps({
                        "type": "auth_ok",
                        "status": "authenticated",
                        "agent": "HERMES",
                        "alex_connected": True
                    }))
                else:
                    print(f"[{get_timestamp()}] ALEX rejected from {peer[0]}")
                    await websocket.send(json.dumps({"error": "Unauthorized"}))
                continue

            msg_type = data.get("type", "")

            if msg_type == "task_result":
                task_id = data.get("task_id", "")
                result = data.get("result", {})
                with tasks_condition:
                    pending_tasks[task_id] = {
                        "result": result,
                        "timestamp": get_timestamp(),
                        "done": True
                    }
                    tasks_condition.notify_all()

            elif msg_type == "pong":
                pass
            elif msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong", "timestamp": get_timestamp()}))
            elif msg_type == "status":
                with alex_lock:
                    count = len(connected_websockets)
                await websocket.send(json.dumps({
                    "type": "status",
                    "alex_connected": alex_connected,
                    "client_count": count,
                    "pending_tasks": len(pending_tasks),
                    "timestamp": get_timestamp()
                }))
            else:
                pass

    except Exception as e:
        print(f"[{get_timestamp()}] WS error client {client_id}: {e}")
    finally:
        with alex_lock:
            connected_websockets.discard(websocket)
            if not connected_websockets:
                alex_connected = False
        print(f"[{get_timestamp()}] Client gone: {client_id}")

# ========== MESSAGE QUEUE ==========

msg_queue = []
msg_queue_lock = threading.Lock()

def queue_ws_message(msg_json, loop):
    with msg_queue_lock:
        msg_queue.append((loop, msg_json))
    with tasks_condition:
        tasks_condition.notify_all()

# ========== HTTP API ==========

class HTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            with alex_lock:
                data = {
                    "alex_connected": alex_connected,
                    "pending_tasks": len(pending_tasks),
                    "timestamp": get_timestamp()
                }
            self.send_json(data)
        elif path == "/api/health":
            self.send_json({"status": "ok", "timestamp": get_timestamp()})
        elif path == "/health":
            self.send_json({"status": "ok", "service": "hermes-ws", "alex_connected": alex_connected, "timestamp": get_timestamp()})
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/delegate":
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
            self.send_json({"error": "No command provided"}, 400)
            return

        with alex_lock:
            client_count = len(connected_websockets)

        if client_count == 0:
            self.send_json({"error": "ALEX not connected", "alex_connected": False}, 503)
            return

        ws_msg = json.dumps({
            "type": "task",
            "task_id": task_id,
            "task": {"command": command, "text": text, "timeout": timeout}
        })

        queue_ws_message(ws_msg, asyncio.get_event_loop())

        with tasks_condition:
            pending_tasks[task_id] = {"waiting": True, "command": command}
            start_time = datetime.now()
            while pending_tasks[task_id].get("waiting", False):
                remaining = timeout - (datetime.now() - start_time).seconds
                if remaining <= 0:
                    del pending_tasks[task_id]
                    self.send_json({"error": "Task timeout", "task_id": task_id, "ok": False}, 504)
                    return
                tasks_condition.wait(timeout=max(1, min(remaining, 10)))
                if task_id in pending_tasks and pending_tasks[task_id].get("done"):
                    result = pending_tasks[task_id]["result"]
                    del pending_tasks[task_id]
                    self.send_json({"ok": True, "task_id": task_id, "result": result, "timestamp": get_timestamp()})
                    return

        del pending_tasks[task_id]
        self.send_json({"error": "Task failed"}, 500)

def run_http_server():
    server = HTTPServer(("0.0.0.0", HTTP_PORT), HTTPHandler)
    print(f"[{get_timestamp()}] HTTP API started on http://127.0.0.1:{HTTP_PORT}")
    server.serve_forever()

async def ws_message_consumer():
    while True:
        with tasks_condition:
            while len(msg_queue) == 0:
                tasks_condition.wait(timeout=1)
            with msg_queue_lock:
                if msg_queue:
                    loop, msg_json = msg_queue.pop(0)
                else:
                    continue
        if msg_json:
            with alex_lock:
                for ws in list(connected_websockets):
                    try:
                        await ws.send(msg_json)
                    except Exception as e:
                        print(f"[{get_timestamp()}] Failed to send: {e}")
                        connected_websockets.discard(ws)

async def main_async():
    ws_task = asyncio.create_task(start_ws_server())
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    consumer_task = asyncio.create_task(ws_message_consumer())
    await ws_task

async def start_ws_server():
    try:
        async with serve(ws_handler, "0.0.0.0", WS_PORT):
            print(f"[{get_timestamp()}] Starting WS Server v7 on port {WS_PORT}")
            print(f"[{get_timestamp()}] Auth: {AUTH_TOKEN}")
            await asyncio.Future()
    except Exception as e:
        print(f"[{get_timestamp()}] WS server error: {e}")

def main():
    print(f"[{get_timestamp()}] Starting WS Server v7 on port {WS_PORT}")
    print(f"[{get_timestamp()}] HTTP API on port {HTTP_PORT}")
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
