"""
notebooklm_client.py — клиент NotebookLM для Алины.

Использует Hermes tools (browser_navigate/snapshot/click) для автономной работы.
Без OAuth, без API — через реальный браузер.

⚠️ ЗАВИСИМОСТЬ: работает только если вызвано через Hermes subprocess.
"""
import os
from typing import Optional


NOTEBOOKLM_BASE = "https://notebooklm.google.com"
NOTEBOOK_URL = os.getenv("NOTEBOOKLM_URL",
                         "https://notebooklm.google.com/notebook/9d68c355-7f1f-46c6-b9fd-407292f070c8")


def is_configured() -> bool:
    return bool(NOTEBOOK_URL)


def ask_via_hermes(query: str) -> str:
    """
    Вызывает Hermes через subprocess для browser automation.
    Возвращает текст ответа NotebookLM.

    Пример вызова: ask_via_hermes("Что такое Mirror Sync v3.3?")
    """
    if not is_configured():
        return "[ERR: NOTEBOOKLM_URL not configured]"

    # Используем Hermes CLI через subprocess
    import subprocess
    hermes_bin = "/usr/local/lib/hermes-agent/venv/bin/hermes"
    prompt = f"""Зайди на {NOTEBOOK_URL}, авторизуйся, задай вопрос в NotebookLM: "{query}".
Верни КРАТКО (1-3 абзаца) основной ответ. НЕ объясняй свои действия — только ответ."""

    try:
        result = subprocess.run(
            [hermes_bin, "chat", "-q", prompt, "-Q", "--max-turns", "15"],
            capture_output=True, text=True, timeout=180
        )
        return result.stdout.strip() if result.returncode == 0 else f"[ERR: {result.stderr[:200]}]"
    except subprocess.TimeoutExpired:
        return "[ERR: timeout 180s]"
    except Exception as e:
        return f"[ERR: {e}]"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print(ask_via_hermes(q))
    else:
        print("Usage: notebooklm_client.py <query>")
