#!/usr/bin/env python3
"""
mimo_privacy_filter.py — Privacy middleware для MiMo (Phase 0.5)
23.06.2026 — Блокирует отправку ПДн в Xiaomi cloud.

Правила:
- domain=personal → BLOCK (152-ФЗ)
- [PRIVACY] marker → BLOCK
- ALINA-related (case-insensitive match) → BLOCK
- Всё остальное → ALLOW

Использование в Router:
    from mimo_privacy_filter import check_privacy

    decision = check_privacy(payload)
    if not decision["allowed"]:
        log_audit("privacy_block", actor="router", target="alf-mimo", detail=decision["reason"])
        return decision  # не отправляем в MiMo
    # ... route to MiMo ...
"""
import re
from typing import Dict, Any

# === Privacy rules ===

PERSONAL_DOMAIN_MARKERS = [
    "domain=personal",
    "domain = personal",
    "[privacy]",
    "[personal]",
    "alina_data",
]

# Case-insensitive keywords для ALINA-данных (Николай — отдельный кейс)
# ВАЖНО: дублируем латиницу + кириллицу, т.к. Whisper и пользователи пишут по-разному
ALINA_KEYWORDS = [
    r"\balina\b", r"\bалина\b", r"\bАлина\b",
    r"\bnikolai\b", r"\bnikolay\b", r"\bниколай\b", r"\bНиколай\b",
    r"\bклиент николай\b", r"\bклиент Николай\b",
    r"\bслучай николая\b", r"\bслучай Николая\b",
]

# Теги/маркеры для sensitive данных (можно расширять) — тоже латиница + кириллица
SENSITIVE_TAGS = [
    "passport", "паспорт",
    "snils", "снилс",
    "inn", "инн",
    "medical", "здоровье", "медицин",
]


def check_privacy(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Проверить payload на privacy-маркеры.
    Возвращает {"allowed": bool, "reason": str, "matched": str|None}
    """
    # Сериализуем payload в строку для поиска
    text = _payload_to_text(payload)

    # Правило 1: явный маркер personal/PRIVACY
    for marker in PERSONAL_DOMAIN_MARKERS:
        if marker in text.lower():
            return {
                "allowed": False,
                "reason": f"explicit marker '{marker}'",
                "matched": marker,
            }

    # Правило 2: ALINA-related (отдельный кейс, не идёт в MiMo)
    # Используем substring match вместо \b regex, т.к. underscore — это word char в regex
    # (т.е. \balina\b не сматчит "alina_session")
    text_lower = text.lower()
    alina_patterns_lower = [p.lower() for p in [
        "alina", "алина",
        "nikolai", "nikolay", "николай",
        "клиент николай", "случай николая",
    ]]
    for pattern in alina_patterns_lower:
        if pattern in text_lower:
            return {
                "allowed": False,
                "reason": f"ALINA/Nikolai data detected (pattern: '{pattern}')",
                "matched": pattern,
            }

    # Правило 3: sensitive tags (ПДн)
    for tag in SENSITIVE_TAGS:
        if tag.lower() in text_lower:
            return {
                "allowed": False,
                "reason": f"sensitive tag '{tag}'",
                "matched": tag,
            }

    return {"allowed": True, "reason": "no privacy markers", "matched": None}


def _payload_to_text(payload: Dict[str, Any]) -> str:
    """Преобразовать payload в плоский текст для поиска."""
    parts = []
    for key, value in payload.items():
        if isinstance(value, str):
            parts.append(f"{key}={value}")
        elif isinstance(value, (int, float, bool)):
            parts.append(f"{key}={value}")
        elif isinstance(value, dict):
            parts.append(_payload_to_text(value))
        elif isinstance(value, list):
            parts.append(" ".join(str(x) for x in value))
    return " ".join(parts)


# === Тесты ===

def test_allow_normal():
    """Нормальный запрос — allowed."""
    p = {"question": "проанализируй код ALF на баги", "context": "opencode router"}
    d = check_privacy(p)
    assert d["allowed"] is True, f"должен быть allowed, got {d}"
    print("✅ test_allow_normal PASSED")


def test_block_personal_domain():
    """domain=personal — блок."""
    p = {"question": "обработай данные клиента", "metadata": {"domain": "personal"}}
    d = check_privacy(p)
    assert d["allowed"] is False, "должен быть blocked"
    assert "domain=personal" in d["reason"]
    print(f"✅ test_block_personal_domain PASSED (reason: {d['reason']})")


def test_block_privacy_marker():
    """[PRIVACY] в тексте — блок."""
    p = {"question": "[PRIVACY] данные паспорта клиента"}
    d = check_privacy(p)
    assert d["allowed"] is False
    print(f"✅ test_block_privacy_marker PASSED")


def test_block_alina_keyword():
    """alina в тексте — блок (отдельный кейс)."""
    p = {"question": "что нового у клиента Алина?"}
    d = check_privacy(p)
    assert d["allowed"] is False, "alina должна блокироваться"
    assert "ALINA" in d["reason"] or "Nikolai" in d["reason"]
    print(f"✅ test_block_alina_keyword PASSED")


def test_block_nikolai_keyword():
    """nikolai — блок."""
    p = {"session": "nikolay_session", "task": "summary"}
    d = check_privacy(p)
    assert d["allowed"] is False
    print(f"✅ test_block_nikolai_keyword PASSED")


def test_block_sensitive_tag():
    """medical/health — блок."""
    p = {"question": "обработай medical данные"}
    d = check_privacy(p)
    assert d["allowed"] is False
    print(f"✅ test_block_sensitive_tag PASSED")


def test_allow_technical_code():
    """Технический код — allowed."""
    p = {
        "question": "напиши python функцию для rate limiter",
        "context": "5 req/min token bucket",
    }
    d = check_privacy(p)
    assert d["allowed"] is True
    print("✅ test_allow_technical_code PASSED")


if __name__ == "__main__":
    test_allow_normal()
    test_block_personal_domain()
    test_block_privacy_marker()
    test_block_alina_keyword()
    test_block_nikolai_keyword()
    test_block_sensitive_tag()
    test_allow_technical_code()
    print("\n🎉 Все тесты mimo_privacy_filter.py прошли успешно (7/7)")
    print("Privacy rules:")
    print(f"  - personal domain markers: {len(PERSONAL_DOMAIN_MARKERS)}")
    print(f"  - ALINA keywords: {len(ALINA_KEYWORDS)}")
    print(f"  - sensitive tags: {len(SENSITIVE_TAGS)}")
