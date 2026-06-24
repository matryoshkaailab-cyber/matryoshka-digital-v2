#!/usr/bin/env python3
"""Генерация нового баннера XKIN из существующего через Gemini image editing."""
import base64
import json
import os
import urllib.request
import urllib.error

# Ключ из /root/.hermes/.env
_env_text = open("/root/.hermes/.env").read()
api_key = [l.split("=", 1)[1].strip() for l in _env_text.splitlines() if l.startswith("OPENROUTER_API_KEY=")][0]

SOURCE = "/root/matryoshka/cases/nikolay/work/banner_v17/source.jpg"
OUT_DIR = "/root/matryoshka/cases/nikolay/work/banner_v17"

# Reference image → base64
with open(SOURCE, "rb") as f:
    src_b64 = base64.b64encode(f.read()).decode()

# Промпт на редактирование
prompt = """You are given an advertising banner (1080x1920 portrait) for XKIN accessories.
This is the EXACT source image. You must EDIT it (not recreate from scratch) and preserve the product composition.

=== REMOVE (delete completely) ===
- Text "официальная гарантия 12 месяцев" (top-left)
- "XKIN.RU@YANDEX.RU" email (bottom-center)
- Two phone numbers "Сергей +79181467717" and "Мурат +79298298188" (bottom)
- Two QR codes (bottom-left and bottom-right)
- Telegram paper-plane icon and VK logo icons (bottom)

=== PRESERVE ===
- All products (headphones, TWS earbuds in case, powerbank with wireless charging, charger, cables)
- Blue/cyan gradient background
- White round logo plate with XKIN in center
- Composition, lighting, product placement

=== ADD NEW RUSSIAN TEXT ===
Add these text overlays in CORRECT Russian Cyrillic (NEVER mix Latin letters):

TOP HEADER (replace old text, large white bold):
"Аксессуары от бренда XKIN"

SUBTITLE (smaller white text):
"Производитель Англия • Премиальное качество по доступной цене"

ORANGE BADGE (prominent, orange background or border, white or dark text):
"ГАРАНТИЯ • ОПТ И РОЗНИЦА"

PRICE BLOCK (white card or dark overlay, near bottom-middle):
"Наушники от 700 ₽"
"Повербанк с быстрой зарядкой от 1500 ₽"

CONTACT BLOCK (bottom-center, clean dark or white card):
"Точные цены уточняйте:"
"+7 928 035-50-00"
"WhatsApp · Telegram"

=== STYLE RULES ===
- Background: keep dark blue / cyan gradient
- Accent color: ORANGE (#FF6600) for badges, prices, phone number
- White text for body, orange for emphasis
- Modern sans-serif (Montserrat-style), all Russian words MUST be perfectly spelled
- DO NOT add any new products not in the original
- DO NOT change product colors or positions

=== RUSSIAN SPELLING (MANDATORY — do not corrupt) ===
- "Аксессуары" (NOT "Aксессуары", NOT "Акессуары")
- "производитель" (NOT "произвадитель", NOT "proizvoditel")
- "Премиальное" (NOT "Премиальное" with Latin letters)
- "ГАРАНТИЯ" (NOT "ГАРАНТИ" or with Latin R)
- "Повербанк" (NOT "Повер бaнк", NOT "Powerbank")
- "Точные" (NOT "Точние", NOT "Tochnye")
- "уточняйте" (NOT "уточняите")
- "WhatsApp" and "Telegram" — keep these as Latin brand names, this is correct
- All Cyrillic words must use ONLY Russian letters, no Latin substitutions

=== OUTPUT ===
Output ONE image: 1080x1920 vertical banner, edited version of the source."""

payload = {
    "model": "google/gemini-3.1-flash-image-preview",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{src_b64}"}},
            {"type": "text", "text": prompt}
        ]
    }],
    "modalities": ["image", "text"]
}

print(f"[{__file__}] Отправляю запрос к gemini-2.5-flash-image...")
print(f"Размер исходника: {os.path.getsize(SOURCE)} bytes")

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read())
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="ignore")
    print(f"HTTP {e.code}: {body[:1000]}")
    raise

# Парсинг ответа
msg = result["choices"][0]["message"]
images = msg.get("images", [])
print(f"Получено изображений: {len(images)}")
content = msg.get("content")
print(f"Текст ответа: {(content or '')[:500]}")

# Сохраняем
for i, img in enumerate(images):
    url = img["image_url"]["url"]
    b64 = url.split("base64,", 1)[1]
    out_path = os.path.join(OUT_DIR, f"v17_gemini_{i+1}.png")
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"Сохранено: {out_path} ({os.path.getsize(out_path)} bytes)")

# Usage info
if "usage" in result:
    u = result["usage"]
    print(f"Tokens: prompt={u.get('prompt_tokens')} completion={u.get('completion_tokens')} total={u.get('total_tokens')}")
