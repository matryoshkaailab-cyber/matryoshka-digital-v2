#!/usr/bin/env python3
"""swarm_send_alex.py — sync отправка задачи ALEX через ACP (прямой канал VPS→ALEX).

В отличие от swarm_send.py (который кладёт в swarm/inbox/alex/ для SCP-polling),
этот скрипт вызывает acp_send.sh синхронно и возвращает результат в JSON.

Использование:
    python3 swarm_send_alex.py "команда для ALEX" [--timeout 60]
    python3 swarm_send_alex.py "команда" --context "от Олега" --timeout 120

Возвращает:
    {"ok": true, "task_id": "...", "output": "...", "elapsed_sec": 5.2}
"""
import argparse
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

ACP_SEND_SH = Path("/root/matryoshka/bin/acp_send.sh")
DEFAULT_TIMEOUT = 60


def send_alex(command: str, context: str = "", timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Sync отправка команды ALEX через ACP."""
    if not ACP_SEND_SH.exists():
        return {"ok": False, "error": f"acp_send.sh not found at {ACP_SEND_SH}"}

    task_id = f"acp_{uuid.uuid4().hex[:8]}"
    start = time.time()
    # ALEX enforcement (19.06.2026): Obsidian must be fresh before ACP call
    import subprocess as _enforce_sp
    _enforce_r = _enforce_sp.run(["python3", "/usr/local/bin/hermes_obsidian_enforce.py"], capture_output=True, text=True, timeout=30)
    if _enforce_r.returncode == 2:
        return {"ok": False, "error": "Obsidian stale or invalid", "enforce_output": _enforce_r.stdout, "task_id": task_id}



    prompt = f"{command}\n\nContext: {context}" if context else command

    try:
        result = subprocess.run(
            [str(ACP_SEND_SH), prompt, str(timeout)],
            capture_output=True,
            text=True,
            timeout=timeout + 30,
        )
        elapsed = time.time() - start

        if result.returncode == 0:
            return {
                "ok": True,
                "task_id": task_id,
                "output": result.stdout,
                "elapsed_sec": round(elapsed, 2),
            }
        else:
            return {
                "ok": False,
                "task_id": task_id,
                "error": result.stderr or result.stdout,
                "returncode": result.returncode,
                "elapsed_sec": round(elapsed, 2),
            }
    except subprocess.TimeoutExpired:
        return {"ok": False, "task_id": task_id, "error": f"timeout after {timeout}s"}
    except Exception as e:
        return {"ok": False, "task_id": task_id, "error": str(e)}


def main():
    ap = argparse.ArgumentParser(description="Send task to ALEX via ACP")
    ap.add_argument("command")
    ap.add_argument("--context", default="")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = ap.parse_args()
    result = send_alex(args.command, args.context, args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
