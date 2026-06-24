#!/usr/bin/env python3
"""
swarm_send.py — отправка задачи агенту роя.

Использование:
    python3 swarm_send.py alex "команда"
    python3 swarm_send.py alf "аналитика по рынку X"
    python3 swarm_send.py alisa "сделай пост про DATALINK PRO"

Записывает JSON в /root/matryoshka/swarm/inbox/<agent>/<task_id>.json
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

SWARM_BASE = Path("/root/matryoshka/swarm")
AGENTS = ["alex", "alf", "alisa"]


def send(target: str, command: str, context: str = "", timeout: int = 300) -> dict:
    if target not in AGENTS:
        return {"ok": False, "error": f"unknown agent: {target}"}
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    task = {
        "task_id": task_id,
        "from": "hermes",
        "to": target,
        "command": command,
        "context": context,
        "timeout": timeout,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    inbox_dir = SWARM_BASE / "inbox" / target
    inbox_dir.mkdir(parents=True, exist_ok=True)
    inbox_file = inbox_dir / f"{task_id}.json"
    inbox_file.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "task_id": task_id, "inbox": str(inbox_file)}


def main():
    ap = argparse.ArgumentParser(description="Send task to swarm agent")
    ap.add_argument("target", choices=AGENTS)
    ap.add_argument("command")
    ap.add_argument("--context", default="")
    ap.add_argument("--timeout", type=int, default=300)
    args = ap.parse_args()
    result = send(args.target, args.command, args.context, args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 1)


# ALEX enforcement (19.06.2026): Obsidian must be fresh before sending LLM tasks
import subprocess as _enforce_sp
_enforce_r = _enforce_sp.run(["python3", "/usr/local/bin/hermes_obsidian_enforce.py"], capture_output=True, text=True, timeout=30)
if _enforce_r.returncode == 2:
    print(f"[ENFORCE] BLOCKED: {_enforce_r.stdout}", file=__import__('sys').stderr)
    print(json.dumps({"ok": False, "error": "Obsidian stale or invalid", "enforce_output": _enforce_r.stdout}, ensure_ascii=False))
    __import__('sys').exit(2)

if __name__ == "__main__":
    main()
