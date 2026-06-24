#!/usr/bin/env python3
"""
Получить OAuth-токен для Яндекс.Диска через PKCE flow.
Запуск: python3 yadisk_get_token.py
"""
import hashlib
import base64
import secrets
import sys
import urllib.parse
import urllib.request
import json

def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

# 1. Генерируем PKCE
code_verifier = b64url(secrets.token_bytes(48))
code_challenge = b64url(hashlib.sha256(code_verifier.encode()).digest())

CLIENT_ID = input("Вставь ClientID из oauth.yandex.ru (только ID, без пробелов): ").strip()

# 2. Ссылка для браузера
params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "redirect_uri": "https://oauth.yandex.ru/verification_code",
    "scope": "cloud_api:disk.read cloud_api:disk.write cloud_api:disk.info",
}
url = "https://oauth.yandex.ru/authorize?" + urllib.parse.urlencode(params)
print("\n=== ОТКРОЙ ЭТУ ССЫЛКУ В БРАУЗЕРЕ ===")
print(url)
print("===\n")
print("Яндекс покажет страницу с кодом. Скопируй его и вставь сюда.\n")

code = input("Authorization code: ").strip()

# 3. Обмен кода на токен
data = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "code": code,
    "client_id": CLIENT_ID,
    "code_verifier": code_verifier,
    "redirect_uri": "https://oauth.yandex.ru/verification_code",
}).encode()

req = urllib.request.Request("https://oauth.yandex.ru/token", data=data)
try:
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
except urllib.error.HTTPError as e:
    print(f"ОШИБКА {e.code}: {e.read().decode()}")
    sys.exit(1)

if "access_token" not in resp:
    print("Ошибка:", resp)
    sys.exit(1)

token = resp["access_token"]
print(f"\n✅ ТОКЕН ПОЛУЧЕН:\n{token}\n")
print(f"Действует: {resp.get('expires_in', '?')} сек")
print(f"Token type: {resp.get('token_type', '?')}")

# Сохранить в .env
env_path = "/root/.hermes/profiles/alina/.env"
try:
    with open(env_path) as f:
        content = f.read()
    # Удалить старую строку, если есть
    lines = [l for l in content.splitlines() if not l.startswith("YANDEX_DISK_TOKEN=")]
    lines.append(f"YANDEX_DISK_TOKEN={token}")
    with open(env_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n💾 Токен сохранён в {env_path}")
except Exception as e:
    print(f"\n⚠️  Не удалось записать в .env: {e}")
    print("Скопируй токен вручную:")
    print(f'  export YANDEX_DISK_TOKEN="{token}"')
