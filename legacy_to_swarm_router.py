#!/usr/bin/env python3
"""
Legacy → Swarm router. Мониторит /root/matryoshka/.hermes_task.json
(который теперь symlink) и автоматически копирует содержимое в
/root/matryoshka/swarm/inbox/alex/<task_id>.json.

Создан 19.06.2026 16:30 MSK — фикс «два непересекающихся канала».
"""
import os, json, time, shutil
from pathlib import Path

LEGACY = Path("/root/matryoshka/.hermes_task.json")
SWARM_INBOX = Path("/root/matryoshka/swarm/inbox/alex")
SWARM_INBOX.mkdir(parents=True, exist_ok=True)


def main():
    if not LEGACY.exists():
        return None
    try:
        data = json.loads(LEGACY.read_text(encoding="utf-8"))
    except Exception:
        return None
    task_id = data.get("task_id", f"unknown-{int(time.time())}")
    dest = SWARM_INBOX / f"{task_id}.json"
    if dest.exists():
        return None  # уже доставлено
    shutil.copy(LEGACY, dest)
    return task_id


if __name__ == "__main__":
    tid = main()
    print(f"routed: {tid}" if tid else "no new task")
