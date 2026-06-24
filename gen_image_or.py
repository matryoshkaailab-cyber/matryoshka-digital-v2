#!/usr/bin/env python3
import os
import base64
import json
import requests

# OpenRouter API
api_key = "***"

url = "https://openrouter.ai/api/v1/images/generations"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "google/gemini-2.0-flash-001",
    "prompt": "A German Shepherd dog snowboarder, realistic style, winter mountain landscape, snow, bright sun",
    "image_size": "1024x1024"
}

print("Generating image via OpenRouter...")
response = requests.post(url, headers=headers, json=payload, timeout=120)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2)[:1000])
else:
    print(f"Error: {response.text[:500]}")