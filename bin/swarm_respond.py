#!/usr/bin/env python3
"""
swarm_respond.py — hook для профилей Hermes (alf, alisa).

Когда агент профиля хочет ответить HERMES-у, он вызывает:
    python3 swarm_respond.py <task_id> --ok --output "результат"

Или hook автоматически вызывает при завершении сессии.

Пишет в /root/matryoshka/swarm/outbox/<agent>/<task_id>.json
"""
import argparse
import json
import sys
import os
from datetime import datetime
from pathlib import Path

SWARM_BASE = Path("/root/matryoshka/swarm")


def get_my_agent_name() -> str:
    """Определяет имя агента по переменной окружения HERMES_PROFILE."""
    profile = os.environ.get("HERMES_PROFILE", "")
    mapping = {
        "alf": "alf",
        "alisa": "alisa",
        "alex": "alex",
    }
    return mapping.get(profile, profile)


def respond(task_id: str, ok: bool, output: str, error: str = ""):
    agent = get_my_agent_name()
    if not agent:
        return {"ok": False, "error": "cannot determine agent name (HERMES_PROFILE not set)"}
    result = {
        "task_id": task_id,
        "from": agent,
        "to": "hermes",
        "status": "done",
        "ok": ok,
        "output": output[:50000],
        "error": (error or "")[:5000],
        "executed_by": agent.upper(),
        "finished_at": datetime.now().isoformat(timespec="seconds"),
    }
    outbox_dir = SWARM_BASE / "outbox" / agent
    outbox_dir.mkdir(parents=True, exist_ok=True)
    outbox_file = outbox_dir / f"{task_id}.json"
    outbox_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    # Remove from inbox
    inbox_file = SWARM_BASE / "inbox" / agent / f"{task_id}.json"
    if inbox_file.exists():
        inbox_file.unlink()
    return {"ok": True, "outbox": str(outbox_file)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task_id")
    ap.add_argument("--ok", action="store_true", help="success")
    ap.add_argument("--fail", action="store_true", help="failure")
    ap.add_argument("--output", default="")
    ap.add_argument("--error", default="")
    args = ap.parse_args()
    ok = args.ok and not args.fail
    result = respond(args.task_id, ok, args.output, args.error)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
