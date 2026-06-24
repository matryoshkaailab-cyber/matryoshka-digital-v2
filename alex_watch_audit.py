#!/usr/bin/env python3
import os, time, subprocess
from pathlib import Path

TASK_FILE = Path("/root/matryoshka/alex_tasks/2026-06-08_1205_audit_fixes.md")
HERMES_TOK = os.environ.get("HERMES_TOK", "")
OLEG_ID = "1951845052"
MAX_WAIT = 900
start = time.time()
print(f"[{time.strftime('%H:%M:%S')}] Watchdog started")

while True:
    elapsed = int(time.time() - start)
    if TASK_FILE.exists() and TASK_FILE.stat().st_size > 100:
        size = TASK_FILE.stat().st_size
        print(f"Alex answered size={size} elapsed={elapsed}s")
        text = f"ALEX ANSWERED ({elapsed}s)\n\nFile: {TASK_FILE}\nSize: {size} bytes"
        subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{HERMES_TOK}/sendMessage",
            "-d", f"chat_id={OLEG_ID}",
            "--data-urlencode", f"text={text}"
        ], check=False, capture_output=True)
        subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{HERMES_TOK}/sendDocument",
            "-F", f"chat_id={OLEG_ID}",
            "-F", f"document=@{TASK_FILE}"
        ], check=False, capture_output=True)
        print(TASK_FILE.read_text()[:3000])
        break
    if elapsed > MAX_WAIT:
        text = f"TIMEOUT 15min. Alex did not answer. File {TASK_FILE} missing."
        subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{HERMES_TOK}/sendMessage",
            "-d", f"chat_id={OLEG_ID}",
            "--data-urlencode", f"text={text}"
        ], check=False, capture_output=True)
        break
    time.sleep(30)
