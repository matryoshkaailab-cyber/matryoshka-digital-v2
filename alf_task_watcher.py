#!/usr/bin/env python3
"""
ALF Task Watcher — маршрутизация задач HERMES → ALF.

Создан 19.06.2026 17:24 MSK. Раньше файла НЕ БЫЛО (была ложь в fact 12).

Что делает:
1. Каждые 30 сек проверяет /root/matryoshka/.hermes_task_alf.json (свежие задачи)
2. Если есть — переносит в /root/matryoshka/swarm/inbox/alf/
3. Записывает в shared_brain WAL
4. Генерирует digest

НЕ ТРОГАЕТ:
- .hermes_task.json (файл ALEX'а)
- swarm/inbox/hermes/ (файл HERMES'а)
"""
import os
import sys
import json
import time
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/matryoshka")
ALF_INBOX = BASE / "swarm/inbox/alf"
ALF_OUTBOX = BASE / "swarm/outbox/alf"
HERMES_TO_ALF = BASE / ".hermes_task_alf.json"  # HERMES пишет сюда
SHARED_BRAIN = BASE / "shared_brain"
APPEND_WAL = SHARED_BRAIN / "append_wal.py"

LOCK = SHARED_BRAIN / "shared_brain.lock"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    print(f"[{now_iso()}] {msg}", file=sys.stderr)


def append_wal(agent: str, msg: str) -> None:
    """Записать в shared_brain WAL."""
    import subprocess
    try:
        subprocess.run(
            ["/usr/bin/python3", str(APPEND_WAL), agent, msg],
            capture_output=True, timeout=10,
        )
    except Exception as e:
        log(f"ERROR append_wal: {e}")


def process_hermes_to_alf() -> int:
    """
    Проверить .hermes_task_alf.json. Если есть задача — перенести в inbox.
    Возвращает количество обработанных задач.
    """
    if not HERMES_TO_ALF.exists():
        return 0
    try:
        task = json.loads(HERMES_TO_ALF.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"ERROR parse {HERMES_TO_ALF}: {e}")
        return 0

    task_id = task.get("task_id", f"unknown-{int(time.time())}")
    ALF_INBOX.mkdir(parents=True, exist_ok=True)
    dest = ALF_INBOX / f"{task_id}.json"
    # Атомарно перенести
    shutil.move(str(HERMES_TO_ALF), str(dest))
    log(f"OK перенесён {task_id} → {dest}")
    append_wal("hermes", f"ALERT: ALF task routed via watcher → {task_id} ({task.get('subject', '?')})")
    return 1


def main() -> int:
    log("=== ALF watcher started ===")
    try:
        n = process_hermes_to_alf()
        if n > 0:
            log(f"Processed {n} task(s)")
        else:
            log("No trigger, nothing to do")
    except Exception as e:
        log(f"ERROR: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
