#!/usr/bin/env python3
"""
swarm_watchdog.py — проверяет задачи в inbox/, которые висят дольше timeout.
Помечает как timed_out, переносит в archive/timed_out/ и пишет в poller.log.

Запуск через cron: */5 * * * * root python3 /root/matryoshka/bin/swarm_watchdog.py
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

SWARM_BASE = Path("/root/matryoshka/swarm")
INBOX = SWARM_BASE / "inbox"
ARCHIVE = SWARM_BASE / "archive" / "timed_out"
POLLER_LOG = Path("/var/log/swarm/poller.log")
DEFAULT_TIMEOUT = 300  # 5 минут


def log(msg: str):
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {watchdog_TAG} {msg}"
    print(line, flush=True)
    try:
        POLLER_LOG.parent.mkdir(parents=True, exist_ok=True)
        with POLLER_LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


watchdog_TAG = "WATCHDOG"


def check_stale_tasks():
    now = datetime.now().timestamp()
    moved = 0
    for agent_dir in INBOX.iterdir():
        if not agent_dir.is_dir():
            continue
        for task_file in agent_dir.glob("*.json"):
            try:
                task = json.loads(task_file.read_text(encoding="utf-8"))
                ct = task.get("created_at"); created = datetime.fromisoformat(ct).timestamp() if ct else task_file.stat().st_mtime
                timeout = task.get("timeout", DEFAULT_TIMEOUT)
                age = now - created
                if age > timeout:
                    task_id = task.get("task_id", "?")
                    log(f"TIMEOUT task_id={task_id} from={agent_dir.name} age={age:.0f}s > timeout={timeout}s")
                    ARCHIVE.mkdir(parents=True, exist_ok=True)
                    # Mark as timed_out
                    task["status"] = "timed_out"
                    task["timed_out_at"] = datetime.now().isoformat(timespec="seconds")
                    # Write result to outbox so poller picks up
                    result = {
                        "task_id": task_id,
                        "from": agent_dir.name,
                        "to": "hermes",
                        "status": "timed_out",
                        "ok": False,
                        "output": "",
                        "error": f"Task exceeded timeout ({timeout}s) and was aborted by watchdog",
                        "executed_by": "WATCHDOG",
                        "finished_at": datetime.now().isoformat(timespec="seconds"),
                    }
                    outbox_file = SWARM_BASE / "outbox" / agent_dir.name / f"{task_id}.json"
                    outbox_file.parent.mkdir(parents=True, exist_ok=True)
                    outbox_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                    # Move task from inbox to archive
                    shutil.move(str(task_file), str(ARCHIVE / task_file.name))
                    moved += 1
            except Exception as e:
                log(f"ERROR processing {task_file}: {e}")
    return moved


def main():
    moved = check_stale_tasks()
    if moved:
        log(f"moved {moved} timed_out task(s) to archive")
    else:
        log("no stale tasks")


if __name__ == "__main__":
    main()
