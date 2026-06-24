#!/usr/bin/env python3
"""
ALF v4.0 — DEPRECATED standalone server stub.
Используй Hermes gateway + ALF persona вместо этого:
  hermes gateway run --profile alf
  systemctl --user status hermes-gateway-alf
"""
import sys


def main():
    print("=" * 70)
    print("ALF v3 standalone server DEPRECATED")
    print("=" * 70)
    print()
    print("ALF теперь — persona внутри Hermes Agent (профиль alf).")
    print("Standalone сервер не используется.")
    print()
    print("  systemctl --user status hermes-gateway-alf")
    print("  journalctl --user -u hermes-gateway-alf -f")
    print()
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
