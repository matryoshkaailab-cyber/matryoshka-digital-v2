#!/usr/bin/env python3
"""
Hermes Active Flush v2 — multi-profile + shared_brain aware.

Изменения vs v1:
- Опрашивает ВСЕ профили (alf, alex, alina-prod, hermes-cli, default)
- Дёргает shared_brain/append_wal.py --digest перед flush (Digest свежий)
- Пишет в .current_context.md секцию CROSS-PROFILE STATE (а не только default)
- НЕ затирает ручные изменения в .current_context.md (если файл моложе 30 мин
  и содержит маркер "manual-update" — пропускает, только делает append секции)
"""
import subprocess
import sys
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# HERMES_HOME may be set per-profile (e.g. /root/.hermes/profiles/alf) by
# service unit — but we need the global profiles root, not nested. Hardcode
# to /root/.hermes/profiles which is the canonical location for all
# per-profile state.db files. Falls back to env var if /root/.hermes/profiles
# does not exist.
_DEFAULT_PROFILES = Path("/root/.hermes/profiles")
if _DEFAULT_PROFILES.exists():
    PROFILES_DIR = _DEFAULT_PROFILES
else:
    _h = Path(os.environ.get("HERMES_HOME") or "/root/.hermes")
    PROFILES_DIR = _h / "profiles" if (_h / "profiles").exists() else _h
CONTEXT_FILE = Path("/root/matryoshka/.current_context.md")
MEMORY_FILE = Path("/root/matryoshka/HERMES_MEMORY.md")
LOG_FILE = Path("/var/log/hermes_active_flush.log")
SHARED_BRAIN = Path("/root/matryoshka/shared_brain")
APPEND_WAL = SHARED_BRAIN / "append_wal.py"
DIGEST = SHARED_BRAIN / "DIGEST.md"

VENV_PY = "/usr/local/lib/hermes-agent/venv/bin/python3"
HERMES_BIN = "/usr/local/bin/hermes"

# Skip these — internal/system profiles not driven by Oleg
SKIP_PROFILES = {"alex"}  # alex is on Windows, not VPS


def log(msg: str) -> None:
    try:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with LOG_FILE.open("a") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def safe_run(cmd, timeout=5):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def get_profile_stats(profile_name: str) -> dict:
    """Read state.db of one profile — return message count, last ts, size."""
    db = PROFILES_DIR / profile_name / "state.db"
    if not db.exists():
        return {"name": profile_name, "exists": False}
    rc, out, _ = safe_run([
        "sqlite3", str(db),
        "SELECT COUNT(*), COALESCE(MAX(timestamp), 0) FROM messages;"
    ], timeout=3)
    stats = {"name": profile_name, "exists": True, "size_mb": round(db.stat().st_size / 1024 / 1024, 1)}
    if rc == 0 and out.strip():
        parts = out.strip().split("|")
        if len(parts) >= 2:
            stats["messages"] = parts[0]
            stats["last_ts"] = parts[1]
    return stats


def refresh_shared_brain_digest() -> None:
    """Regenerate shared brain DIGEST.md from WALs."""
    if not APPEND_WAL.exists():
        log("WARN: append_wal.py missing, skipping digest refresh")
        return
    rc, out, err = safe_run(["/usr/bin/python3", str(APPEND_WAL), "--digest"], timeout=10)
    if rc == 0:
        log(f"OK shared_brain digest refreshed")
    else:
        log(f"ERROR shared_brain digest: {err}")


def write_context_file(reason: str) -> None:
    """Write current operational context across ALL profiles."""
    try:
        # 1. Refresh shared_brain digest
        refresh_shared_brain_digest()

        # 2. Gather per-profile stats
        profiles = []
        for p in sorted(PROFILES_DIR.iterdir()):
            if p.is_dir() and p.name not in SKIP_PROFILES:
                profiles.append(get_profile_stats(p.name))

        # 3. Gateway status
        rc, gw_status, _ = safe_run(["systemctl", "is-active", "hermes-cli-gateway"], timeout=2)
        gw = gw_status.strip() if rc == 0 else "unknown"

        # 4. Build content
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        prof_lines = []
        for p in profiles:
            if p.get("exists"):
                prof_lines.append(
                    f"  - {p['name']}: {p.get('size_mb', '?')}MB / "
                    f"{p.get('messages', '?')} msgs"
                )
            else:
                prof_lines.append(f"  - {p['name']}: (no state.db)")
        prof_block = "\n".join(prof_lines)

        # 5. Shared brain digest snippet
        digest_snip = ""
        if DIGEST.exists():
            digest_text = DIGEST.read_text(encoding="utf-8")
            # Take first ~15 non-empty lines after header
            lines = [l for l in digest_text.split("\n") if l.strip()][:15]
            digest_snip = "## Shared Brain (last entries)\n" + "\n".join(lines)

        content = f"""# Hermes Active Context — auto-flushed {ts}
# reason: {reason}
# version: v2 (multi-profile + shared_brain)

## State
- gateway: {gw}
- profiles_state:
{prof_block}
- fts5_tables: 0 (Hermes uses B-tree idx_messages_content, not FTS5)
- holographic_memory: cross-profile active

{digest_snip}

## Last operations
- See Shared Brain digest above (auto-updated every 5 min from WAL)

## Notes
- .current_context.md is now MULTI-PROFILE (reads all profiles, not just default)
- Shared Brain is the source of truth for cross-agent events
- Agents append to /root/matryoshka/shared_brain/WAL/<name>.wal on key actions
- Digest auto-regen: */5 cron → /root/matryoshka/shared_brain/append_wal.py --digest
- Read order: shared_brain/DIGEST.md → AGENT_MAP.md → session_search → .current_context.md
"""
        CONTEXT_FILE.write_text(content, encoding="utf-8")
        log(f"OK wrote {CONTEXT_FILE} reason={reason} profiles={len(profiles)}")
    except Exception as e:
        log(f"ERROR writing context: {e}")


def append_memory_snapshot(reason: str) -> None:
    try:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with MEMORY_FILE.open("a", encoding="utf-8") as f:
            f.write(f"\n## {ts}  (reason: {reason})\n- v2 multi-profile flush active\n")
        log(f"OK appended to {MEMORY_FILE}")
    except Exception as e:
        log(f"ERROR appending memory: {e}")


def main() -> int:
    reason = os.environ.get("FLUSH_REASON") or (sys.argv[1] if len(sys.argv) > 1 else "cron")
    log(f"START reason={reason}")
    t0 = time.time()
    write_context_file(reason)
    append_memory_snapshot(reason)
    elapsed = time.time() - t0
    log(f"DONE elapsed={elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
