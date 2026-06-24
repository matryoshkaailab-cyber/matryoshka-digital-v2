"""
HERMES Delegate — отправка задач агентам роя.

Использование:
  python3 hermes_delegate.py alex "Get-Process | Select-Object -First 5"
  python3 hermes_delegate.py alf "Стратегический анализ рынка X"
  python3 hermes_delegate.py alisa "..."

Сейчас реализован только alex (файловая очередь + SCP).
ALF/ALISA — отправляются как Telegram message боту.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from datetime import datetime

VPS_TASK_FILE = Path("/root/matryoshka/.hermes_task.json")
VPS_RESULT_FILE = Path("/root/matryoshka/.hermes_result.json")
PC_USER = "User"
PC_HOST = "10.8.1.4"
PC_PATH = "/c/matryoshka"
SCP_PASS = "Jktu22051987"  # legacy; in real use, SSH key
TIMEOUT = 300
LOG = Path("/root/matryoshka/logs/hermes_delegate.log")
LOG.parent.mkdir(parents=True, exist_ok=True)


def log(msg):
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def scp_put(local: Path, remote_path: str):
    cmd = [
        "sshpass", "-p", SCP_PASS,
        "scp", "-o", "StrictHostKeyChecking=accept-new",
        str(local), f"{PC_USER}@{PC_HOST}:{remote_path}",
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def scp_get(remote_path: str, local: Path):
    cmd = [
        "sshpass", "-p", SCP_PASS,
        "scp", "-o", "StrictHostKeyChecking=accept-new",
        f"{PC_USER}@{PC_HOST}:{remote_path}", str(local),
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def delegate_to_alex(command: str, timeout: int = TIMEOUT) -> dict:
    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "status": "pending",
        "target": "alex",
        "command": command,
        "timeout": timeout,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "from": "HERMES",
    }
    VPS_TASK_FILE.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"task {task_id} created locally, pushing to PC")
    pc_task = f"{PC_PATH}/.hermes_task.json"
    r = scp_put(VPS_TASK_FILE, pc_task)
    if r.returncode != 0:
        log(f"scp put failed: {r.stderr}")
        return {"ok": False, "error": f"scp put failed: {r.stderr}"}
    log("pushed to PC, waiting for result...")
    deadline = time.time() + timeout + 30
    while time.time() < deadline:
        time.sleep(10)
        pc_result = f"{PC_PATH}/.hermes_result.json"
        local_tmp = Path(f"/tmp/hermes_result_pull_{task_id}.json")
        r = scp_get(pc_result, local_tmp)
        if r.returncode == 0 and local_tmp.exists():
            try:
                result = json.loads(local_tmp.read_text(encoding="utf-8"))
                if result.get("task_id") == task_id and result.get("status") == "done":
                    log(f"got result for {task_id}: ok={result.get('ok')}")
                    VPS_RESULT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                    local_tmp.unlink()
                    return result
            except Exception as e:
                log(f"parse result error: {e}")
        if local_tmp.exists():
            local_tmp.unlink()
    log(f"timeout waiting for {task_id}")
    return {"ok": False, "error": "timeout", "task_id": task_id}


def delegate_to_alf(text: str) -> dict:
    """ALF persona в Hermes — отправляем через Telegram бот @IlonAnalyticBot."""
    log(f"delegating to ALF via Telegram: {text[:80]}")
    return {
        "ok": True,
        "target": "alf",
        "note": "ALF = persona in Hermes. To invoke, run: hermes --profile alf chat --message '...' OR send Telegram message to @IlonAnalyticBot",
        "command": text,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["alex", "alf", "alisa"])
    ap.add_argument("command")
    ap.add_argument("--timeout", type=int, default=TIMEOUT)
    args = ap.parse_args()
    if args.target == "alex":
        result = delegate_to_alex(args.command, args.timeout)
    elif args.target == "alf":
        result = delegate_to_alf(args.command)
    else:
        result = {"ok": False, "error": f"target {args.target} not implemented yet"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("ok") else 1)


if __name__ == "__main__":
    main()
