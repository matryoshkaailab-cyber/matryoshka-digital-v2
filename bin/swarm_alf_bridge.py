#!/usr/bin/env python3
"""
swarm_alf_bridge.py v2 — НОТИФИКАТОР outbox/alf/ (ФИКС 21.06.2026 race fix).

v1: bridge читал inbox/alf/*.json И outbox/alf/*.json, гонялся с FileWatcher.
v2: bridge читает ТОЛЬКО outbox/alf/*.json, шлёт ALERT Олегу.
    FileWatcher (alf_filewatcher.py) берёт на себя inbox/alf/*.json → ALF → outbox.

Разделение зон:
- FileWatcher: inbox → ALF → outbox (producer)
- Bridge:      outbox → ALERT Олегу (consumer/notifier)

Без race, без дублей.
"""
import json
import time
import requests
from pathlib import Path
from datetime import datetime

SWARM_OUTBOX = Path("/root/matryoshka/swarm/outbox/alf")
SWARM_SENT_OUTBOX = Path("/root/matryoshka/swarm/outbox/alf/.notified")
ALF_BOT_TOKEN = "8941776316:AAE...полныйтокен..."
OLEG_CHAT_ID = "1951845052"
POLL_INTERVAL = 5
LOG = Path("/var/log/swarm/alf_bridge.log")


def log(msg):
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def notify_oleg(text: str) -> bool:
    url = f"https://api.telegram.org/bot{ALF_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": OLEG_CHAT_ID, "text": text}, timeout=15)
        return r.status_code == 200
    except Exception as e:
        log(f"sendMessage EXC: {e}")
        return False


def process_outbox() -> int:
    """Read outbox/alf/*.json, notify Oleg, mark as notified."""
    if not SWARM_OUTBOX.exists():
        return 0
    SWARM_SENT_OUTBOX.mkdir(parents=True, exist_ok=True)
    sent = 0
    for resp_file in SWARM_OUTBOX.glob("*.json"):
        try:
            resp = json.loads(resp_file.read_text(encoding="utf-8"))
        except Exception as e:
            log(f"PARSE FAIL {resp_file.name}: {e}")
            continue
        
        task_id = resp.get("task_id", resp_file.stem)
        ok = resp.get("ok", False)
        status = resp.get("status", "?")
        output_preview = resp.get("output", "")[:300]
        
        icon = "✅" if ok else "❌"
        msg = (
            f"{icon} [ALF-OUTBOX] {status.upper()}\n"
            f"Task: {task_id}\n"
            f"Output (300 chars):\n{output_preview}"
        )
        notify_oleg(msg)
        log(f"NOTIFY to Oleg: task_id={task_id}, ok={ok}")
        
        # Mark as notified (rename)
        notified = SWARM_SENT_OUTBOX / f"{resp_file.name}.notified.{int(time.time())}"
        try:
            resp_file.rename(notified)
        except Exception as e:
            log(f"RENAME FAIL {resp_file.name}: {e}")
        sent += 1
    return sent


def main():
    log("=== ALF bridge NOTIFIER v2 started (outbox only) ===")
    while True:
        try:
            n = process_outbox()
            if n > 0:
                log(f"processed {n} outbox message(s)")
        except Exception as e:
            log(f"loop error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
