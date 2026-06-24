#!/usr/bin/env python3
"""
council_v2.py — Council 2.0 voting logic (Phase 0.5, 3-way с MiMo SOFT FAIL)
23.06.2026 — По правкам Аликса: weight ×1.5 только при context >80K, soft_fail если MiMo down.

Использование:
    from council_v2 import council_decide, VoterConfig

    decision = council_decide(
        decision_text="...",
        context_length=120000,  # >80K → MiMo weight ×1.5
        voters={
            "alf": {"vote": "for", "reason": "...", "voter": "alf-strateg"},
            "librarian": {"veto": False, "reason": "...", "voter": "alf-librarian"},
            "mimo": {"vote": "for", "reason": "...", "voter": "mimo-v2.5"},
        },
    )
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Literal
import time


# === VoterConfig — настройки голосования для каждого voter'а ===

@dataclass
class VoterConfig:
    """Конфигурация одного voter'а в Council."""
    name: str
    weight: float = 1.0
    timeout_sec: float = 60.0
    soft_fail: bool = True  # если True — failure не veto, просто weight=0
    can_veto: bool = False
    veto_categories: list = field(default_factory=list)
    veto_min_confidence: float = 0.95


# Дефолтные конфиги для Council 2.0/3-way
DEFAULT_VOTERS: Dict[str, VoterConfig] = {
    "alf": VoterConfig(
        name="alf",
        weight=1.0,
        timeout_sec=90.0,  # ALF async polling (FileWatcher)
        soft_fail=True,  # timeout fallback
        can_veto=False,
    ),
    "librarian": VoterConfig(
        name="librarian",
        weight=1.0,
        timeout_sec=35.0,  # Librarian sync HTTP, быстрый
        soft_fail=True,
        can_veto=True,
        veto_categories=["security_issue", "data_leak", "compliance_violation"],
        veto_min_confidence=0.90,
    ),
    "mimo": VoterConfig(
        name="mimo",
        weight=1.5,  # Базовый ×1.5 для длинных задач
        timeout_sec=60.0,
        soft_fail=True,  # КЛЮЧЕВО: если MiMo down — weight=0, НЕ veto
        can_veto=True,
        veto_categories=["security_issue", "data_leak"],
        veto_min_confidence=0.95,  # Высокий порог для veto
    ),
}


# === Главная функция решения ===

def council_decide(
    *,
    decision_text: str,
    voters: Dict[str, dict],
    context_length: int = 0,
    custom_configs: Optional[Dict[str, VoterConfig]] = None,
) -> dict:
    """
    Council 2.0 решение с 3-way voting (ALF + Librarian + MiMo).

    Args:
        decision_text: что решаем (для логов)
        voters: {"alf": {"vote": "for"|"against"|"unclear", "reason": "..."}, ...}
                voter может отсутствовать (timeout) или иметь "ok": False (error)
        context_length: если >80K → MiMo weight ×1.5
        custom_configs: override дефолтных конфигов

    Returns:
        {
            "decision_id": "council-...",
            "status": "accepted" | "rejected",
            "votes": {...},  # нормализованные голоса
            "weights_applied": {...},
            "reasons": [...],
            "veto_triggered": Optional[str],
            "elapsed_sec": float,
        }
    """
    start = time.monotonic()
    configs = custom_configs or DEFAULT_VOTERS
    decision_id = f"council-{int(time.time())}-{hex(hash(decision_text) & 0xFFFF)[2:]}"

    # === Step 1: нормализуем голоса, проверяем veto, применяем weight ===

    normalized_votes = {}
    weights_applied = {}
    veto_triggered = None
    reasons = []

    for voter_name, vote_data in voters.items():
        cfg = configs.get(voter_name)
        if cfg is None:
            # Неизвестный voter — пропускаем с warning
            reasons.append(f"unknown voter '{voter_name}', skipped")
            continue

        # === Soft fail: если voter не ответил (timeout/error) — weight=0 ===
        if not vote_data.get("ok", True):
            weights_applied[voter_name] = 0.0
            reasons.append(
                f"{voter_name}: soft_fail (no response) — vote ignored"
            )
            normalized_votes[voter_name] = {"vote": "skipped", "weight": 0.0}
            continue

        # === Vote parsing ===
        vote_value = vote_data.get("vote", "unclear").lower()
        if vote_value not in ("for", "against", "unclear"):
            vote_value = "unclear"

        # === Weight calculation ===
        # MiMo: ×1.5 только при context > 80K (по решению Аликса)
        weight = cfg.weight
        if voter_name == "mimo" and context_length > 80_000:
            weight = cfg.weight  # уже 1.5 в config
            reasons.append(f"mimo: context={context_length} > 80K, weight ×1.5 applied")
        elif voter_name == "mimo":
            # Контекст короткий — MiMo weight = базовый (1.5 всё равно от конфига,
            # но v2 Аликс сказал ×1.5 "ТОЛЬКО для context > 80K" — уточняем)
            weight = 1.0
            reasons.append(f"mimo: context={context_length} ≤ 80K, weight=1.0")

        weights_applied[voter_name] = weight
        normalized_votes[voter_name] = {
            "vote": vote_value,
            "weight": weight,
            "reason": vote_data.get("reason", "")[:200],
        }
        reasons.append(f"{voter_name}: vote={vote_value} (weight={weight})")

        # === Veto check ===
        if cfg.can_veto and vote_data.get("veto", False):
            confidence = vote_data.get("confidence", 0.0)
            category = vote_data.get("category", "")
            if (
                confidence >= cfg.veto_min_confidence
                and category in cfg.veto_categories
            ):
                veto_triggered = f"{voter_name}: VETO on {category} (confidence={confidence:.2f})"
                reasons.append(veto_triggered)
                # Veto — выходим сразу
                break

    # === Step 2: финальное решение ===

    if veto_triggered:
        status = "rejected"
    else:
        # Weighted sum
        for_score = sum(
            v["weight"] for v in normalized_votes.values()
            if v["vote"] == "for"
        )
        against_score = sum(
            v["weight"] for v in normalized_votes.values()
            if v["vote"] == "against"
        )

        if against_score > for_score:
            status = "rejected"
        elif for_score > against_score:
            status = "accepted"
        else:
            # Tie → accepted (fallback по консервативному правилу, как в Council 2.0)
            status = "accepted"
            reasons.append("tie → accepted (fallback)")

    elapsed = time.monotonic() - start

    return {
        "decision_id": decision_id,
        "status": status,
        "decision_text": decision_text[:200],
        "context_length": context_length,
        "votes": normalized_votes,
        "weights_applied": weights_applied,
        "reasons": reasons,
        "veto_triggered": veto_triggered,
        "elapsed_sec": round(elapsed, 3),
    }


# === Тесты ===

def test_3way_all_for():
    """Все 3 ЗА → accepted."""
    d = council_decide(
        decision_text="approve new MiMo integration",
        context_length=120_000,
        voters={
            "alf": {"vote": "for", "reason": "good plan"},
            "librarian": {"veto": False, "reason": "no conflicts"},
            "mimo": {"vote": "for", "reason": "MiMo supports this", "ok": True},
        },
    )
    assert d["status"] == "accepted", f"expected accepted, got {d['status']}"
    assert d["weights_applied"]["mimo"] == 1.5, "mimo должен быть ×1.5 при context>80K"
    print(f"✅ test_3way_all_for PASSED (decision_id={d['decision_id']})")


def test_mimo_down_soft_fail():
    """MiMo timeout → weight=0, остальные решают."""
    d = council_decide(
        decision_text="test soft fail",
        context_length=50_000,
        voters={
            "alf": {"vote": "for", "reason": "ok"},
            "librarian": {"veto": False, "reason": "ok"},
            "mimo": {"ok": False, "error": "timeout"},  # MiMo down
        },
    )
    assert d["status"] == "accepted"
    assert d["weights_applied"]["mimo"] == 0.0, "MiMo down должен быть weight=0"
    assert "soft_fail" in " ".join(d["reasons"])
    print("✅ test_mimo_down_soft_fail PASSED (MiMo down → 2 voters OK)")


def test_mimo_veto_security():
    """MiMo veto на security_issue с high confidence → rejected."""
    d = council_decide(
        decision_text="deploy suspicious code",
        context_length=30_000,
        voters={
            "alf": {"vote": "for", "reason": "ship it"},
            "librarian": {"veto": False, "reason": "ok"},
            "mimo": {
                "vote": "against",
                "veto": True,
                "category": "security_issue",
                "confidence": 0.97,
                "reason": "SQL injection detected",
                "ok": True,
            },
        },
    )
    assert d["status"] == "rejected", f"veto должен reject, got {d['status']}"
    assert d["veto_triggered"] is not None
    print(f"✅ test_mimo_veto_security PASSED (veto: {d['veto_triggered']})")


def test_mimo_veto_low_confidence_not_triggered():
    """MiMo veto, но confidence < 0.95 → veto НЕ срабатывает."""
    d = council_decide(
        decision_text="maybe problematic",
        context_length=30_000,
        voters={
            "alf": {"vote": "for", "reason": "ok"},
            "librarian": {"veto": False, "reason": "ok"},
            "mimo": {
                "vote": "against",
                "veto": True,
                "category": "security_issue",
                "confidence": 0.80,  # ниже порога
                "reason": "maybe issue",
                "ok": True,
            },
        },
    )
    # Veto не сработал → MiMo просто "against" с weight=1.5, но alf+lib = 2.0 for → accepted
    assert d["status"] == "accepted", f"low confidence veto не должен reject: {d}"
    print("✅ test_mimo_veto_low_confidence_not_triggered PASSED")


def test_short_context_mimo_weight_1():
    """Context ≤ 80K → MiMo weight = 1.0 (не 1.5)."""
    d = council_decide(
        decision_text="short task",
        context_length=50_000,
        voters={
            "alf": {"vote": "for", "reason": "ok"},
            "librarian": {"veto": False, "reason": "ok"},
            "mimo": {"vote": "for", "reason": "ok", "ok": True},
        },
    )
    assert d["weights_applied"]["mimo"] == 1.0, f"short ctx: weight should be 1.0, got {d['weights_applied']['mimo']}"
    print("✅ test_short_context_mimo_weight_1 PASSED")


def test_2_voters_only():
    """Council с 2 voters (ALF + Librarian), без MiMo — должен работать."""
    d = council_decide(
        decision_text="тест 2 voters без MiMo",
        context_length=50_000,
        voters={
            "alf": {"vote": "for", "reason": "ok"},
            "librarian": {"veto": False, "reason": "ok"},
            # MiMo нет вовсе (down/unconfigured)
        },
    )
    assert d["status"] == "accepted", f"2 voters должны принимать решение: {d['status']}"
    assert "mimo" not in d["weights_applied"], "MiMo не должно быть в weights_applied"
    print("✅ test_2_voters_only PASSED (ALF + Librarian без MiMo OK)")


def test_majority_against_rejected():
    """2 veto против 1 за → rejected (librarian veto triggered)."""
    d = council_decide(
        decision_text="controversial security issue",
        context_length=30_000,
        voters={
            "alf": {"vote": "for", "reason": "ok"},
            "librarian": {
                "vote": "against",
                "veto": True,
                "category": "security_issue",
                "confidence": 0.92,
                "reason": "detected issue",
            },
            "mimo": {"vote": "for", "reason": "ok", "ok": True},
        },
    )
    assert d["status"] == "rejected", f"librarian veto должен reject, got {d['status']}"
    assert d["veto_triggered"] is not None
    print(f"✅ test_majority_against_rejected PASSED (veto: {d['veto_triggered']})")


if __name__ == "__main__":
    test_3way_all_for()
    test_mimo_down_soft_fail()
    test_mimo_veto_security()
    test_mimo_veto_low_confidence_not_triggered()
    test_short_context_mimo_weight_1()
    test_2_voters_only()
    test_majority_against_rejected()
    print("\n🎉 Все тесты council_v2.py прошли успешно (7/7)")
    print("Council 2.0/3-way voting готов. Подключить к Router в Phase 2.")
