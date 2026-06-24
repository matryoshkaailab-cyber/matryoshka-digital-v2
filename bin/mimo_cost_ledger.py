#!/usr/bin/env python3
"""
mimo_cost_ledger.py — Трекинг usage MiMo для защиты от cost trap (Phase 0.5+)
23.06.2026 — По предложению ALF в review v3.

Зачем: Xiaomi "free for limited time" — может flip'нуть на paid tier.
Если не трекать usage заранее — счёт может удивить.

Логи: /var/log/matryoshka/mimo/cost.jsonl
Метрики: total tokens, estimated cost, requests per model.
"""
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

LOG_DIR = Path("/var/log/matryoshka/mimo")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LEDGER_PATH = LOG_DIR / "cost.jsonl"

# Известные pricing (по открытым данным Xiaomi, обновлять при изменении)
# Эти цифры — ОЦЕНКА. Реальная стоимость может отличаться.
MODEL_PRICING = {
    "mimo-auto": {
        "input_per_1k": 0.0,   # free for limited time
        "output_per_1k": 0.0,
        "note": "free for limited time — track usage, expect change",
    },
    "xiaomi/mimo-v2.5": {
        "input_per_1k": 0.001,   # ОЦЕНКА: $0.001 / 1K input tokens
        "output_per_1k": 0.002,  # ОЦЕНКА: $0.002 / 1K output tokens
        "note": "estimated pricing (Xiaomi does not publish)",
    },
    "xiaomi/mimo-v2.5-pro": {
        "input_per_1k": 0.005,
        "output_per_1k": 0.010,
        "note": "pro tier — more expensive",
    },
}

# In-memory счётчики
_totals = {
    "requests": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "estimated_cost_usd": 0.0,
    "by_model": {},
}


def record_usage(
    *,
    model: str,
    input_tokens: int,
    output_tokens: int,
    session_id: Optional[str] = None,
    ok: bool = True,
) -> Dict[str, Any]:
    """
    Записать использование MiMo. Возвращает запись с estimated cost.
    """
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["mimo-auto"])
    cost = (input_tokens / 1000.0) * pricing["input_per_1k"] + \
           (output_tokens / 1000.0) * pricing["output_per_1k"]

    _totals["requests"] += 1
    _totals["input_tokens"] += input_tokens
    _totals["output_tokens"] += output_tokens
    _totals["estimated_cost_usd"] += cost

    if model not in _totals["by_model"]:
        _totals["by_model"][model] = {
            "requests": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
        }
    bm = _totals["by_model"][model]
    bm["requests"] += 1
    bm["input_tokens"] += input_tokens
    bm["output_tokens"] += output_tokens
    bm["cost_usd"] += cost

    record = {
        "ts": time.time(),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "session_id": session_id,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(cost, 6),
        "ok": ok,
    }
    try:
        with LEDGER_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        # Не блокируем запрос если лог не пишется
        print(f"[cost_ledger] WARN: failed to write: {e}", flush=True)

    return record


def get_totals() -> Dict[str, Any]:
    """Получить totals для /metrics endpoint."""
    return {
        **_totals,
        "estimated_cost_usd": round(_totals["estimated_cost_usd"], 4),
    }


def format_prometheus() -> str:
    """Prometheus exposition format для cost metrics."""
    t = get_totals()
    lines = [
        "# TYPE mimo_total_requests counter",
        f"mimo_total_requests {t['requests']}",
        "# TYPE mimo_input_tokens counter",
        f"mimo_input_tokens {t['input_tokens']}",
        "# TYPE mimo_output_tokens counter",
        f"mimo_output_tokens {t['output_tokens']}",
        "# TYPE mimo_estimated_cost_usd counter",
        f"mimo_estimated_cost_usd {t['estimated_cost_usd']}",
    ]
    for model, bm in t["by_model"].items():
        lines.append(f"# TYPE mimo_model_requests counter")
        lines.append(f'mimo_model_requests{{model="{model}"}} {bm["requests"]}')
    return "\n".join(lines) + "\n"


# === Тесты ===

def test_record_free_model():
    """mimo-auto (free) → cost = 0."""
    rec = record_usage(model="mimo-auto", input_tokens=1000, output_tokens=500)
    assert rec["estimated_cost_usd"] == 0.0, f"free model должен быть $0, got {rec['estimated_cost_usd']}"
    print(f"✅ test_record_free_model PASSED (cost=${rec['estimated_cost_usd']})")


def test_record_paid_model():
    """xiaomi/mimo-v2.5 → cost > 0."""
    rec = record_usage(model="xiaomi/mimo-v2.5", input_tokens=10_000, output_tokens=5_000)
    expected = (10_000/1000)*0.001 + (5_000/1000)*0.002
    assert abs(rec["estimated_cost_usd"] - expected) < 0.0001, \
        f"expected {expected}, got {rec['estimated_cost_usd']}"
    print(f"✅ test_record_paid_model PASSED (10K+5K tokens = ${rec['estimated_cost_usd']:.4f})")


def test_totals():
    """Totals правильно суммируются."""
    initial = get_totals()
    record_usage(model="mimo-auto", input_tokens=100, output_tokens=50)
    record_usage(model="mimo-auto", input_tokens=200, output_tokens=100)
    t = get_totals()
    delta_requests = t["requests"] - initial["requests"]
    delta_input = t["input_tokens"] - initial["input_tokens"]
    assert delta_requests == 2, f"expected 2 new requests, got {delta_requests}"
    assert delta_input == 300, f"expected 300 new input tokens, got {delta_input}"
    print(f"✅ test_totals PASSED (totals now: {t['requests']} requests, {t['input_tokens']} input tokens)")


def test_ledger_file_created():
    """Ledger файл создаётся при первой записи."""
    if not LEDGER_PATH.exists():
        record_usage(model="mimo-auto", input_tokens=1, output_tokens=1)
    assert LEDGER_PATH.exists(), f"{LEDGER_PATH} должен быть создан"
    last_line = LEDGER_PATH.read_text().strip().splitlines()[-1]
    rec = json.loads(last_line)
    assert "model" in rec
    print(f"✅ test_ledger_file_created PASSED ({LEDGER_PATH})")


def test_prometheus_format():
    """Prometheus output корректный."""
    out = format_prometheus()
    assert "mimo_total_requests" in out
    assert "mimo_estimated_cost_usd" in out
    print(f"✅ test_prometheus_format PASSED")


if __name__ == "__main__":
    test_record_free_model()
    test_record_paid_model()
    test_totals()
    test_ledger_file_created()
    test_prometheus_format()
    print("\n🎉 Все тесты mimo_cost_ledger.py прошли успешно (5/5)")
    print(f"\nТекущие totals: {get_totals()}")
