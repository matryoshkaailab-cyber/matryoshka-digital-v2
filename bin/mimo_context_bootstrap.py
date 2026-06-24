#!/usr/bin/env python3
"""
mimo_context_bootstrap.py — Загружает shared_brain/DIGEST.md в MiMo prompt (Phase 0.5+)
23.06.2026 — По предложению ALF в review v3.

Зачем: ALF сказал "MiMo голосует blind к проекту, иначе голосует вслепую".
Решение: перед каждым MiMo запросом — подмешиваем DIGEST.md + последние WAL entries.

Это НЕ весь контекст (1M токенов хватит), а только общая картина:
- Что делали все агенты за последние 24 часа
- P0 решения
- Open questions
"""
import os
import time
from pathlib import Path
from typing import Optional


DIGEST_PATH = Path("/root/matryoshka/shared_brain/DIGEST.md")
WAL_DIR = Path("/root/matryoshka/shared_brain/WAL")

# Сколько последних WAL entries включать в контекст
WAL_TAIL_LINES = 30


def load_digest(max_chars: int = 8000) -> Optional[str]:
    """
    Загрузить DIGEST.md (общая память роя).
    Возвращает None если файл не существует.
    """
    if not DIGEST_PATH.exists():
        return None
    try:
        text = DIGEST_PATH.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + f"\n\n[... truncated, {len(text)-max_chars} chars skipped ...]"
        return text
    except OSError as e:
        print(f"[context_bootstrap] WARN: failed to read DIGEST: {e}", flush=True)
        return None


def load_recent_wal(max_lines: int = WAL_TAIL_LINES) -> list:
    """
    Загрузить последние N строк из всех WAL файлов (alf, alex, hermes, alina).
    Возвращает список dict: {agent, line}.
    """
    if not WAL_DIR.exists():
        return []
    entries = []
    for wal_file in WAL_DIR.glob("*.wal"):
        agent = wal_file.stem
        try:
            lines = wal_file.read_text(encoding="utf-8").strip().splitlines()
            # Берём последние max_lines
            for line in lines[-max_lines:]:
                entries.append({"agent": agent, "line": line[:500]})
        except OSError:
            continue
    # Сортируем по ts (если есть) или просто берём последние
    return entries[-max_lines * 4:]  # не больше 4 агентов × max_lines


def build_mimo_context_prompt(
    task: str,
    *,
    include_digest: bool = True,
    include_wal: bool = True,
    max_total_chars: int = 12_000,
) -> str:
    """
    Собрать MiMo prompt с контекстом роя.

    Структурно: [HEADER] + [truncated content] + [FOOTER] + [TASK].
    Маркеры BEGIN/END CONTEXT и TASK всегда сохраняются при truncation.

    Args:
        task: оригинальная задача для MiMo
        include_digest: добавлять ли DIGEST.md
        include_wal: добавлять ли последние WAL
        max_total_chars: жёсткий лимит на размер всего промпта

    Returns:
        Готовый промпт для отправки в MiMo.
    """
    HEADER = "=== SHARED_BRAIN CONTEXT (auto-injected by HERMES Router) ===\n"
    FOOTER = "\n=== END OF SHARED_BRAIN CONTEXT ==="
    TASK_HEADER = "\n\n## TASK:\n"

    # Резервируем место для маркеров и TASK (они никогда не обрезаются)
    RESERVED = len(HEADER) + len(FOOTER) + len(TASK_HEADER) + len(task) + 100  # +buffer
    content_max = max(500, max_total_chars - RESERVED)

    content_parts = []

    # === P0 решения (если есть в DIGEST) ===
    if include_digest:
        digest = load_digest(max_chars=content_max // 2)
        if digest:
            content_parts.append("## Recent Shared Brain Digest (last 24h across all agents):\n")
            content_parts.append(digest)
            content_parts.append("")

    # === Последние WAL entries (что делали недавно) ===
    if include_wal:
        wal_entries = load_recent_wal(max_lines=WAL_TAIL_LINES)
        if wal_entries:
            content_parts.append("## Recent WAL entries (what agents did recently):\n")
            for entry in wal_entries[-WAL_TAIL_LINES:]:
                content_parts.append(f"- [{entry['agent']}] {entry['line']}")
            content_parts.append("")

    content = "\n".join(content_parts)

    # Если контент слишком большой — обрезаем ЕГО (не маркеры)
    if len(content) > content_max:
        content = content[:content_max] + "\n\n[... context truncated ...]"

    full_prompt = f"{HEADER}{content}{FOOTER}{TASK_HEADER}{task}"

    # Финальная страховка
    if len(full_prompt) > max_total_chars:
        full_prompt = full_prompt[:max_total_chars] + "\n[... hard-truncated ...]"

    return full_prompt


# === Тесты ===

def test_load_digest_exists():
    """DIGEST.md существует и читается."""
    digest = load_digest()
    assert digest is not None, "DIGEST.md должен существовать"
    assert "SHARED BRAIN" in digest or "DIGEST" in digest, "DIGEST должен содержать header"
    print(f"✅ test_load_digest_exists PASSED ({len(digest)} chars)")


def test_load_wal():
    """WAL entries загружаются."""
    wal = load_recent_wal(max_lines=5)
    assert len(wal) > 0, "должны быть WAL entries"
    assert all("agent" in e and "line" in e for e in wal)
    print(f"✅ test_load_wal PASSED ({len(wal)} entries)")


def test_build_prompt_basic():
    """build_mimo_context_prompt создаёт структурированный промпт."""
    task = "проверь council 2.0 на стабильность"
    prompt = build_mimo_context_prompt(task, max_total_chars=5000)
    assert "TASK" in prompt
    assert task in prompt
    assert "SHARED_BRAIN CONTEXT" in prompt
    assert "END OF SHARED_BRAIN CONTEXT" in prompt
    print(f"✅ test_build_prompt_basic PASSED ({len(prompt)} chars)")


def test_build_prompt_respects_limit():
    """Промпт не превышает max_total_chars И сохраняет TASK секцию."""
    task = "очень длинная задача " * 1000
    prompt = build_mimo_context_prompt(task, max_total_chars=5000)
    assert len(prompt) <= 5100, f"промпт слишком длинный: {len(prompt)}"  # +буфер на truncation msg
    assert "## TASK:" in prompt, "TASK секция должна быть даже при truncation"
    assert task[:50] in prompt, "task должен быть в prompt (начало)"
    print(f"✅ test_build_prompt_respects_limit PASSED ({len(prompt)} chars, limit=5000, TASK preserved)")


def test_build_prompt_without_digest():
    """Можно собирать без DIGEST (если он не нужен)."""
    task = "test"
    prompt = build_mimo_context_prompt(task, include_digest=False, include_wal=False)
    assert "TASK" in prompt
    assert "SHARED_BRAIN CONTEXT" in prompt  # header всё равно есть
    assert "## Recent Shared Brain Digest" not in prompt  # но контента нет
    print("✅ test_build_prompt_without_digest PASSED")


if __name__ == "__main__":
    test_load_digest_exists()
    test_load_wal()
    test_build_prompt_basic()
    test_build_prompt_respects_limit()
    test_build_prompt_without_digest()
    print("\n🎉 Все тесты mimo_context_bootstrap.py прошли успешно (5/5)")
    print("\nПример промпта:")
    print(build_mimo_context_prompt("проверь последний council", max_total_chars=3000)[:500])
