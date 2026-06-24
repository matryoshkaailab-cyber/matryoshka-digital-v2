#!/usr/bin/env python3
"""
ALIAS hook: append session summary to shared_brain WAL on session end.
Installed at /root/.hermes/profiles/alf/hooks/on_session_end.py
Also symlinked to default profile for testing.

Use:  echo "summary text" | python3 on_session_end.py alf
or:   python3 on_session_end.py alf "summary text"
"""
import os
import sys
from pathlib import Path

SHARED_BRAIN = Path("/root/matryoshka/shared_brain")
APPEND_WAL = SHARED_BRAIN / "append_wal.py"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: on_session_end.py <agent> [message]")
        return 1
    agent = sys.argv[1]
    if len(sys.argv) >= 3:
        msg = " ".join(sys.argv[2:])
    else:
        msg = sys.stdin.read().strip() or "session ended (no summary)"
    import subprocess
    r = subprocess.run(
        ["/usr/bin/python3", str(APPEND_WAL), agent, msg],
        capture_output=True, text=True, timeout=10,
    )
    print(r.stdout, end="")
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
