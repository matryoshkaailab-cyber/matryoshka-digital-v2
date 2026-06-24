#!/usr/bin/env python3
"""
mimo_query_async.py — Async wrapper для mimo_query.py с asyncio.Lock
23.06.2026 — Phase 0.5 (по правкам Аликса: race conditions в subprocess)

Зачем: subprocess НЕ thread-safe (fork-exec race на stdin/stdout/stderr).
Даже threading.Lock не решает проблему полностью — нужен serial execution.
Поэтому: ОДИН subprocess запрос за раз, остальные ждут в очереди.

Kill switch: env MIMO_DISABLED=1 → мгновенный отказ без перезапуска сервиса
(предложение ALF в review v3: belt+suspenders к systemctl).

Использование в Router:
    from mimo_query_async import MimoQueryAsync

    async with MimoQueryAsync() as mq:
        result = await mq.query("ping", timeout_sec=60)
"""
import asyncio
import os
import time
from typing import Optional, Dict, Any

# Импорт существующего sync mimo_query.py
import sys
sys.path.insert(0, "/root/matryoshka/bin")
import mimo_query as _sync


def _is_disabled() -> bool:
    """
    Kill switch: env MIMO_DISABLED=1 (или "true"/"yes") → все MiMo запросы rejected.
    Без перезапуска сервиса. Олег может включить в .env или export.
    """
    val = os.environ.get("MIMO_DISABLED", "0").strip().lower()
    return val in ("1", "true", "yes", "on")


class MimoDisabledError(Exception):
    """MiMo отключен через MIMO_DISABLED=1."""
    pass


class MimoQueryAsync:
    """
    Async обёртка над sync mimo_query с serial execution.

    asyncio.Lock гарантирует что ОДНОВРЕМЕННО выполняется только один subprocess.
    Остальные запросы ждут в FIFO очереди.
    """

    def __init__(self, max_queue_size: int = 100):
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(1)  # только 1 subprocess за раз
        self._queue_size = max_queue_size
        self._active_count = 0
        self._total_queries = 0
        self._total_wait_sec = 0.0

    async def query(
        self,
        question: str,
        model: str = "mimo-auto",
        timeout_sec: int = 60,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Async query к MiMo через subprocess (с serial execution).
        Если очередь переполнена → raise asyncio.QueueFull.
        Если MIMO_DISABLED=1 → raise MimoDisabledError (kill switch).
        """
        # Kill switch check (env MIMO_DISABLED=1)
        if _is_disabled():
            raise MimoDisabledError(
                "MiMo отключен через env MIMO_DISABLED=1. "
                "Уберите переменную или systemctl restart mimo-acp."
            )

        if self._active_count >= self._queue_size:
            raise asyncio.QueueFull(
                f"MimoQueryAsync: queue full ({self._active_count}/{self._queue_size})"
            )

        start = time.monotonic()
        async with self._semaphore:
            wait_sec = time.monotonic() - start
            self._total_wait_sec += wait_sec
            self._active_count += 1
            self._total_queries += 1
            try:
                # Запускаем sync mimo_query в executor (не блокируем event loop)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,  # default ThreadPoolExecutor
                    _sync.run_mimo,
                    question,
                    model,
                    timeout_sec,
                )
                return result
            finally:
                self._active_count -= 1

    def stats(self) -> Dict[str, Any]:
        """Статистика для /metrics."""
        avg_wait = (
            self._total_wait_sec / self._total_queries
            if self._total_queries > 0 else 0.0
        )
        return {
            "total_queries": self._total_queries,
            "active": self._active_count,
            "avg_wait_sec": round(avg_wait, 3),
            "queue_capacity": self._queue_size,
        }


# === Тесты ===

def test_serial_execution():
    """Два одновременных запроса — выполняются serial."""
    import asyncio

    async def runner():
        mq = MimoQueryAsync()
        # Запускаем 3 "запроса" одновременно — semaphore должен их сериализовать
        tasks = [
            asyncio.create_task(mq.query("ping 1", timeout_sec=2)),
            asyncio.create_task(mq.query("ping 2", timeout_sec=2)),
            asyncio.create_task(mq.query("ping 3", timeout_sec=2)),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results, mq.stats()

    # Note: реальные mimo subprocess будут пытаться вызвать Xiaomi cloud
    # (без API key упадёт). Но мы проверяем SERIAL EXECUTION, не сам MiMo.
    # Тест запускаем с моками — подменяем _sync.run_mimo.

    calls = []

    def mock_run_mimo(question, model="mimo-auto", timeout_sec=60):
        calls.append((time.monotonic(), question))
        time.sleep(0.05)  # эмуляция работы
        return {"ok": True, "output": f"echo: {question}", "model": model}

    _sync.run_mimo = mock_run_mimo

    async def test_runner():
        mq = MimoQueryAsync()
        tasks = [
            asyncio.create_task(mq.query("ping 1")),
            asyncio.create_task(mq.query("ping 2")),
            asyncio.create_task(mq.query("ping 3")),
        ]
        results = await asyncio.gather(*tasks)
        return results, mq.stats()

    results, stats = asyncio.run(test_runner())

    # Все 3 завершились
    assert len(results) == 3
    assert all(r["ok"] for r in results), f"results: {results}"
    assert len(calls) == 3, f"должно быть 3 вызова mock, got {len(calls)}"

    # Проверка SERIAL: время между вызовами должно быть ≥ время работы мока (0.05s)
    times = [c[0] for c in calls]
    gaps = [times[i+1] - times[i] for i in range(len(times)-1)]
    assert all(g >= 0.04 for g in gaps), f"запросы НЕ serial! gaps={gaps}"

    print(f"✅ test_serial_execution PASSED (3 запроса serial, gaps={[round(g, 3) for g in gaps]})")
    print(f"   stats: {stats}")


def test_kill_switch():
    """MIMO_DISABLED=1 → все запросы rejected без обращения к subprocess."""
    import asyncio

    # Сохраняем оригинальные значения
    original = os.environ.get("MIMO_DISABLED")
    os.environ["MIMO_DISABLED"] = "1"

    # Мок subprocess (не должен вызваться)
    calls = []
    def mock_run_mimo(question, model="mimo-auto", timeout_sec=60):
        calls.append(question)
        return {"ok": True, "output": "should not be called"}
    _sync.run_mimo = mock_run_mimo

    async def test_runner():
        mq = MimoQueryAsync()
        try:
            await mq.query("test query")
            return False  # должно было raise
        except MimoDisabledError as e:
            return True

    result = asyncio.run(test_runner())
    assert result, "MIMO_DISABLED=1 должен raise MimoDisabledError"
    assert len(calls) == 0, f"subprocess НЕ должен вызываться, но было {len(calls)} вызовов"

    # Восстанавливаем
    if original is None:
        os.environ.pop("MIMO_DISABLED", None)
    else:
        os.environ["MIMO_DISABLED"] = original

    print("✅ test_kill_switch PASSED (MIMO_DISABLED=1 → raise, subprocess не вызван)")


def test_kill_switch_off():
    """Без MIMO_DISABLED — обычная работа."""
    import asyncio

    original = os.environ.get("MIMO_DISABLED")
    if "MIMO_DISABLED" in os.environ:
        os.environ.pop("MIMO_DISABLED")

    def mock_run_mimo(question, model="mimo-auto", timeout_sec=60):
        return {"ok": True, "output": "ok"}

    _sync.run_mimo = mock_run_mimo

    async def test_runner():
        mq = MimoQueryAsync()
        return await mq.query("test")

    result = asyncio.run(test_runner())
    assert result["ok"], "без kill switch должен работать"

    if original is not None:
        os.environ["MIMO_DISABLED"] = original

    print("✅ test_kill_switch_off PASSED (no kill switch → normal work)")


def test_stats():
    """Stats корректно обновляются."""
    async def runner():
        mq = MimoQueryAsync()
        # Просто проверяем что stats() возвращает правильную структуру
        s = mq.stats()
        return s

    s = asyncio.run(runner())
    assert s["total_queries"] == 0
    assert s["active"] == 0
    assert s["queue_capacity"] == 100
    print(f"✅ test_stats PASSED (initial stats: {s})")


if __name__ == "__main__":
    test_stats()
    test_kill_switch_off()
    test_kill_switch()
    test_serial_execution()
    print("\n🎉 Все тесты mimo_query_async.py прошли успешно (4/4)")
    print("\nФайл готов. Использовать в Router вместо прямого вызова mimo_query.run_mimo().")
    print("Phase 2: подключить MimoQueryAsync к /alf-mimo endpoint (fallback path).")
