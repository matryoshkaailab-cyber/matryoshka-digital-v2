#!/usr/bin/env python3
"""
clients_db.py — утилита для таблицы клиентов MATRYOSHKA.

Использование:
  clients_db.py init                — создать таблицу + засеять тестовыми
  clients_db.py list                — все клиенты
  clients_db.py add <name> <tg> <ip> <plan> <status>
  clients_db.py active              — только active
  clients_db.py count               — количество
"""
import sys
import sqlite3
from pathlib import Path

DB = Path("/root/matryoshka/data/clients.db")
DB.parent.mkdir(parents=True, exist_ok=True)


def conn():
    c = sqlite3.connect(str(DB))
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                telegram TEXT,
                vpn_ip TEXT,
                status TEXT DEFAULT 'active',
                plan TEXT,
                contact_date TEXT,
                notes TEXT,
                created_at INTEGER DEFAULT (strftime('%s','now'))
            )
        """)
        # seed if empty
        cnt = c.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        if cnt == 0:
            seed = [
                ("Oleg Chut",          "@oleglab22",   "10.8.1.2",  "VIP",     "active",  "2026-06-01", "Owner"),
                ("Natalya (Zarni An)", "@natalya_za",   "10.8.1.3",  "Standard","active",  "2026-05-28", "Гончарная школа Зарни Ань, ALINA bot"),
                ("Leonid (Legion)",    "@leonid_pc",   "10.8.1.4",  "Pro",     "active",  "2026-05-15", "Legion PC Club"),
                ("Елена",              "@elena_x",     "10.8.1.5",  "Standard","active",  "2026-05-05", "From Yandex.Disk folder"),
                ("Документы Матрёшка", "@matryoshka_dg","10.8.1.6", "Basic",   "trial",   "2026-03-07", "Trial period"),
                ("TASYA (AMNEZIA)",    "@tasya_amn",   "10.8.1.7",  "Standard","active",  "2026-05-13", "AmneziaWG config"),
                ("Client #7",          "@client7",     "10.8.1.8",  "Standard","paused",  "2026-04-12", "Paused by request"),
                ("Client #8",          "@client8",     "10.8.1.9",  "Pro",     "active",  "2026-05-20", "VPN + ALISA marketing"),
                ("Client #9",          "@client9",     "10.8.1.10", "Standard","active",  "2026-05-25", ""),
                ("Client #10",         "@client10",    "10.8.1.11", "Basic",   "trial",   "2026-05-30", "New trial"),
            ]
            c.executemany(
                "INSERT INTO clients (name, telegram, vpn_ip, plan, status, contact_date, notes) VALUES (?,?,?,?,?,?,?)",
                seed,
            )
            print(f"Seeded {len(seed)} clients")
        else:
            print(f"Already has {cnt} clients, skipping seed")
    print(f"DB: {DB}")


def list_all():
    with conn() as c:
        rows = c.execute("SELECT * FROM clients ORDER BY id").fetchall()
    if not rows:
        print("  (empty)")
        return
    print(f"  ID  {'Name':<22} {'Telegram':<18} {'VPN IP':<11} {'Plan':<10} {'Status':<8} {'Contact':<10}")
    print(f"  --  {'-'*22} {'-'*18} {'-'*11} {'-'*10} {'-'*8} {'-'*10}")
    for r in rows:
        print(f"  {r['id']:<3} {r['name']:<22} {(r['telegram'] or '-'):<18} {(r['vpn_ip'] or '-'):<11} {(r['plan'] or '-'):<10} {(r['status'] or '-'):<8} {(r['contact_date'] or '-'):<10}")


def list_active():
    with conn() as c:
        rows = c.execute("SELECT * FROM clients WHERE status='active' ORDER BY id").fetchall()
    for r in rows:
        print(f"{r['id']}|{r['name']}|{r['telegram'] or ''}|{r['vpn_ip'] or ''}|{r['plan'] or ''}|{r['contact_date'] or ''}|{r['notes'] or ''}")


def add(name, telegram="", ip="", plan="", status="active", contact="", notes=""):
    with conn() as c:
        c.execute(
            "INSERT INTO clients (name, telegram, vpn_ip, plan, status, contact_date, notes) VALUES (?,?,?,?,?,?,?)",
            (name, telegram, ip, plan, status, contact, notes),
        )
    print(f"Added: {name}")


def count():
    with conn() as c:
        n = c.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
        a = c.execute("SELECT COUNT(*) FROM clients WHERE status='active'").fetchone()[0]
    print(f"total={n} active={a}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "init":      init()
    elif cmd == "list":    list_all()
    elif cmd == "active":  list_active()
    elif cmd == "add":     add(*sys.argv[2:])
    elif cmd == "count":   count()
    else:
        print(f"Unknown: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
