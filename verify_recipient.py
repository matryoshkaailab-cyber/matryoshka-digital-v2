#!/usr/bin/env python3
"""ВЕЧНЫЙ СТРАЖ — проверяет любого получателя перед отправкой"""
import json
import sys
import subprocess

def load_blocked():
    try:
        with open('/root/matryoshka/blocked_users.json', 'r') as f:
            data = json.load(f)
            return {str(u['user_id']) for u in data.get('blocked', [])}
    except:
        return set()

def verify(user_id_str):
    blocked = load_blocked()
    user_id = str(user_id_str).strip()
    
    if user_id in blocked:
        print(f"🚫 BLOCKED: {user_id} — ЗАПРЕЩЕНО ОТПРАВЛЯТЬ")
        return False
    
    print(f"✅ ALLOWED: {user_id}")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: verify_recipient.py <user_id>")
        sys.exit(1)
    
    if not verify(sys.argv[1]):
        sys.exit(1)
