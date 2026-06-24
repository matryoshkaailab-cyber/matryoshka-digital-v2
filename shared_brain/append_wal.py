#!/usr/bin/env python3
"""
SHARED BRAIN — WAL append + digest generator.
Phase 1 fix: каждый агент при завершении сессии пишет в свой WAL.
Digest генерируется из всех WAL каждые 5 мин.
HERMES читает Digest в RECALL PROTOCOL шаг 0.

Использование:
  append_wal.py <agent> <message>   # append to WAL
  append_wal.py --digest             # regenerate DIGEST.md from all WALs

Примеры:
  append_wal.py alf "запустил P0 чистку, освобождено 1.2G"
  append_wal.py hermes "Олег одобрил shared brain v2"
  append_wal.py alex "обновил Python 3.12"
"""
import os
import sys
import fcntl
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/matryoshka/shared_brain")
WAL_DIR = BASE / "WAL"
DIGEST = BASE / "DIGEST.md"
LOCK = BASE / "shared_brain.lock"
SCHEMA_VERSION = 1

VALID_AGENTS = ("hermes", "alf", "alex", "alina", "hermes-cli")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class _FileLock:
    """Context-manager wrapper around flock."""
    def __init__(self, timeout: int = 5) -> None:
        self.timeout = timeout
        self._f = None

    def __enter__(self):
        LOCK.parent.mkdir(parents=True, exist_ok=True)
        LOCK.touch(exist_ok=True)
        self._f = open(LOCK, "w+")
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            try:
                fcntl.flock(self._f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self._f
            except (IOError, OSError):
                time.sleep(0.05)
        raise TimeoutError(f"Could not acquire {LOCK} within {self.timeout}s")

    def __exit__(self, *exc) -> None:
        if self._f is not None:
            try:
                fcntl.flock(self._f, fcntl.LOCK_UN)
            except Exception:
                pass
            self._f.close()


def acquire_lock(timeout: int = 5) -> _FileLock:
    """Return a context-manager lock object."""
    return _FileLock(timeout=timeout)


def append_wal(agent: str, message: str) -> None:
    """Append timestamped entry to agent's WAL."""
    if agent not in VALID_AGENTS:
        # Auto-allow any agent name (so we don't break forward compat)
        pass
    WAL_DIR.mkdir(parents=True, exist_ok=True)
    wal_file = WAL_DIR / f"{agent}.wal"
    entry = {
        "ts": now_iso(),
        "agent": agent,
        "msg": message,
        "schema": SCHEMA_VERSION,
    }
    import json
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    with acquire_lock():
        with wal_file.open("a", encoding="utf-8") as f:
            f.write(line)
    print(f"✓ WAL[{agent}] appended: {message[:80]}")

    # Self-improvement loop (19.06.2026): also append to Obsidian AGENT_EVENTS.md
    try:
        import subprocess as _sl_sp
        from datetime import datetime, timezone
        from pathlib import Path as _sl_Path
        _sl_obsidian = _sl_Path("/root/obsidian-vault")
        _sl_day = _sl_obsidian / "daily" / datetime.now(timezone.utc).strftime("%Y-%m-%d")
        _sl_day.mkdir(parents=True, exist_ok=True)
        _sl_events = _sl_day / "AGENT_EVENTS.md"
        _sl_icon = "▶"
        for _sl_w, _sl_i in [("decision", "◆"), ("error", "✗"), ("question", "?"), ("learning", "💡"), ("fixed", "✓"), ("created", "★")]:
            if _sl_w in message.lower():
                _sl_icon = _sl_i
                break
        _sl_ts = entry["ts"]
        _sl_line = f"- `{_sl_ts}` **{_sl_icon} {agent.upper()}** {message}\n"
        with _sl_events.open("a", encoding="utf-8") as _sl_f:
            _sl_f.write(_sl_line)
    except Exception as _sl_e:
        print(f"  WARN: Obsidian sync failed: {_sl_e}", file=__import__("sys").stderr)


def generate_digest(max_per_agent: int = 10) -> None:
    """Aggregate last N entries from all WALs into DIGEST.md."""
    import json
    entries = []
    if not WAL_DIR.exists():
        WAL_DIR.mkdir(parents=True, exist_ok=True)
    for wal_file in sorted(WAL_DIR.glob("*.wal")):
        agent = wal_file.stem
        try:
            with wal_file.open("r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"WARN: cannot read {wal_file}: {e}")
            continue
        for line in lines[-max_per_agent:]:
            try:
                e = json.loads(line.strip())
                e["_source"] = agent
                entries.append(e)
            except Exception:
                pass
    entries.sort(key=lambda e: e.get("ts", ""), reverse=True)

    ts = now_iso()
    out = [f"# SHARED BRAIN DIGEST — {ts}\n"]
    out.append(f"**Total entries (last {max_per_agent} per agent):** {len(entries)}\n")

    # P0/P1/P2 decisions
    p0 = [e for e in entries if any(k in e.get("msg", "").lower()
           for k in ["p0", "critical", "approved", "rejected"])]
    if p0:
        out.append("\n## P0 Decisions\n")
        for e in p0[:8]:
            out.append(f"- [{e['ts']}] **{e['agent']}**: {e['msg']}\n")

    # All recent entries grouped by agent
    out.append("\n## Recent (all agents, newest first)\n")
    for e in entries[:30]:
        out.append(f"- [{e['ts']}] **{e['agent']}**: {e['msg']}\n")

    # Open questions (heuristic)
    qs = [e for e in entries if "?" in e.get("msg", "")]
    if qs:
        out.append(f"\n## Open Questions ({len(qs)})\n")
        for e in qs[:5]:
            out.append(f"- {e['agent']}: {e['msg']}\n")

    out.append("\n---\n*Auto-generated by shared_brain/append_wal.py --digest*\n")

    with acquire_lock():
        DIGEST.write_text("".join(out), encoding="utf-8")
    print(f"✓ DIGEST regenerated: {len(entries)} entries → {DIGEST}")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    if sys.argv[1] == "--digest":
        generate_digest()
        return 0
    # Support legacy --agent <name> <message> invocation
    if sys.argv[1] == "--agent":
        if len(sys.argv) < 4:
            print("Usage: append_wal.py --agent <agent_name> <message>")
            return 1
        agent = sys.argv[2]
        msg = " ".join(sys.argv[3:])
        append_wal(agent, msg)
        return 0
    if len(sys.argv) < 3:
        print("Usage: append_wal.py <agent> <message>")
        return 1
    agent = sys.argv[1]
    msg = " ".join(sys.argv[2:])
    append_wal(agent, msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
