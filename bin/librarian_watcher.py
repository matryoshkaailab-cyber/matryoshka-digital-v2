#!/usr/bin/env python3
"""
librarian_watcher.py — cron watcher для alf-librarian (file-queue).
Читает .hermes_task_librarian.json, выполняет через Hermes Agent, пишет ответ в outbox.
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path

VPS = Path('/root/matryoshka')
TASK_FILE = VPS / '.hermes_task_librarian.json'
OUTBOX = VPS / 'swarm/outbox/librarian'
HERMES_BIN = '/opt/alf-hermes/venv/bin/hermes'

def process_task(task: dict) -> dict:
    """Обработать задачу через Hermes Agent."""
    query = task.get('query', task.get('question', ''))
    if not query:
        return {'ok': False, 'error': 'no query'}

    # Используем hermes run с prompt (НЕ polling)
    result = subprocess.run(
        [HERMES_BIN, 'agent', '--profile', 'alf-librarian', '--prompt', query, '--non-interactive'],
        capture_output=True, text=True, timeout=120
    )
    return {
        'ok': result.returncode == 0,
        'output': result.stdout[:5000],
        'error': result.stderr[:1000] if result.returncode != 0 else '',
    }

def main():
    if not TASK_FILE.exists():
        return
    try:
        task = json.loads(TASK_FILE.read_text())
        if task.get('status') != 'pending':
            return
        TASK_FILE.write_text(json.dumps({**task, 'status': 'processing'}))
        result = process_task(task)
        result['task_id'] = task.get('task_id', 'unknown')
        result['finished_at'] = time.strftime('%Y-%m-%dT%H:%M:%S')
        OUTBOX.mkdir(parents=True, exist_ok=True)
        out_file = OUTBOX / f"{result['task_id']}.json"
        out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        TASK_FILE.write_text(json.dumps({**task, 'status': 'done', 'result_file': str(out_file)}))
    except Exception as e:
        sys.stderr.write(f'librarian_watcher error: {e}\n')

if __name__ == '__main__':
    main()
