#!/usr/bin/env python3
"""
anonymize.py — обезличивание персональных данных (152-ФЗ).

Использование:
    python3 anonymize.py /root/matryoshka/notebooklm_sources/

Заменяет:
    Николай → CLIENT_001 (TG: 146881168)
    Наталья → CLIENT_002 (TG: 461605744)
    Олег → OLEG_ID (TG: 1951845052)
    Краснодар → CITY_KRD
    + телефоны, явные ID

Создан 16.06.2026 для MATRYOSHKA NotebookLM integration.
"""
import re
import os
import sys

# Маппинг персональных данных → псевдо-ID
REPLACEMENTS = [
    # Клиенты (приоритет — длинные паттерны первыми)
    (re.compile(r'Николай\s*(?:Варнаков)?', re.IGNORECASE), 'CLIENT_001'),
    (re.compile(r'@?NikolaiAlinaBot\s*\((?:id\s*)?(\d+)?\)'), r'@NikolaAlinaBot (TG:146881168)'),
    (re.compile(r'\(TG:?\s*146881168,?\s*~\s*400к₽,\s*Краснодар\)'), '(TG:146881168, ~400k₽, CITY_KRD)'),

    (re.compile(r'Наталья\s*(?:\(Telegram\s*id:?\s*\d+\))?', re.IGNORECASE), 'CLIENT_002'),
    (re.compile(r'@?ZarnyAlexaBot\s*\(id:?\s*\d+\)'), r'@ZarnyAlexaBot (TG:461605744)'),

    (re.compile(r'Олег\s*Чут', re.IGNORECASE), 'OLEG_ID'),
    (re.compile(r'Олег', re.IGNORECASE), 'OLEG_ID'),
    (re.compile(r'@?oleglab22', re.IGNORECASE), '@oleglab22'),
    (re.compile(r'TG:?\s*1951845052'), 'TG:1951845052'),

    # География
    (re.compile(r'Краснодар(?:а|е|у|ом)?', re.IGNORECASE), 'CITY_KRD'),
    (re.compile(r'Краснодарский\s*край', re.IGNORECASE), 'REGION_KRD'),

    # Телефоны (формат +7...)
    (re.compile(r'\+7\s*\(?9\d{2}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}'), '+7 (9XX) XXX-XX-XX'),
    (re.compile(r'8\s*\(?9\d{2}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}'), '+7 (9XX) XXX-XX-XX'),

    # Email (если есть)
    (re.compile(r'[\w\.-]+@[\w\.-]+\.\w+'), 'email@anonymized.local'),

    # Telegram-стикеры (имена в скобках)
    (re.compile(r'([А-ЯЁ][а-яё]+)\s*\((Telegram\s*id:?\s*\d+)\)', re.IGNORECASE), r'\1 (TG:ANONYMIZED)'),
]


def anonymize_text(text: str) -> tuple[str, int]:
    """Возвращает (anonymized_text, num_replacements)."""
    count = 0
    for pattern, replacement in REPLACEMENTS:
        new_text, n = pattern.subn(replacement, text)
        if n > 0:
            count += n
            text = new_text
    return text, count


def anonymize_file(path: str) -> tuple[bool, int]:
    """Anonymize один файл. Возвращает (changed, replacements)."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            original = f.read()
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        return False, 0

    anonymized, count = anonymize_text(original)
    if count > 0 and anonymized != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(anonymized)
        return True, count
    return False, 0


def process_dir(directory: str, dry_run: bool = False) -> tuple[int, int]:
    """Anonymize все .md/.txt/.json/.yaml в директории."""
    files_changed = 0
    total_replacements = 0
    skipped = []

    for root, dirs, files in os.walk(directory):
        # Пропустить .archive
        dirs[:] = [d for d in dirs if d not in ('.archive', '.git', 'node_modules')]
        for fname in files:
            if not fname.endswith(('.md', '.txt', '.json', '.yaml', '.yml')):
                continue
            fpath = os.path.join(root, fname)
            if dry_run:
                # Только показать, не менять
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        original = f.read()
                    _, count = anonymize_text(original)
                    if count > 0:
                        files_changed += 1
                        total_replacements += count
                        print(f"  [DRY] {fpath}: {count} replacements")
                except Exception as e:
                    skipped.append((fpath, str(e)))
            else:
                changed, count = anonymize_file(fpath)
                if changed:
                    files_changed += 1
                    total_replacements += count
                    print(f"  ✅ {fpath}: {count} replacements")

    return files_changed, total_replacements


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '/root/matryoshka/notebooklm_sources/'
    dry_run = '--dry-run' in sys.argv

    if not os.path.isdir(target):
        print(f"❌ Не директория: {target}")
        sys.exit(1)

    print(f"=== Anonymizer v2.0 (16.06.2026) ===")
    print(f"Target: {target}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'WRITE'}")
    print()

    files_changed, total_repl = process_dir(target, dry_run=dry_run)

    print()
    print(f"📊 Files changed: {files_changed}")
    print(f"📊 Total replacements: {total_repl}")
    if dry_run:
        print()
        print("🔄 Запусти без --dry-run чтобы применить.")
    else:
        print()
        print("✅ Готово. Проверь результат перед загрузкой в NotebookLM.")
