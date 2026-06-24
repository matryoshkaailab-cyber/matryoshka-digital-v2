#!/usr/bin/env python3
import urllib.request, json

with open('/root/.hermes/.env') as f:
    for line in f:
        stripped = line.strip()
        if stripped.startswith('OPENROUTER_API_KEY=') and not stripped.startswith('#'):
            key = line.split('=',1)[1].strip()
            break

models_url = 'https://openrouter.ai/api/v1/models'
req_m = urllib.request.Request(models_url, headers={'Authorization': f'Bearer {key}'})
resp_m = urllib.request.urlopen(req_m, timeout=10)
all_models = json.loads(resp_m.read().decode()).get('data', [])

# Find image generation models specifically
for m in all_models:
    name = m.get('id', '').lower()
    if 'image' in name or 'flash-image' in name or 'generate' in name:
        print(f"=== {m['id']} ===")
        print(m.get('description','')[:400])
        print()

# Check gemini-2.5-flash-image for multimodal
for m in all_models:
    if m['id'] == 'google/gemini-2.5-flash-image':
        print("\n=== gemini-2.5-flash-image FULL INFO ===")
        print(json.dumps(m, indent=2)[:1000])
        break