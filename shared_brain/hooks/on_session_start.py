#!/usr/bin/env python3
"""
SHARED BRAIN — session start hook.
ГАРАНТИРУЕТ что при старте любой Hermes-сессии агент прочитает DIGEST.
Без этого — RECALL PROTOCOL не работает (мы это уже видели 19.06 утром).

Установка:
  Hermes CLI автоматически вызывает этот hook перед стартом сессии
  если файл лежит в ~/.hermes/profiles/<name>/hooks/on_session_start.py
"""
import os
import sys
from pathlib import Path

SHARED_BRAIN = Path("/root/matryoshka/shared_brain")
DIGEST = SHARED_BRAIN / "DIGEST.md"


def main() -> int:
    # 1. Убедиться что DIGEST свежий (если старше 10 мин — обновить)
    import subprocess
    if DIGEST.exists():
        import time
        age = time.time() - DIGEST.stat().st_mtime
        if age > 600:  # 10 мин
            subprocess.run(
                ["/usr/bin/python3", str(SHARED_BRAIN / "append_wal.py"), "--digest"],
                capture_output=True, timeout=10,
            )
    else:
        subprocess.run(
            ["/usr/bin/python3", str(SHARED_BRAIN / "append_wal.py"), "--digest"],
            capture_output=True, timeout=10,
        )

    # 2. Прочитать DIGEST в stdout — Hermes CLI инжектит это в system prompt
    if DIGEST.exists():
        print(f"\n# ═══ SHARED_BRAIN RECALL (ОБЯЗАТЕЛЬНО ПРОЧИТАТЬ ПЕРВЫМ) ═══")
        print(f"# Файл: {DIGEST}")
        print(f"# Это мандат v4.1 Олега от 19.06.2026 — без этого шага ты 'пиздабол'.")
        print(f"# ═══════════════════════════════════════════════════════════════\n")
        sys.stdout.write(DIGEST.read_text(encoding="utf-8"))
        print(f"\n# ═══ END SHARED_BRAIN RECALL ═══\n")
        return 0
    print("⚠ shared_brain/DIGEST.md не найден", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
