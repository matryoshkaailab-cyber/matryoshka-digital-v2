#!/usr/bin/env python3
"""
mimo_query.py — HTTP адаптер для MiMo CLI (subprocess wrapper)
23.06.2026 — Phase 2 v3 (MiMo интеграция)

Endpoints:
  GET  /health    — alive check
  POST /query     — {question, timeout_sec} → {output, model, elapsed_sec, ok}
  GET  /models    — список доступных моделей

Реализация: subprocess.run("mimo run <question>") — медленнее чем HTTP API,
но это единственный рабочий способ пока mimo acp / mimo serve не работают.
"""
import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

PORT = 8402
MIMO_BIN = "/usr/local/lib/python3.12/dist-packages/nodejs_wheel/lib/node_modules/@mimo-ai/cli/node_modules/@mimo-ai/mimocode-linux-x64/bin/mimo"
WORK_DIR = "/tmp/mimo-test"
DEFAULT_TIMEOUT = 60
MAX_CONCURRENT = 2  # MiMo CLI не любит concurrent запуски

# Rate limit + concurrency control
_rate_lock = threading.Lock()
_active_count = 0

STARTED_AT = datetime.now(timezone.utc).isoformat()


def run_mimo(question: str, model: str = "mimo-auto", timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Запустить mimo run через subprocess и вернуть результат."""
    global _active_count
    with _rate_lock:
        if _active_count >= MAX_CONCURRENT:
            return {
                "ok": False,
                "error": f"busy: {_active_count} active requests",
                "elapsed_sec": 0
            }
        _active_count += 1

    try:
        start = time.time()
        cmd = [MIMO_BIN, "run", "--model", model, question]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=WORK_DIR
        )
        elapsed = round(time.time() - start, 2)
        output = result.stdout.strip()
        # Удаляем префиксы типа "> build · mimo-auto"
        lines = output.split("\n")
        clean_lines = []
        for line in lines:
            if line.startswith(">") or "build" in line[:20]:
                continue
            if line.strip():
                clean_lines.append(line)
        clean_output = "\n".join(clean_lines).strip()
        if not clean_output:
            clean_output = output
        return {
            "ok": result.returncode == 0,
            "output": clean_output,
            "stderr": result.stderr[-500:] if result.stderr else "",
            "returncode": result.returncode,
            "elapsed_sec": elapsed,
            "model": model,
            "tokens_estimate": len(clean_output) // 4
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"timeout after {timeout}s",
            "elapsed_sec": timeout,
            "model": model
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"exception: {e}",
            "elapsed_sec": 0
        }
    finally:
        with _rate_lock:
            _active_count = max(0, _active_count - 1)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        msg = f"[{ts}] {self.address_string()} {fmt % args}"
        print(msg, flush=True)

    def _json(self, status, data):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(body)
        except Exception:
            return {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            with _rate_lock:
                active = _active_count
            self._json(200, {
                "status": "ok",
                "service": "mimo-query-adapter",
                "version": "v0.1 (23.06.2026)",
                "mimo_bin": MIMO_BIN,
                "work_dir": WORK_DIR,
                "started_at": STARTED_AT,
                "active_requests": active,
                "max_concurrent": MAX_CONCURRENT
            })
        elif path == "/models":
            self._json(200, {
                "models": [
                    {"id": "mimo-auto", "name": "MiMo Auto (free, Xiaomi hosted)"},
                    {"id": "xiaomi/mimo-v2-flash", "name": "MiMo V2 Flash"},
                    {"id": "xiaomi/mimo-v2-omni", "name": "MiMo V2 Omni"},
                    {"id": "xiaomi/mimo-v2-pro", "name": "MiMo V2 Pro"},
                    {"id": "xiaomi/mimo-v2.5", "name": "MiMo V2.5 (1M context)"},
                    {"id": "xiaomi/mimo-v2.5-pro", "name": "MiMo V2.5 Pro"},
                    {"id": "xiaomi/mimo-v2.5-pro-ultraspeed", "name": "MiMo V2.5 Pro Ultr高速"},
                ],
                "default": "mimo-auto",
                "note": "MiMo CLI 0.1.2 — mimo-auto (Xiaomi hosted, free, без auth)"
            })
        else:
            self._json(404, {"error": "not found", "path": path})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/query":
            question = body.get("question") or body.get("message") or body.get("text")
            model = body.get("model", "mimo-auto")
            timeout = body.get("timeout_sec", DEFAULT_TIMEOUT)
            if not question:
                self._json(400, {"error": "'question' required"})
                return
            if timeout > 180:
                timeout = 180  # max timeout
            result = run_mimo(question, model=model, timeout=timeout)
            self._json(200 if result.get("ok") else 500, result)
        else:
            self._json(404, {"error": "not found", "path": path})


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{ts}] MiMo Query Adapter v0.1 on 0.0.0.0:{PORT}", flush=True)
    print(f"[{ts}] MiMo binary: {MIMO_BIN}", flush=True)
    print(f"[{ts}] Work dir: {WORK_DIR}", flush=True)
    print(f"[{ts}] Max concurrent: {MAX_CONCURRENT}", flush=True)

    Path("/var/log/matryoshka").mkdir(parents=True, exist_ok=True)
    Path("/var/log/matryoshka/mimo-query.state").write_text(
        f"started_at={STARTED_AT}\nport={PORT}\n"
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"[{ts}] shutting down", flush=True)
        server.shutdown()


if __name__ == "__main__":
    main()