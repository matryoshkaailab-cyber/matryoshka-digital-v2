#!/usr/bin/env python3.12
"""
gateway_commands_hook.py — Перехватчик команд Telegram.
Вызывается Hermes Agent когда Николай шлёт сообщение.

Если сообщение начинается с / — парсим как команду.
Иначе — обычное сообщение для модели.
"""
import os
import sys
import json
from pathlib import Path

# Команды обрабатываются через telegram_commands.py
TELEGRAM_COMMANDS = "/root/matryoshka/alina/telegram_commands.py"


def is_command(text):
    """Проверяем что это команда (а не обычное сообщение)"""
    text = text.strip()
    if not text:
        return False
    return text.startswith("/")


def run_command(text):
    """Запустить обработчик команд"""
    import subprocess
    r = subprocess.run(
        ["python3.12", TELEGRAM_COMMANDS, text],
        capture_output=True, text=True, timeout=20
    )
    return r.stdout.strip() if r.returncode == 0 else f"❌ Ошибка: {r.stderr}"


# Пример для теста
if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read()
    if is_command(text):
        print(run_command(text))
    else:
        print(f"NOT_COMMAND: {text}")
