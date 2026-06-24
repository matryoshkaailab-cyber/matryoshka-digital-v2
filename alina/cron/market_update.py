#!/usr/bin/env python3.12
"""Обновить рыночные цены через API"""
import urllib.request
import json
from datetime import datetime

LOG = "/var/log/alina_market.log"

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

try:
    req = urllib.request.Request("http://localhost:8475/update", method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read())
        log(f"Updated: {result.get('updated')}")
        print(f"OK: {result.get('updated')}")
except Exception as e:
    log(f"ERR: {e}")
    print(f"ERR: {e}")
