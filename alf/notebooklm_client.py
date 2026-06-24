"""
NotebookLM client for ALF — browser automation через Hermes tools.
Без OAuth, без MCP, без API — только реальный браузер.

⚠️ ЗАВИСИМОСТЬ: работает только внутри Hermes-сессии (browser_navigate/snapshot/click).
Для автономной работы ALF нужен другой подход (см. notebooklm_simple.py).
"""
import json
import os
import time
import urllib.parse
from typing import Optional

NOTEBOOKLM_BASE = "https://notebooklm.google.com"
NOTEBOOK_URL = os.getenv("NOTEBOOKLM_URL", "")  # Полный URL notebook

# Заглушки — реальные вызовы работают только через Hermes tools
def ask_notebooklm_simple(query: str) -> dict:
    """
    Простая версия — возвращает заглушку.
    Использует только если NOTEBOOK_URL не задан.
    """
    return {
        "ok": False,
        "error": "NOTEBOOKLM_URL not configured. Set it in /root/matryoshka/alf/.env",
        "fallback_to": "ask_brain"
    }

def ask_notebooklm_browser(query: str, timeout: int = 60) -> dict:
    """
    ВЕРСИЯ ДЛЯ HERMES — использует browser_navigate/snapshot/click.
    ВЫЗЫВАТЬ ТОЛЬКО ИЗ HERMES (не из alf_server.py напрямую).
    """
    if not NOTEBOOK_URL:
        return ask_notebooklm_simple(query)

    # Этот код выполняется ТОЛЬКО если вызван из Hermes
    # Внутри alf_server.py нужен wrapper через subprocess/hermes-cli
    return {
        "ok": False,
        "error": "browser_automation not callable from alf_server.py. Use hermes-alf-bridge.sh",
        "fallback_to": "ask_brain"
    }

def is_configured() -> bool:
    """Check if NotebookLM URL is set."""
    return bool(NOTEBOOK_URL)
