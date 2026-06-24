#!/usr/bin/env python3
"""
Memory -> Obsidian Bridge
Экспортирует состояние памяти агентов (kanban.db, MEMORY.md, USER.md, SOUL.md)
в Obsidian vault (/root/obsidian-vault/) для двусторонней синхронизации.

Vault доступен через WebDAV :8181, Remotely Save на ПК подхватывает автоматически.
"""
import os
import sqlite3
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path("/root/.hermes")
VAULT = Path("/root/obsidian-vault")
KANBAN_DB = HERMES_HOME / "kanban.db"

DAILY = VAULT / "daily"
AGENTS = VAULT / "agents"

DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")
TS = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def ensure_dirs():
    for d in (DAILY, AGENTS):
        d.mkdir(parents=True, exist_ok=True)


def export_static_files():
    """Копируем MEMORY.md / USER.md / SOUL.md в agents/ (один-к-одному, с датой обновления)"""
    pairs = [
        (HERMES_HOME / "MEMORY.md", AGENTS / "HERMES_MEMORY.md"),
        (HERMES_HOME / "USER.md", AGENTS / "USER_PROFILE.md"),
        (HERMES_HOME / "SOUL.md", AGENTS / "HERMES_SOUL.md"),
    ]
    exported = []
    for src, dst in pairs:
        if not src.exists():
            continue
        try:
            content = src.read_text(encoding="utf-8")
            banner = (
                f"\n\n---\n"
                f"_Memory bridge export. Source: `{src}`_\n"
                f"_Exported: {TS}_\n"
            )
            dst.write_text(content + banner, encoding="utf-8")
            exported.append(str(dst.relative_to(VAULT)))
        except Exception as e:
            print(f"FAIL {src.name}: {e}")
    return exported


def export_kanban():
    """Снапшот kanban в daily/kanban_YYYY-MM-DD.md"""
    if not KANBAN_DB.exists():
        return None
    try:
        con = sqlite3.connect(str(KANBAN_DB))
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            "SELECT id, title, status, priority, assignee, created_at, "
            "last_heartbeat_at, completed_at FROM tasks ORDER BY "
            "CASE status WHEN 'processing' THEN 0 WHEN 'pending' THEN 1 "
            "WHEN 'failed' THEN 2 WHEN 'done' THEN 3 ELSE 4 END, "
            "COALESCE(last_heartbeat_at, completed_at, started_at, created_at) DESC"
        )
        rows = cur.fetchall()
        cur.execute("SELECT COUNT(*) AS c FROM tasks")
        total = cur.fetchone()["c"]
        cur.execute(
            "SELECT status, COUNT(*) AS c FROM tasks GROUP BY status ORDER BY c DESC"
        )
        stats = cur.fetchall()
        con.close()

        out = DAILY / f"kanban_{DATE}.md"
        lines = [
            f"# Kanban Snapshot — {DATE}",
            f"",
            f"_Exported: {TS}_",
            f"_Source: `{KANBAN_DB}`_",
            f"",
            f"## Stats: {total} tasks",
            f"",
            f"| Status | Count |",
            f"|--------|------:|",
        ]
        for r in stats:
            lines.append(f"| {r['status']} | {r['c']} |")
        lines += ["", "## Tasks", ""]
        for r in rows:
            prio = r["priority"] if r["priority"] is not None else 0
            title = (r["title"] or "")[:120]
            ts = r["last_heartbeat_at"] or r["completed_at"] or r["created_at"] or 0
            ts_str = (
                datetime.fromtimestamp(ts, timezone.utc).strftime("%m-%d %H:%M")
                if ts
                else "—"
            )
            lines.append(
                f"- **{r['status']}** | prio={prio} | {r['assignee'] or '-'} | "
                f"`{r['id']}` | {ts_str} | {title}"
            )
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(out.relative_to(VAULT))
    except Exception as e:
        print(f"FAIL kanban: {e}")
        return None


def main():
    ensure_dirs()
    print(f"=== Memory -> Obsidian bridge @ {TS} ===")
    files = export_static_files()
    kanban = export_kanban()
    print(f"Exported static: {files}")
    print(f"Exported kanban: {kanban}")


if __name__ == "__main__":
    main()
