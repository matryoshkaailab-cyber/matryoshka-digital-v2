#!/usr/bin/env python3
"""vps_tunnel_bridge.py ??? ALEX bridge (VPS-side), forwards to PC via WG VPN
Listens on :8454, proxies to 10.8.1.4:8446 (alex_bridge HTTP API) through AmneziaWG
"""
import http.server
import json
import urllib.request
import urllib.error

HOST = "127.0.0.1"
PORT = 8453
ALEX_BRIDGE = "http://10.8.1.4:8446"

class BridgeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "ok", "mode": "wg-direct", "target": ALEX_BRIDGE})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except Exception:
            self._json(400, {"error": "invalid json"})
            return

        try:
            req = urllib.request.Request(
                ALEX_BRIDGE,
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            resp = urllib.request.urlopen(req, timeout=180)
            result = json.loads(resp.read())
            self._json(resp.status, result)
        except urllib.error.URLError as e:
            self._json(502, {"ok": False, "error": f"ALEX unreachable via WG: {e.reason}"})
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer((HOST, PORT), BridgeHandler)
    print(f"VPS Tunnel Bridge running on :{PORT} -> ALEX via WG ({ALEX_BRIDGE})")
    server.serve_forever()

