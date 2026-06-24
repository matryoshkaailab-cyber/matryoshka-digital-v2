#!/usr/bin/env python3
import os
import json
import urllib.request

ENV_FILE = '/root/.hermes/profiles/hermes-cli/.env'
api_key = None
if os.path.exists(ENV_FILE):
    for line in open(ENV_FILE).read().splitlines():
        if 'MINIMAX_API_KEY=' in line and not line.startswith('#'):
            parts = line.split('=', 1)
            if len(parts) == 2:
                api_key = parts[1].strip()
                break

if not api_key:
    api_key = os.environ.get('MINIMAX_API_KEY', '')

print(f"Key prefix: {api_key[:15]}...")

MINIMAX_API_URL = "https://api.minimax.io/v1/image_generation"
prompt = "Собака-овчарка на сноуборде, реалистичный стиль, зимний пейзаж"
model = "image-01"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": model,
    "prompt": prompt,
    "aspect_ratio": "1:1",
    "response_format": "url",
    "n": 1,
    "prompt_optimizer": True
}

data = json.dumps(payload).encode()
req = urllib.request.Request(MINIMAX_API_URL, data=data, headers=headers, method="POST")

print("Generating...")
with urllib.request.urlopen(req, timeout=180) as resp:
    result = json.loads(resp.read())

image_url = result.get("data", {}).get("image_urls", [None])[0]
print(f"Got URL")

output = "/root/.hermes/profiles/hermes-cli/image_cache/guerra_dog.jpg"
req2 = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req2, timeout=30) as resp:
    with open(output, 'wb') as f:
        f.write(resp.read())

print(f"Saved: {os.path.getsize(output)} bytes")
