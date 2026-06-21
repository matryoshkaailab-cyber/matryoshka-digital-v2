#!/usr/bin/env python3
"""
validate_task_kind.py — P1 kind enum validator.

Backward-compat:
- kind отсутствует → legacy → log warning, НЕ reject
- kind='' → legacy → log warning, НЕ reject
- kind в ALLOWED → OK
- kind вне ALLOWED → reject (return 1, error message)

Использование:
    python3 validate_task_kind.py <task.json>
"""
import sys
import json

ALLOWED_KINDS = {
    'alf',                  # ALF (стратег, основной)
    'alina-prod',           # ALINA (клиентский кейс Николая)
    'alf-strategist',      # ALF профиль "стратег"
    'alf-librarian',        # ALF профиль "библиотекарь"
    'hermes-cli',           # HERMES (дирижёр)
    'alex',                 # ALEX (тех. инженер на ПК)
    # BACKWARD-COMPAT: пустая строка = legacy
    '',
}

def validate(task: dict) -> tuple[bool, str]:
    kind = task.get('kind', '')  # default '' = legacy
    if kind == '':
        return True, 'LEGACY: kind отсутствует/пустой, обработано как legacy (warning logged)'

    if kind in ALLOWED_KINDS:
        return True, f'OK: kind={kind}'

    return False, f'REJECT: kind="{kind}" не в ALLOWED ({sorted(ALLOWED_KINDS - {""})})'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: validate_task_kind.py <task.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        task = json.load(f)

    ok, msg = validate(task)
    print(msg)
    sys.exit(0 if ok else 1)
