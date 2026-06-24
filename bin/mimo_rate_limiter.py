#!/usr/bin/env python3
"""
mimo_rate_limiter.py — Token bucket rate limiter для MiMo (Xiaomi cloud API)
23.06.2026 — Phase 0.5 (по правкам Аликса, до получения API key)

Защита от бана Xiaomi API (rate limits неизвестны, начинаем консервативно).

Использование:
    from mimo_rate_limiter import MimoRateLimiter

    limiter = MimoRateLimiter(rate_per_minute=5)
    if not limiter.allow():
        return {"ok": False, "error": "rate_limited", "retry_after_sec": limiter.retry_after()}
    # ... call mimo ...
"""
import asyncio
import time
from threading import Lock
from typing import Optional


class MimoRateLimiter:
    """Token bucket: N запросов в минуту (configurable). Thread-safe + async-safe."""

    def __init__(self, rate_per_minute: int = 5, burst: Optional[int] = None):
        self.rate = rate_per_minute / 60.0  # токенов в секунду
        self.capacity = burst if burst is not None else rate_per_minute
        self.tokens = float(self.capacity)
        self.last_refill = time.monotonic()
        self._lock = Lock()
        self._async_lock: Optional[asyncio.Lock] = None
        # Метрики для Prometheus / логов
        self.total_requests = 0
        self.allowed_requests = 0
        self.rate_limited_requests = 0

    def _refill(self) -> None:
        """Пополнить бакет на основе прошедшего времени (sync)."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

    def allow(self) -> bool:
        """Sync: разрешить запрос? Уменьшает bucket на 1."""
        with self._lock:
            self.total_requests += 1
            self._refill()
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                self.allowed_requests += 1
                return True
            self.rate_limited_requests += 1
            return False

    async def aallow(self) -> bool:
        """Async: разрешить запрос? (для использования в mimo_query.py с asyncio)."""
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()
        async with self._async_lock:
            return self.allow()

    def retry_after(self) -> float:
        """Сколько секунд ждать до следующего доступного токена."""
        with self._lock:
            self._refill()
            if self.tokens >= 1.0:
                return 0.0
            return (1.0 - self.tokens) / self.rate

    def stats(self) -> dict:
        """Статистика для /metrics endpoint."""
        return {
            "rate_per_minute": int(self.rate * 60),
            "capacity": self.capacity,
            "current_tokens": round(self.tokens, 2),
            "total_requests": self.total_requests,
            "allowed": self.allowed_requests,
            "rate_limited": self.rate_limited_requests,
        }


# Singleton для Router (используется всеми MiMo-запросами)
_DEFAULT_LIMITER: Optional[MimoRateLimiter] = None


def get_default_limiter() -> MimoRateLimiter:
    global _DEFAULT_LIMITER
    if _DEFAULT_LIMITER is None:
        _DEFAULT_LIMITER = MimoRateLimiter(rate_per_minute=5)
    return _DEFAULT_LIMITER


# === Тесты (запускать: python3 mimo_rate_limiter.py) ===

def test_basic_rate_limit():
    """5 запросов подряд OK, 6-й — rate_limited."""
    limiter = MimoRateLimiter(rate_per_minute=5, burst=5)
    assert limiter.allow() is True, "1st should be allowed"
    assert limiter.allow() is True, "2nd should be allowed"
    assert limiter.allow() is True, "3rd should be allowed"
    assert limiter.allow() is True, "4th should be allowed"
    assert limiter.allow() is True, "5th should be allowed"
    assert limiter.allow() is False, "6th should be rate_limited"
    assert limiter.retry_after() > 0, "retry_after должен быть > 0"
    print("✅ test_basic_rate_limit PASSED")


def test_burst_rate_limit():
    """5 быстрых OK, 6-й → rate_limited (burst pattern из Аликса)."""
    limiter = MimoRateLimiter(rate_per_minute=5, burst=5)
    # 5 burst запросов подряд — все OK
    for i in range(5):
        assert limiter.allow() is True, f"burst #{i+1} должен быть allowed"
    # 6-й сразу — rate_limited (burst exhausted)
    assert limiter.allow() is False, "6-й burst должен быть rate_limited"
    s = limiter.stats()
    assert s["allowed"] == 5, f"allowed={s['allowed']}"
    assert s["rate_limited"] == 1, f"rate_limited={s['rate_limited']}"
    print(f"✅ test_burst_rate_limit PASSED (5 OK + 1 rate_limited)")


def test_stats():
    """Stats корректно отражают счётчики."""
    limiter = MimoRateLimiter(rate_per_minute=10)
    for _ in range(3):
        limiter.allow()
    s = limiter.stats()
    assert s["total_requests"] == 3, f"total={s['total_requests']}"
    assert s["allowed"] == 3, f"allowed={s['allowed']}"
    assert s["rate_limited"] == 0, f"rate_limited={s['rate_limited']}"
    print(f"✅ test_stats PASSED ({s})")


def test_refill():
    """После ожидания — bucket пополняется."""
    limiter = MimoRateLimiter(rate_per_minute=60, burst=1)  # 1 токен, refill быстрый
    assert limiter.allow() is True
    assert limiter.allow() is False
    time.sleep(1.1)  # ждём refill
    assert limiter.allow() is True, "после 1.1 сек должен refill"
    print("✅ test_refill PASSED")


if __name__ == "__main__":
    test_basic_rate_limit()
    test_burst_rate_limit()
    test_stats()
    test_refill()
    print("\n🎉 Все тесты mimo_rate_limiter.py прошли успешно (4/4)")
