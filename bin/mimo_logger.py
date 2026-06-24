#!/usr/bin/env python3
"""
mimo_logger.py — Structured logging для MiMo (Phase 0.5)
23.06.2026 — Логи: request, error, audit. Метрики для Prometheus.

Путь: /var/log/matryoshka/mimo/{request,error,audit}.log (JSONL)
"""
import json
import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

LOG_DIR = Path("/var/log/matryoshka/mimo")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# === JSONL логгеры (без ротации — добавим позже если нужно) ===

_request_log_path = LOG_DIR / "request.log"
_error_log_path = LOG_DIR / "error.log"
_audit_log_path = LOG_DIR / "audit.log"

# In-memory счётчики для Prometheus-style /metrics
_metrics = {
    "mimo_requests_total": 0,
    "mimo_errors_total": 0,
    "mimo_latency_seconds_sum": 0.0,
    "mimo_latency_seconds_count": 0,
    "mimo_privacy_blocks_total": 0,
    "mimo_rate_limits_total": 0,
}


def _write_jsonl(path: Path, data: Dict[str, Any]) -> None:
    """Append JSON line to log file. Best-effort, не падаем если диск полный."""
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except OSError as e:
        # Если логи не пишутся — fallback в stderr, но НЕ raise
        logging.error(f"mimo_logger: failed to write {path}: {e}")


def log_request(
    *,
    question: str,
    model: str,
    elapsed_sec: float,
    ok: bool,
    output_preview: str = "",
    error: Optional[str] = None,
    session_id: Optional[str] = None,
) -> None:
    """Логировать MiMo запрос."""
    _metrics["mimo_requests_total"] += 1
    _metrics["mimo_latency_seconds_sum"] += elapsed_sec
    _metrics["mimo_latency_seconds_count"] += 1
    if not ok:
        _metrics["mimo_errors_total"] += 1
    _write_jsonl(_request_log_path, {
        "ts": time.time(),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "session_id": session_id,
        "model": model,
        "elapsed_sec": round(elapsed_sec, 3),
        "ok": ok,
        "question_len": len(question),
        "question_preview": question[:200],
        "output_preview": output_preview[:200],
        "error": error,
    })


def log_error(
    *,
    where: str,
    error: str,
    question: str = "",
    session_id: Optional[str] = None,
) -> None:
    """Логировать ошибку MiMo (не привязанную к конкретному запросу)."""
    _metrics["mimo_errors_total"] += 1
    _write_jsonl(_error_log_path, {
        "ts": time.time(),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "session_id": session_id,
        "where": where,
        "error": error[:500],
        "question_preview": question[:200],
    })


def log_audit(
    *,
    action: str,
    actor: str,
    target: str = "",
    detail: str = "",
    session_id: Optional[str] = None,
) -> None:
    """Логировать аудит-событие (privacy block, rate limit, council vote)."""
    if action == "privacy_block":
        _metrics["mimo_privacy_blocks_total"] += 1
    elif action == "rate_limit":
        _metrics["mimo_rate_limits_total"] += 1
    _write_jsonl(_audit_log_path, {
        "ts": time.time(),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "session_id": session_id,
        "action": action,
        "actor": actor,
        "target": target,
        "detail": detail[:300],
    })


def get_metrics() -> Dict[str, Any]:
    """Вернуть текущие метрики (для /metrics endpoint Router)."""
    count = _metrics["mimo_latency_seconds_count"]
    avg_latency = _metrics["mimo_latency_seconds_sum"] / count if count > 0 else 0.0
    return {
        **_metrics,
        "mimo_latency_seconds_avg": round(avg_latency, 3),
    }


def format_prometheus() -> str:
    """Форматировать метрики в Prometheus exposition format."""
    m = get_metrics()
    lines = []
    for k, v in m.items():
        lines.append(f"# TYPE {k} counter")
        lines.append(f"{k} {v}")
    return "\n".join(lines) + "\n"


# === Тесты ===

def test_log_request():
    log_request(
        question="test ping",
        model="mimo-v2.5",
        elapsed_sec=0.5,
        ok=True,
        output_preview="pong",
    )
    assert _request_log_path.exists(), f"{_request_log_path} не создан"
    last_line = _request_log_path.read_text().strip().splitlines()[-1]
    rec = json.loads(last_line)
    assert rec["model"] == "mimo-v2.5"
    assert rec["ok"] is True
    print(f"✅ test_log_request PASSED (last record: {rec['iso']})")


def test_log_error():
    log_error(where="mimo_query", error="API timeout")
    assert _error_log_path.exists()
    print("✅ test_log_error PASSED")


def test_log_audit_privacy():
    log_audit(action="privacy_block", actor="router", target="alf-mimo", detail="domain=personal")
    log_audit(action="rate_limit", actor="router", target="alf-mimo", detail="6 req/min")
    assert _audit_log_path.exists()
    m = get_metrics()
    assert m["mimo_privacy_blocks_total"] >= 1
    assert m["mimo_rate_limits_total"] >= 1
    print(f"✅ test_log_audit_privacy PASSED (metrics: {m})")


def test_metrics_prometheus():
    out = format_prometheus()
    assert "mimo_requests_total" in out
    print(f"✅ test_metrics_prometheus PASSED (len={len(out)} bytes)")


if __name__ == "__main__":
    test_log_request()
    test_log_error()
    test_log_audit_privacy()
    test_metrics_prometheus()
    print("\n🎉 Все тесты mimo_logger.py прошли успешно")
    print(f"Логи: {LOG_DIR}")
    print(f"\nМетрики:\n{format_prometheus()}")
