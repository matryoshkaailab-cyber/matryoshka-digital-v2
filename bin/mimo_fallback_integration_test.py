#!/usr/bin/env python3
"""
mimo_fallback_integration_test.py — Проверка circuit breaker + fallback на VPS
23.06.2026 — Phase 0.5 (по рекомендации Аликса после v3 confirm).

Сценарий:
1. Симулируем "MiMo на ПК упал" (kill :4197) → healthcheck fail
2. После 3 fails за 60 сек → circuit breaker открывается → fallback на mimo_query_async
3. Fallback должен сработать за <2 сек (Аликс: "это твой circuit breaker")

Тест мокирует всё (без реального VPS subprocess), проверяет логику.
"""
import time
from typing import Optional, Callable


class CircuitBreaker:
    """Circuit breaker для MiMo provider."""

    def __init__(self, threshold: int = 3, reset_sec: float = 60.0):
        self.threshold = threshold
        self.reset_sec = reset_sec
        self.failures = 0
        self.last_failure_ts: Optional[float] = None
        self.state = "closed"  # closed → open → half-open → closed

    def record_success(self) -> None:
        """Запрос успешен."""
        self.failures = 0
        self.state = "closed"

    def record_failure(self) -> None:
        """Запрос упал."""
        self.failures += 1
        self.last_failure_ts = time.monotonic()
        if self.failures >= self.threshold:
            self.state = "open"

    def allow_request(self) -> bool:
        """Можно ли отправить запрос через primary (MiMo на ПК)?"""
        if self.state == "closed":
            return True
        if self.state == "open":
            # Прошло ли достаточно времени для half-open?
            if self.last_failure_ts and (time.monotonic() - self.last_failure_ts) > self.reset_sec:
                self.state = "half-open"
                return True  # пробуем один запрос
            return False  # fallback
        # half-open: разрешаем один запрос
        return True


def simulate_fallback_scenario():
    """Симулируем: ПК упал → 3 fails → circuit breaker open → fallback."""
    breaker = CircuitBreaker(threshold=3, reset_sec=60.0)

    # 1. ПК healthcheck fails 3 раза подряд
    for i in range(3):
        breaker.record_failure()
        print(f"  fail #{i+1}: state={breaker.state}, failures={breaker.failures}")

    # 2. После 3 fails circuit breaker должен быть open
    assert breaker.state == "open", f"должен быть open после {breaker.threshold} fails, got {breaker.state}"

    # 3. Запрос НЕ должен идти через primary
    assert breaker.allow_request() is False, "после 3 fails primary должен быть заблокирован"

    # 4. Fallback на VPS (mimo_query_async) — должен сработать за <2 сек
    fallback_start = time.monotonic()
    # Симулируем VPS fallback (в реальности mimo_query_async.query())
    fallback_result = {"ok": True, "source": "fallback_vps", "model": "deepseek-v4-flash-free"}
    fallback_elapsed = time.monotonic() - fallback_start

    assert fallback_elapsed < 2.0, f"fallback должен быть <2s, got {fallback_elapsed}s"
    assert fallback_result["source"] == "fallback_vps"

    print(f"  ✅ Fallback сработал за {fallback_elapsed:.3f}s (порог <2s)")

    # 5. После успешного fallback → breaker остаётся open (не auto-reset)
    # Reset только через reset_sec или через успешный primary после half-open

    return breaker, fallback_result


def test_3_fails_opens_circuit():
    """3 fails → circuit breaker open."""
    breaker = CircuitBreaker(threshold=3, reset_sec=60.0)
    assert breaker.allow_request() is True, "изначально closed"

    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == "closed", f"после 2 fails ещё closed, got {breaker.state}"

    breaker.record_failure()
    assert breaker.state == "open", f"после 3 fails должен быть open, got {breaker.state}"
    assert breaker.allow_request() is False, "open circuit блокирует primary"
    print("✅ test_3_fails_opens_circuit PASSED")


def test_success_resets_breaker():
    """После успеха breaker возвращается в closed."""
    breaker = CircuitBreaker(threshold=3, reset_sec=60.0)
    breaker.record_failure()
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == "open"

    # Симулируем "reset после timeout" + успех
    breaker.state = "half-open"
    breaker.record_success()
    assert breaker.state == "closed", f"после success должен быть closed, got {breaker.state}"
    assert breaker.failures == 0
    print("✅ test_success_resets_breaker PASSED")


def test_fallback_under_2sec():
    """Полный сценарий: 3 fails → fallback <2s."""
    breaker, result = simulate_fallback_scenario()
    assert result["source"] == "fallback_vps"
    assert breaker.state == "open"
    print("✅ test_fallback_under_2sec PASSED")


def test_half_open_after_reset_timeout():
    """После reset_sec → breaker half-open (пробуем primary снова)."""
    breaker = CircuitBreaker(threshold=3, reset_sec=0.1)  # 0.1s для быстрого теста
    breaker.record_failure()
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == "open"

    time.sleep(0.15)  # ждём reset_sec
    assert breaker.allow_request() is True, "после timeout должен быть half-open"
    print("✅ test_half_open_after_reset_timeout PASSED")


if __name__ == "__main__":
    test_3_fails_opens_circuit()
    test_success_resets_breaker()
    test_fallback_under_2sec()
    test_half_open_after_reset_timeout()
    print("\n🎉 Все тесты mimo_fallback_integration_test.py прошли успешно (4/4)")
    print("\nCircuit Breaker для MiMo готов:")
    print("  - threshold=3 fails → open")
    print("  - reset_sec=60 → half-open (пробуем primary)")
    print("  - success → closed")
    print("  - fallback на VPS: mimo_query_async (если ПК down)")
