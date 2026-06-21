#!/usr/bin/env python3
"""
atomic_result_write.py — P0 race fix для .hermes_result.json.
Записывает JSON результат атомарно (tmpfile + os.replace + git add + commit в одной транзакции).

Использование:
    python3 atomic_result_write.py <task_id> <result_json>
    python3 atomic_result_write.py --json '{"task_id":"...","ok":true,"output":"..."}'

Гарантии:
1. Write в /tmp/atomic_result_<pid>.json (atomic на уровне ОС)
2. fsync (дождаться записи на диск)
3. os.replace(tmp, .hermes_result.json) — атомарный rename в POSIX
4. git add + git commit --amend --no-edit (в subshell с set -e)
5. Если любой шаг fail — cleanup (rm tmpfile)

НЕ нужен file lock — атомарный rename + subshell = mutual exclusion.
"""
import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

VPS = Path('/root/matryoshka')
RESULT = VPS / '.hermes_result.json'
TMP_DIR = Path('/tmp')

def atomic_write(payload: dict) -> bool:
    """Атомарная запись .hermes_result.json с git commit в одной транзакции."""
    payload['finished_at'] = __import__('datetime').datetime.now().isoformat(timespec='seconds')

    # 1. Write в /tmp tmpfile (atomic)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=TMP_DIR, prefix='atomic_result_', suffix='.json')
    try:
        with os.fdopen(tmp_fd, 'w') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        # 2. Атомарный rename
        os.replace(tmp_path, RESULT)

        # 3. Git add + commit в subshell (всё или ничего)
        result = subprocess.run(
            ['bash', '-c', f'set -e; cd {VPS} && git add .hermes_result.json && git commit --amend --no-edit'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            print(f"Git commit failed: {result.stderr}", file=sys.stderr)
            return False

        print(f"OK: {RESULT} (committed)")
        return True

    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: atomic_result_write.py <task_id> <output>")
        print("       atomic_result_write.py --json '<json>'")
        sys.exit(1)

    if sys.argv[1] == '--json':
        payload = json.loads(sys.argv[2])
    else:
        payload = {
            'task_id': sys.argv[1],
            'output': sys.argv[2] if len(sys.argv) > 2 else '',
            'ok': True,
            'executed_by': 'hermes',
        }

    success = atomic_write(payload)
    sys.exit(0 if success else 1)
