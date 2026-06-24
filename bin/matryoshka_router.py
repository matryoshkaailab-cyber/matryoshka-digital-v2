#!/usr/bin/env python3
"""
matryoshka_router.py — Единый router MATRYOSHKA на :8400 (v0.2 с Council 2.0)
По предложению Аликса — НЕ плодить зоопарк портов.

Endpoints:
  GET  /health                    — aggregated health всех сервисов
  POST /council                   — Council 2.0 cycle (ALF "за/против" + Библиотекарь veto, async polling)
  GET  /council/<id>              — статус конкретного решения
  GET  /council/list              — список последних решений
  POST /alf/query                 — proxy ALF стратег (inbox/alf)
  POST /alf-librarian/...         — proxy Библиотекарь (fact-check, veto, search)
  POST /alina/query               — proxy ALINA

23.06.2026 — Фаза 2 v0.2 + Council 2.0 (гибридный async polling pattern)
"""
import asyncio
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

PORT = 8400

# Endpoints of inner services
ALF_LIBRARIAN_URL = "http://127.0.0.1:8461"
ALF_INBOX_DIR = "/root/matryoshka/swarm/inbox/alf"
ALF_OUTBOX_DIR = "/root/matryoshka/swarm/outbox/alf"
ALF_ARCHIVE_DIR = "/root/matryoshka/swarm/archive"
COUNCIL_LOGS_DIR = "/root/matryoshka/council/logs"
ALINA_PROXY_URL = "http://127.0.0.1:8470"

# Council 2.0 config
COUNCIL_ALF_TIMEOUT = 90  # максимум ждём ALF (увеличено с 60 — для стабильности)
COUNCIL_ALF_POLL_INTERVAL = 2  # как часто проверяем

# Council state (in-memory + persist to file)
COUNCIL_STATE = {
    "decisions": {},  # council_id → state
}

# Startup
STARTED_AT = datetime.now(timezone.utc).isoformat()
Path(COUNCIL_LOGS_DIR).mkdir(parents=True, exist_ok=True)


def proxy_request(url, method, body=None, timeout=60):
    """Proxy HTTP request to inner service."""
    try:
        data = None
        headers = {}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {}
        return e.code, {"error": str(e), "url": url, "body": body}
    except Exception as e:
        return 500, {"error": str(e), "url": url}


def health_aggregated():
    """Опросить health всех сервисов и собрать агрегированный статус."""
    services = {}

    code, body = proxy_request(f"{ALF_LIBRARIAN_URL}/health", "GET", timeout=5)
    services["alf-librarian"] = {"status": "ok" if code == 200 else "down", "http_code": code, "url": ALF_LIBRARIAN_URL}

    try:
        r = urllib.request.Request("http://127.0.0.1:8452/health")
        with urllib.request.urlopen(r, timeout=3) as resp:
            services["alf-strateg"] = {"status": "ok", "http_code": 200, "url": "http://127.0.0.1:8452"}
    except Exception as e:
        services["alf-strateg"] = {"status": "down", "error": str(e)}

    services["alina"] = {"status": "skipped (separate case)", "url": ALINA_PROXY_URL}
    services["matryoshka-router"] = {"status": "ok", "url": f"http://127.0.0.1:{PORT}"}

    overall = "ok" if all(
        s.get("status") == "ok" for s in services.values()
        if s.get("status") != "skipped (separate case)"
    ) else "degraded"
    return {
        "overall": overall,
        "router": "matryoshka-router",
        "version": "v0.2 (Council 2.0)",
        "started_at": STARTED_AT,
        "services": services
    }


def write_alf_task(question: str, task_id: str = None) -> dict:
    """Write task to ALF inbox."""
    if not task_id:
        task_id = f"router-alf-{int(time.time())}"
    task = {"task_id": task_id, "question": question}
    os.makedirs(ALF_INBOX_DIR, exist_ok=True)
    path = os.path.join(ALF_INBOX_DIR, f"{task_id}.json")
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(task, f)
        f.flush()
        os.fsync(f.fileno())
    os.rename(tmp, path)
    return {"task_id": task_id, "inbox_path": path}


def council_send_to_alf(decision_text: str, council_id: str) -> str:
    """Отправить ALF задачу через inbox. Возвращает task_id."""
    task_id = f"council-{council_id}"
    # Короткий промпт — M3 не тянет длинные
    question = (
        f"Council голосование #{council_id[:8]}. Решение: '{decision_text[:200]}'. "
        f"Твой голос: за или против? Одним предложением, начни с 'ЗА' или 'ПРОТИВ'."
    )
    write_alf_task(question, task_id)
    return task_id


def council_check_alf_response(council_id: str) -> dict:
    """Проверить archive/outbox на ответ ALF по council_id. Возвращает dict с vote/reason/raw."""
    task_id = f"council-{council_id}"

    # 1. Archive (canonical source)
    archive_path = Path(ALF_ARCHIVE_DIR)
    if archive_path.exists():
        try:
            for fname in os.listdir(archive_path):
                if task_id in fname and fname.endswith(".json"):
                    with open(archive_path / fname) as fh:
                        d = json.load(fh)
                    output = d.get("output", "")
                    output_lower = output.lower().strip()
                    if output_lower.startswith("за"):
                        vote = "for"
                    elif output_lower.startswith("против"):
                        vote = "against"
                    else:
                        vote = "unclear"
                    return {
                        "found": True,
                        "vote": vote,
                        "reason": output[:500],
                        "source_file": f"archive/{fname}"
                    }
        except OSError:
            pass

    # 2. Outbox + .notified
    outbox_path = Path(ALF_OUTBOX_DIR)
    for sub in [outbox_path, outbox_path / ".notified"]:
        if not sub.exists():
            continue
        try:
            for fname in os.listdir(sub):
                if task_id in fname and fname.endswith(".json"):
                    with open(sub / fname) as fh:
                        d = json.load(fh)
                    output = d.get("output", "")
                    output_lower = output.lower().strip()
                    if output_lower.startswith("за"):
                        vote = "for"
                    elif output_lower.startswith("против"):
                        vote = "against"
                    else:
                        vote = "unclear"
                    return {
                        "found": True,
                        "vote": vote,
                        "reason": output[:500],
                        "source_file": fname
                    }
        except OSError:
            continue

    return {"found": False}


def council_decide(council_id: str, alf_vote: str, librarian_veto: dict) -> dict:
    """Финальное решение Council на основе двух голосов."""
    alf_vote = alf_vote or "null"
    lib_veto = bool(librarian_veto.get("veto"))

    if lib_veto:
        return {
            "decision": "rejected",
            "reason": f"Библиотекарь veto: {librarian_veto.get('reason', 'unknown')}",
            "by": "alf-librarian"
        }

    if alf_vote == "against":
        return {
            "decision": "rejected",
            "reason": "ALF проголосовал ПРОТИВ",
            "by": "alf-strateg"
        }

    if alf_vote == "for":
        return {
            "decision": "accepted",
            "reason": "ALF за + Библиотекарь не vetoed",
            "by": "council"
        }

    if alf_vote == "unclear":
        return {
            "decision": "accepted",
            "reason": "ALF ответ unclear (fallback на Библиотекаря не vetoed)",
            "by": "council (alf fallback)"
        }

    # alf_vote == "null" (timeout)
    return {
        "decision": "accepted",
        "reason": f"ALF не ответил за {COUNCIL_ALF_TIMEOUT}s — fallback на Библиотекаря (не vetoed)",
        "by": "council (alf timeout)"
    }


def council_finalize(council_id: str, alf_vote: str, alf_reason: str, librarian_review: dict):
    """Завершить Council, persist в файл, обновить state."""
    decision = council_decide(council_id, alf_vote, librarian_review)

    final = {
        "council_id": council_id,
        "alf": {"vote": alf_vote, "reason": alf_reason[:500] if alf_reason else None},
        "librarian": librarian_review,
        "decision": decision["decision"],
        "reason": decision["reason"],
        "decided_by": decision["by"],
        "decided_at": datetime.now(timezone.utc).isoformat(timespec="seconds")
    }

    # Update in-memory state
    if council_id in COUNCIL_STATE["decisions"]:
        COUNCIL_STATE["decisions"][council_id].update({
            "status": "completed",
            "alf_vote": alf_vote,
            "alf_reason": alf_reason[:500] if alf_reason else None,
            "librarian_review": librarian_review,
            "final": final,
            "completed_at": final["decided_at"]
        })

    # Persist to file
    log_path = Path(COUNCIL_LOGS_DIR) / f"{council_id}.json"
    log_path.write_text(json.dumps(final, indent=2, ensure_ascii=False))

    return final


def council_poll_alf(council_id: str, deadline: float) -> dict:
    """Polling ответа ALF до deadline."""
    while time.time() < deadline:
        result = council_check_alf_response(council_id)
        if result.get("found"):
            return result
        time.sleep(COUNCIL_ALF_POLL_INTERVAL)
    return {"found": False}


def council_start(decision_text: str, council_id: str = None) -> dict:
    """Запустить Council 2.0 cycle. Возвращает initial response."""
    if not council_id:
        council_id = f"council-{int(time.time())}-{os.urandom(2).hex()}"

    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Step 1: Send to ALF (async, через inbox)
    alf_task_id = council_send_to_alf(decision_text, council_id)
    alf_deadline = time.time() + COUNCIL_ALF_TIMEOUT

    # Step 2: Librarian veto (sync, 35s timeout)
    code, librarian_review = proxy_request(
        f"{ALF_LIBRARIAN_URL}/veto",
        "POST",
        body={"council_decision": decision_text},
        timeout=35
    )

    # Persist initial state
    COUNCIL_STATE["decisions"][council_id] = {
        "council_id": council_id,
        "decision": decision_text,
        "started_at": started_at,
        "alf_task_id": alf_task_id,
        "alf_deadline": alf_deadline,
        "librarian_review": librarian_review,
        "status": "pending_alf",
        "librarian_completed_at": datetime.now(timezone.utc).isoformat(timespec="seconds")
    }
    # Initial log
    log_path = Path(COUNCIL_LOGS_DIR) / f"{council_id}.json"
    log_path.write_text(json.dumps({
        "council_id": council_id,
        "decision": decision_text,
        "started_at": started_at,
        "alf_task_id": alf_task_id,
        "librarian_review": librarian_review,
        "status": "pending_alf"
    }, indent=2, ensure_ascii=False))

    # Step 3: Poll ALF
    alf_result = council_poll_alf(council_id, alf_deadline)

    if alf_result.get("found"):
        alf_vote = alf_result.get("vote", "unclear")
        alf_reason = alf_result.get("reason", "")
    else:
        alf_vote = None
        alf_reason = f"ALF не ответил за {COUNCIL_ALF_TIMEOUT}s"

    # Finalize
    final = council_finalize(council_id, alf_vote, alf_reason, librarian_review)

    return final


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
            self._json(200, health_aggregated())

        elif path == "/council/list":
            recent = sorted(
                COUNCIL_STATE["decisions"].items(),
                key=lambda x: x[1].get("started_at", ""),
                reverse=True
            )
            summary = {
                cid: {
                    "decision": d.get("decision", "")[:80],
                    "status": d.get("status"),
                    "started_at": d.get("started_at")
                }
                for cid, d in recent[:50]
            }
            self._json(200, {"total": len(COUNCIL_STATE["decisions"]), "recent": summary})

        elif path.startswith("/council/") and len(path) > len("/council/"):
            # /council/<id>
            council_id = path[len("/council/"):]
            if council_id in COUNCIL_STATE["decisions"]:
                self._json(200, COUNCIL_STATE["decisions"][council_id])
            else:
                # Try load from file
                log_path = Path(COUNCIL_LOGS_DIR) / f"{council_id}.json"
                if log_path.exists():
                    self._json(200, json.loads(log_path.read_text()))
                else:
                    self._json(404, {"error": "council_id not found", "council_id": council_id})

        elif path == "/" or path == "/docs":
            self._json(200, {
                "service": "matryoshka-router",
                "version": "v0.2 (Council 2.0, 23.06.2026)",
                "endpoints": {
                    "GET /health": "aggregated health всех сервисов",
                    "POST /council": '{"decision": "...", "decision_id": "..."} → Council 2.0 cycle (sync polling ALF до 60s)',
                    "GET /council/<id>": "статус конкретного решения (in-memory или из /council/logs/)",
                    "GET /council/list": "список последних 50 council решений",
                    "POST /alf/query": '{"question": "..."} → записать в ALF inbox',
                    "POST /alf-librarian/fact-check": '{"query": "...", "text": "..."} → proxy',
                    "POST /alf-librarian/veto": '{"council_decision": "..."} → proxy',
                    "POST /alf-librarian/search": '{"query": "..."} → proxy',
                    "POST /alina/query": '{"message": "..."} → proxy ALINA (отдельный кейс)'
                },
                "council_decision_logic": {
                    "alf_against": "rejected",
                    "librarian_veto": "rejected",
                    "alf_for + librarian_ok": "accepted",
                    "alf_unclear + librarian_ok": "accepted (fallback)",
                    "alf_null (timeout) + librarian_ok": "accepted (timeout fallback)",
                    "alf_null + librarian_veto": "rejected"
                }
            })

        else:
            self._json(404, {"error": "not found", "path": path})

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/council":
            decision = body.get("decision", "")
            council_id = body.get("decision_id")
            if not decision:
                self._json(400, {"error": "'decision' required"})
                return
            final = council_start(decision, council_id)
            status_code = 200 if final["decision"] == "accepted" else 403
            self._json(status_code, final)

        elif path == "/alf/query":
            question = body.get("question", "")
            if not question:
                self._json(400, {"error": "'question' required"})
                return
            result = write_alf_task(question)
            self._json(202, result)

        elif path == "/alf-librarian/fact-check":
            code, resp = proxy_request(f"{ALF_LIBRARIAN_URL}/fact-check", "POST", body=body, timeout=30)
            self._json(code, resp)
        elif path == "/alf-librarian/veto":
            code, resp = proxy_request(f"{ALF_LIBRARIAN_URL}/veto", "POST", body=body, timeout=35)
            self._json(code, resp)
        elif path == "/alf-librarian/search":
            code, resp = proxy_request(f"{ALF_LIBRARIAN_URL}/search", "POST", body=body, timeout=30)
            self._json(code, resp)

        elif path == "/alina/query":
            code, resp = proxy_request(f"{ALINA_PROXY_URL}/message", "POST", body=body, timeout=30)
            self._json(code, resp)

        else:
            self._json(404, {"error": "not found", "path": path})


def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{ts}] MATRYOSHKA Router v0.2 (Council 2.0) on 0.0.0.0:{PORT}", flush=True)
    print(f"[{ts}] Proxy: ALF-librarian={ALF_LIBRARIAN_URL}, ALINA={ALINA_PROXY_URL}", flush=True)
    print(f"[{ts}] Council 2.0: ALF timeout {COUNCIL_ALF_TIMEOUT}s, poll {COUNCIL_ALF_POLL_INTERVAL}s", flush=True)

    Path("/var/log/matryoshka").mkdir(parents=True, exist_ok=True)
    Path("/var/log/matryoshka/router.state").write_text(
        f"started_at={STARTED_AT}\nport={PORT}\nversion=v0.2\n"
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"[{ts}] shutting down", flush=True)
        server.shutdown()


if __name__ == "__main__":
    main()