#!/usr/bin/env python3
"""
ALF v4.0 — DEPRECATED router stub.
Используй Hermes gateway вместо этого скрипта:
  hermes gateway run --profile alf
  systemctl --user status hermes-gateway-alf

Этот файл оставлен для обратной совместимости со старыми скриптами
(systemd unit, cron, мониторинг). При запуске выводит предупреждение
и не делает ничего.
"""
import sys
import os


def main():
    print("=" * 70)
    print("ALF v3 telegram bot DEPRECATED")
    print("=" * 70)
    print()
    print("Вместо этого используй Hermes gateway с профилем alf:")
    print()
    print("  systemctl --user status hermes-gateway-alf")
    print("  journalctl --user -u hermes-gateway-alf -f")
    print("  hermes gateway list")
    print()
    print("Telegram bot @IlonAnalyticBot уже работает через Hermes.")
    print("Standalone сервер alf_server.py тоже deprecated.")
    print()
    print("Если ты это видишь — какой-то cron/systemd всё ещё вызывает")
    print("старый скрипт. Обнови вызовы на hermes gateway run --profile alf")
    print()
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
