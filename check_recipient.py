#!/usr/bin/env python3
"""Проверка получателя перед отправкой данных"""
import json
import sys

def load_blocked():
    try:
        with open('/root/matryoshka/blocked_users.json', 'r') as f:
            data = json.load(f)
            return {u['user_id'] for u in data.get('blocked', [])}
    except:
        return set()

def load_users():
    try:
        with open('/root/matryoshka/user_ids.json', 'r') as f:
            data = json.load(f)
            return data.get('users', {})
    except:
        return {}

def check_recipient(user_id_str):
    blocked = load_blocked()
    users = load_users()
    
    user_id = str(user_id_str)
    
    if user_id in blocked:
        return {"allowed": False, "reason": "POLZOVATEL ZABLOKIROVAN", "user": users.get(user_id, {})}
    
    if user_id in users:
        return {"allowed": True, "user": users[user_id]}
    
    return {"allowed": False, "reason": "POLZOVATEL NE NAIDEN V SPISKE DOZvolENNYH"}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: check_recipient.py <user_id>")
        sys.exit(1)
    
    result = check_recipient(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if not result['allowed']:
        sys.exit(1)
