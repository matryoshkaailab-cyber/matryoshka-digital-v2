#!/usr/bin/env python3
"""
swarm_poller.py — поллер outbox для HERMES.

Запускается как cron или foreground. Каждые N секунд проверяет
/root/matryoshka/swarm/outbox/*/ и логирует завершённые задачи.

HERMES (или hook) читает лог и формирует отчёт Олегу.
"""
import json
import time
import sys
import shutil
from datetime import datetime
from pathlib import Path

SWARM_BASE = Path("/root/matryoshka/swarm")
OUTBOX = SWARM_BASE / "outbox"
ARCHIVE = SWARM_BASE / "archive"
LOG_FILE = Path("/var/log/swarm/poller.log")
POLL_INTERVAL = 15  # seconds
AGENTS = ["alex", "alf", "alisa"]


def log(msg: str):
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8-sig") as f:
            f.write(line + "\n")
    except Exception:
        pass


def process_outbox():
    """Move completed tasks from outbox/<agent>/ to archive/."""
    found = 0
    for agent in AGENTS:
        agent_outbox = OUTBOX / agent
        if not agent_outbox.exists():
            continue
        for json_file in agent_outbox.glob("*.json"):
            try:
                result = json.loads(json_file.read_text(encoding="utf-8-sig"))
                task_id = result.get("task_id", "?")
                ok = result.get("ok", False)
                agent = result.get("from", "?")
                output_preview = (result.get("output", "") or "")[:200]
                log(f"RESULT task_id={task_id} from={agent} ok={ok} output={output_preview!r}")
                # Archive
                archive_file = ARCHIVE / json_file.name
                ARCHIVE.mkdir(parents=True, exist_ok=True)
                shutil.move(str(json_file), str(archive_file))
                found += 1
            except Exception as e:
                log(f"ERROR parsing {json_file}: {e}")
    return found


def main():
    log(f"swarm_poller started, polling {OUTBOX} every {POLL_INTERVAL}s")
    while True:
        try:
            process_outbox()
        except Exception as e:
            log(f"main loop error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("stopped")
