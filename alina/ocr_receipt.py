"""
ocr_receipt.py — OCR для чеков через vision.

Использует Gemini 2.5 Flash (через OpenRouter) — хорошо распознаёт русский текст.
"""
import os
import json
import urllib.request
import base64
from pathlib import Path


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _get_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        env = Path("/root/.hermes/profiles/alina/.env")
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    return key


def ocr_image(image_path: str, question: str = "Извлеки сумму и контрагента") -> dict:
    """
    OCR через Gemini Vision.
    Возвращает: {"ok": True, "text": "...", "extracted": {...}} или {"ok": False, "error": "..."}
    """
    key = _get_api_key()
    if not key:
        return {"ok": False, "error": "OPENROUTER_API_KEY not set"}

    p = Path(image_path)
    if not p.exists():
        return {"ok": False, "error": f"File not found: {image_path}"}

    try:
        image_data = base64.b64encode(p.read_bytes()).decode()
        ext = p.suffix.lstrip(".").lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")

        payload = {
            "model": "google/gemini-2.5-flash",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question + ". Ответь кратко на русском. Если видишь сумму — укажи. Если магазин/контрагента — укажи. Формат: Сумма: X₽\nМагазин: Y"},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_data}"}}
                ]
            }],
            "max_tokens": 500
        }

        req = urllib.request.Request(
            OPENROUTER_URL,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
            text = result["choices"][0]["message"]["content"]
            return {"ok": True, "text": text, "extracted": _parse_receipt(text)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _parse_receipt(text: str) -> dict:
    """Простой парсер из OCR текста."""
    import re
    amount = re.search(r'(\d[\d\s]*)\s*[₽рР]', text)
    return {
        "amount": amount.group(1).strip() if amount else None,
        "raw": text[:300]
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        result = ocr_image(path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Usage: ocr_receipt.py <image_path>")
