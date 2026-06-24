#!/usr/bin/env python3
"""
alf_librarian.py — ALF-Библиотекарь (Python-агент)
HTTP сервер на :8461. Не LLM — Python + grep по локальной KB + правила.

v2 (23.06.2026): добавлены filelock для WAL writes, graceful shutdown, rate limit.

Endpoints:
  GET  /health          — alive check
  POST /fact-check      — {query, text} → {verdict, confidence, sources}
  POST /veto            — {council_decision} → {veto: bool, reason, timeout:30s}
  POST /search          — поиск по ai-knowledge/*.md (локальный fallback)
"""
import asyncio
import fcntl
import json
import re
import signal
import sys
import time
import subprocess
import threading
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

PORT = 8461
KB_DIR = Path("/root/matryoshka/alf/knowledge")
TIMEOUT_VETO = 30  # seconds
STATE_FILE = "/var/log/matryoshka/alf_librarian.state"
WAL_LOCK_FILE = "/var/lock/alf_librarian_wal.lock"

# Rate limiting (in-memory, per-IP)
RATE_LIMIT_WINDOW_SEC = 60
RATE_LIMIT_MAX_REQUESTS = 60
_rate_limit_lock = threading.Lock()
_rate_limit_data = {}  # ip -> [(timestamp, count), ...]

# Shutdown flag (для graceful shutdown)
_shutdown_event = threading.Event()

# Startup time
STARTED_AT = datetime.now(timezone.utc).isoformat()


def check_rate_limit(ip: str) -> bool:
    """Простой sliding window rate limit. Возвращает True если можно, False если превышен."""
    now = time.time()
    with _rate_limit_lock:
        if ip not in _rate_limit_data:
            _rate_limit_data[ip] = []
        # Чистим старые записи
        _rate_limit_data[ip] = [
            t for t in _rate_limit_data[ip] if now - t < RATE_LIMIT_WINDOW_SEC
        ]
        if len(_rate_limit_data[ip]) >= RATE_LIMIT_MAX_REQUESTS:
            return False
        _rate_limit_data[ip].append(now)
        return True


def search_kb(query: str, max_results: int = 5) -> list:
    """Поиск по ai-knowledge/*.md через grep. Возвращает список (file, snippet, score)."""
    results = []
    query_words = [w.lower() for w in re.findall(r'\w+', query.lower()) if len(w) > 2]
    if not query_words:
        return results

    for md_file in KB_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            content_lower = content.lower()
            score = sum(content_lower.count(w) for w in query_words)
            if score > 0:
                snippet = ""
                for line in content.split("\n"):
                    line_lower = line.lower()
                    if any(w in line_lower for w in query_words):
                        snippet = line.strip()[:200]
                        break
                rel_path = md_file.relative_to(KB_DIR)
                results.append({
                    "file": str(rel_path),
                    "score": score,
                    "snippet": snippet
                })
        except Exception:
            continue

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:max_results]


def fact_check(query: str, text: str) -> dict:
    """Проверка фактов в text на основе KB. Возвращает verdict + confidence + sources."""
    sources = search_kb(text or query, max_results=5)

    if not sources:
        return {
            "verdict": "unknown",
            "confidence": 0.0,
            "sources": [],
            "reason": "No relevant sources found in local KB"
        }

    top_score = sources[0]["score"] if sources else 0
    if top_score >= 5:
        verdict = "supported"
        confidence = 0.9
    elif top_score >= 3:
        verdict = "likely_supported"
        confidence = 0.7
    elif top_score >= 1:
        verdict = "uncertain"
        confidence = 0.4
    else:
        verdict = "unsupported"
        confidence = 0.2

    return {
        "verdict": verdict,
        "confidence": confidence,
        "sources": [{"file": s["file"], "snippet": s["snippet"]} for s in sources[:3]],
        "top_score": top_score
    }


def veto(council_decision: str) -> dict:
    """Veto Библиотекаря. Timeout 30s — Аликс правильно поправил (ALF не должен быть bottleneck)."""
    sources = search_kb(council_decision, max_results=3)
    if not sources:
        return {
            "veto": False,
            "reason": "No KB sources found — Библиотекарь не может veto без данных",
            "sources": []
        }

    decision_lower = council_decision.lower()
    is_negative = any(w in decision_lower for w in ["не делай", "stop", "block", "отказ", "veto", "no"])
    is_positive = any(w in decision_lower for w in ["разрешаю", "ok", "do", "yes", "согласен", "ок"])

    if is_negative and not sources:
        return {"veto": True, "reason": "Decision is negative but no KB support", "sources": []}

    if is_positive and sources:
        return {"veto": False, "reason": "Decision is positive and KB supports", "sources": [s["file"] for s in sources]}

    return {
        "veto": False,
        "reason": "No clear KB conflict detected — trusting HERMES",
        "sources": [s["file"] for s in sources[:3]]
    }


def write_to_wal_safe(wal_msg: str, timeout: int = 5) -> bool:
    """Thread-safe запись в shared_brain WAL через filelock. Возвращает True если успешно."""
    try:
        Path(WAL_LOCK_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(WAL_LOCK_FILE, "w") as lock_fd:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                result = subprocess.run(
                    ["python3", "/root/matryoshka/shared_brain/append_wal.py", "alf", wal_msg],
                    capture_output=True, timeout=timeout
                )
                return result.returncode == 0
            finally:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
    except (BlockingIOError, OSError) as e:
        # Lock занят другим процессом — пропускаем, log не критичен
        return False
    except Exception as e:
        return False


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

    def _text(self, status, text):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
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
        if _shutdown_event.is_set():
            self._json(503, {"error": "shutting down"})
            return

        # Rate limit
        if not check_rate_limit(self.client_address[0]):
            self._json(429, {"error": f"rate limit exceeded ({RATE_LIMIT_MAX_REQUESTS}/{RATE_LIMIT_WINDOW_SEC}s)"})
            return

        path = urlparse(self.path).path

        if path == "/health":
            self._json(200, {
                "status": "ok",
                "service": "alf-librarian",
                "version": "v2 (23.06.2026, +filelock+graceful+ratelimit)",
                "started_at": STARTED_AT,
                "kb_dir": str(KB_DIR),
                "kb_files": len(list(KB_DIR.rglob("*.md")))
            })
        elif path == "/" or path == "/docs":
            self._text(200, (
                "ALF Librarian v2 (Библиотекарь MATRYOSHKA) — Python HTTP :8461\n"
                "Endpoints:\n"
                "  GET /health   — alive check\n"
                "  POST /fact-check  — {query, text} → verdict, confidence, sources\n"
                "  POST /veto    — {council_decision} → {veto, reason, timeout:30s}\n"
                "  POST /search   — {query} → top sources from KB\n"
                f"Rate limit: {RATE_LIMIT_MAX_REQUESTS} req per {RATE_LIMIT_WINDOW_SEC}s per IP\n"
            ))
        else:
            self._json(404, {"error": "not found", "path": path})

    def do_POST(self):
        if _shutdown_event.is_set():
            self._json(503, {"error": "shutting down"})
            return

        # Rate limit
        if not check_rate_limit(self.client_address[0]):
            self._json(429, {"error": f"rate limit exceeded ({RATE_LIMIT_MAX_REQUESTS}/{RATE_LIMIT_WINDOW_SEC}s)"})
            return

        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/fact-check":
            query = body.get("query", "")
            text = body.get("text", "")
            if not query and not text:
                self._json(400, {"error": "either 'query' or 'text' required"})
                return
            result = fact_check(query, text)
            result["checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            self._json(200, result)

        elif path == "/veto":
            decision = body.get("council_decision", "")
            if not decision:
                self._json(400, {"error": "'council_decision' required"})
                return
            start = time.time()
            result = veto(decision)
            result["elapsed_sec"] = round(time.time() - start, 3)
            result["timeout_sec"] = TIMEOUT_VETO
            result["checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            # WAL write через filelock (thread-safe)
            wal_msg = f"VETO request: decision='{decision[:100]}', veto={result.get('veto')}, reason='{result.get('reason','')[:80]}'"
            wal_ok = write_to_wal_safe(wal_msg)
            result["wal_recorded"] = wal_ok
            self._json(200, result)

        elif path == "/search":
            query = body.get("query", "")
            if not query:
                self._json(400, {"error": "'query' required"})
                return
            results = search_kb(query, max_results=10)
            self._json(200, {
                "query": query,
                "count": len(results),
                "results": results
            })

        else:
            self._json(404, {"error": "not found", "path": path})


def graceful_shutdown(signum, frame):
    """Signal handler для SIGTERM/SIGINT — закрываем server gracefully."""
    print(f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] Signal {signum} received — initiating graceful shutdown", flush=True)
    _shutdown_event.set()
    # Даём 5 сек на завершение текущих запросов
    import threading
    def stop_server():
        time.sleep(2)
        try:
            httpd.shutdown()
        except Exception:
            pass
    threading.Thread(target=stop_server, daemon=True).start()


def main():
    # Регистрируем signal handlers
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    server = HTTPServer(("0.0.0.0", PORT), Handler)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{ts}] ALF-Библиотекарь v2 listening on 0.0.0.0:{PORT}", flush=True)
    print(f"[{ts}] KB dir: {KB_DIR}", flush=True)
    print(f"[{ts}] KB files: {len(list(KB_DIR.rglob('*.md')))}", flush=True)
    print(f"[{ts}] Veto timeout: {TIMEOUT_VETO}s, rate limit: {RATE_LIMIT_MAX_REQUESTS}/{RATE_LIMIT_WINDOW_SEC}s", flush=True)

    Path(STATE_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(STATE_FILE).write_text(f"started_at={STARTED_AT}\nport={PORT}\nversion=v2\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        graceful_shutdown(signal.SIGINT, None)
    finally:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"[{ts}] ALF-Библиотекарь stopped", flush=True)
        try:
            server.server_close()
        except Exception:
            pass


if __name__ == "__main__":
    main()