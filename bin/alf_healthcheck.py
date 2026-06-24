#!/usr/bin/env python3
"""
alf_healthcheck.py — HTTP healthcheck для ALF gateway (port 8452)
Фаза 1 ALF_ROLE_PROPOSAL_23.06.md

Endpoints:
  GET /health   → 200 OK если systemd active, 503 если нет
  GET /metrics  → JSON с memory, uptime, last task, pid
  GET /         → документация

Запускается через systemd alf-healthcheck.service
"""
import json
import subprocess
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

SERVICE = "hermes-gateway-alf.service"
PORT = 8452
LAST_TASK_FILE = "/root/matryoshka/swarm/outbox/alf/.notified"  # bridge writes here

def get_systemctl_info() -> dict:
    """Получить state, PID, memory, uptime из systemd."""
    try:
        # Active state
        state_proc = subprocess.run(
            ["systemctl", "is-active", SERVICE],
            capture_output=True, text=True, timeout=5
        )
        active = state_proc.stdout.strip() == "active"

        # Main PID + Memory + ActiveEnterTimestamp
        show_proc = subprocess.run(
            ["systemctl", "show", SERVICE,
             "--property=MainPID,MemoryCurrent,ActiveEnterTimestamp,ActiveEnterTimestampMonotonic"],
            capture_output=True, text=True, timeout=5
        )
        props = {}
        for line in show_proc.stdout.strip().split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                props[k] = v

        pid = int(props.get("MainPID", "0") or 0)
        mem_bytes = int(props.get("MemoryCurrent", "0") or 0)
        mem_mb = round(mem_bytes / 1024 / 1024, 1) if mem_bytes else 0
        active_since = props.get("ActiveEnterTimestamp", "")

        # Process RSS через ps (более точный)
        if pid > 0:
            try:
                ps_proc = subprocess.run(
                    ["ps", "-p", str(pid), "-o", "rss=,etime="],
                    capture_output=True, text=True, timeout=5
                )
                if ps_proc.stdout.strip():
                    parts = ps_proc.stdout.strip().split()
                    rss_kb = int(parts[0])
                    etime = parts[1] if len(parts) > 1 else "?"
                    mem_mb_ps = round(rss_kb / 1024, 1)
                    # Берём максимум из двух измерений
                    if mem_mb_ps > mem_mb:
                        mem_mb = mem_mb_ps
                else:
                    etime = "?"
            except Exception:
                etime = "?"
        else:
            etime = "?"

        return {
            "active": active,
            "pid": pid,
            "memory_mb": mem_mb,
            "uptime": etime,
            "active_since": active_since,
        }
    except Exception as e:
        return {"active": False, "error": str(e)}


def get_last_task() -> dict:
    """Найти последнюю обработанную задачу в outbox."""
    try:
        notified_dir = Path(LAST_TASK_FILE)
        if not notified_dir.exists():
            return {"last_task": None}

        files = sorted(notified_dir.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)
        if not files:
            return {"last_task": None}

        latest = files[0]
        mt = latest.stat().st_mtime
        age_sec = int(time.time() - mt)

        return {
            "last_task_file": latest.name,
            "last_task_age_sec": age_sec,
            "last_task_age_human": f"{age_sec // 3600}h {(age_sec % 3600) // 60}m {age_sec % 60}s",
        }
    except Exception as e:
        return {"last_task": None, "error": str(e)}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Логируем в journal
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        msg = f"[{ts}] {self.address_string()} {fmt % args}"
        print(msg, flush=True)

    def _json_response(self, status: int, data: dict):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _text_response(self, status: int, text: str):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        info = get_systemctl_info()

        if path == "/health":
            if info.get("active"):
                self._json_response(200, {"status": "ok", "pid": info["pid"]})
            else:
                self._json_response(503, {"status": "down", "info": info})

        elif path == "/metrics":
            last_task = get_last_task()
            payload = {
                "service": SERVICE,
                "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                **info,
                **last_task,
            }
            self._json_response(200, payload)

        elif path == "/" or path == "/docs":
            self._text_response(200, (
                "ALF Healthcheck Server (alf_healthcheck.py)\n"
                "Endpoints:\n"
                "  GET /health   — 200 если systemd active, 503 если down\n"
                "  GET /metrics  — JSON с memory, uptime, last task\n"
                "  GET /         — это сообщение\n"
            ))

        else:
            self._json_response(404, {"error": "not found", "path": path})


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{ts}] ALF healthcheck server listening on 0.0.0.0:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"[{ts}] shutting down", flush=True)
        server.shutdown()


if __name__ == "__main__":
    main()