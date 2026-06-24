# Council #N — Мета-проверка алгоритма Олега — 2026-06-24

## Участники

| Кто | Via | Score | Главное |
|---|---|---|---|
| ALEX (ИИ) | ACP, deepseek-v4-flash-free | 3/5 | Persuasion convergence — Step где агенты видят чужие анализы до плана |
| ALF | file-queue, 22 сек | — | **ПОЙМАЛ МЕНЯ**: я насчитал 10 шагов, реально 6 (Этапы 0-6) |
| HERMES | MiniMax-M3, прямой | 4/5 | Завышаю (мой алгоритм), self-counter: реально 3/5 как ALEX |

## ⚠️ Моя ошибка (поймал ALF)

Я заявил Олегу «10 шагов», а в skill — **6 (Этапы 0-6)**. ALF сразу заметил в своём ответе. Это урок 23.06: **никогда не выдавать цифру без live-check по своему же skill**.

## Где оба согласны (ALEX + HERMES)

### ✅ Сильные стороны
- Совпадает с **Hideki multi-agent-council** (independent → cross review)
- Совпадает с **SkillsLLM 3-round pattern**
- **SURF-фаза (GitHub-first)** — УНИКАЛЬНО, нет в industry 2026
- **Heterogeneous roles** (ALF стратег / ALEX технарь / HERMES дирижёр) — diversity, не homogeneous
- Один источник истины (skill) + append-only ledger

### ❌ Критические баги
- **CRITICAL: Persuasion convergence** — агенты видят чужие анализы ДО плана. Nature 2026: **-10..40% accuracy** + **+30% incorrect consensus**
- Нет scoring rubric для выбора лучшего
- Нет termination condition — может зациклиться
- Нет cost model: ~2.5x single-agent (Microsoft Copilot Council benchmark)

## 🎯 3 улучшения, без которых нельзя в production

1. **Ослепить Step "план"** — каждый сначала пишет свой план ВСЛЕПУЮ (только задача + свой анализ), потом cross-review
2. **Devil's Advocate** как формальная роль (Google Adversarial Review Panel pattern)
3. **Scoring rubric** + **termination condition** (max 3 итерации или convergence)

## 📊 Production examples 2026 (найдены в SURF)

- **Anthropic Claude Managed Agents** (8 April 2026, public beta) — production orchestration
- **Google Adversarial Review Panel** — research.google
- **Microsoft Copilot Council** — production debate, ~2.5x cost
- **Focuslead AI Council Framework** — "structured disagreement outperforms single AI"
- **DIVYANSH-675 LLM-Council** — GitHub 50+ stars
- **hideki5123/multi-agent-council** — Round 1 independent → Round 2 cross review

## 💡 Финальный вердикт

**3.5/5** (средний). Идея верная, реализация близка к industry, но **3 улучшения обязательны** перед тем как считать production-ready.

## ❓ Что делаем?

- **A.** Применить 3 улучшения к skill council-workflow-oleg → v1.1, перезапустить workflow
- **B.** Сначала попробовать v1.0 на реальной задаче, собрать метрики, потом улучшать
- **C.** Сразу мигрировать на Claude Managed Agents (Anthropic, 8 April 2026) — не писать своё

Жду решение.

---

**Ledger:** `/root/matryoshka/council/meta-2026-06-24/`
- brief.json
- alex-ai-response.json
- alf-response.json
- hermes-analysis.json
- synthesis.json
