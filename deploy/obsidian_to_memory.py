#!/usr/bin/env python3
"""
Obsidian -> Memory Bridge
Читает Obsidian vault (/root/obsidian-vault/) и записывает заметки
в память агента (/root/.hermes/memories/) как текстовые фрагменты.

Направление: human notes (Obsidian) -> agent memory.
"""
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path("/root/obsidian-vault")
MEMORY_DIR = Path("/root/.hermes/memories")
TS = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# Сканируемые папки vault (где лежат человеческие заметки)
SCAN_DIRS = ["clients", "leads", "projects", "daily", "analytics"]

# Шаблон имени файла в memories: <source>__<rel_path>.md
PREFIX = "obsidian"


def ensure_memory_dir():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def fingerprint(content: str) -> str:
    return hashlib.sha1(content.encode("utf-8")).hexdigest()[:12]


def import_vault():
    """Читает .md файлы из SCAN_DIRS, пишет в memories/ с обёрткой source+fingerprint.
    Не дублирует: если содержимое не изменилось (fingerprint совпал) — не перезаписывает.
    """
    ensure_memory_dir()
    imported = 0
    skipped = 0
    failed = 0
    for sub in SCAN_DIRS:
        src_dir = VAULT / sub
        if not src_dir.exists():
            continue
        for md in src_dir.rglob("*.md"):
            try:
                rel = md.relative_to(src_dir).as_posix()
                if rel.endswith(".md"):
                    rel = rel[:-3]
                if rel.startswith("README") or "kanban_" in rel:
                    # README и уже-экспортированные kanban — не импортируем обратно
                    skipped += 1
                    continue
                content = md.read_text(encoding="utf-8")
                fp = fingerprint(content)
                out_name = f"{PREFIX}__{sub}__{rel.replace('/', '_')}.md"
                out = MEMORY_DIR / out_name
                if out.exists():
                    existing = out.read_text(encoding="utf-8")
                    if f"fingerprint: {fp}" in existing:
                        skipped += 1
                        continue
                wrapped = (
                    f"# Obsidian import: {sub}/{rel}\n"
                    f"source: {md}\n"
                    f"imported: {TS}\n"
                    f"fingerprint: {fp}\n"
                    f"\n---\n\n"
                    f"{content}"
                )
                out.write_text(wrapped, encoding="utf-8")
                imported += 1
            except Exception as e:
                print(f"FAIL {md}: {e}")
                failed += 1
    return imported, skipped, failed


def main():
    print(f"=== Obsidian -> Memory bridge @ {TS} ===")
    imp, skp, fld = import_vault()
    print(f"imported: {imp} | skipped (unchanged/empty): {skp} | failed: {fld}")


if __name__ == "__main__":
    main()
