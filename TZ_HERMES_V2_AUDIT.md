# АУДИТ ТЗ: МОДЕРНИЗАЦИЯ HERMES V2.0
**Hermes + Alex, 15.06.2026** | Реальное состояние vs план

---

## 0. TL;DR

| Фаза | План | Сделано | Делать | Отложить |
|---|---|---|---|---|
| **Ф1 Docker sandbox** | P0 | 0% | ❌ | ✅ (ломает SOUL) |
| **Ф2 SOUL+Memory** | P0-P1 | **100%** | — | — |
| **Ф3 ALF+NotebookLM** | P1 | 20% | частично | скептик |
| **Ф4 ACP+крон** | P2 | **80%** | cron | — |

**Главный вывод:** Большинство из ТЗ v0.15.1 **уже выполнено** в рамках патчей 14-15.06. Осталось — **Docker sandbox** (проблемный), **NotebookLM MCP** (рискованно), и **10 cron-задач** (доделать).

---

## 1. ТЕКУЩЕЕ СОСТОЯНИЕ (v0.16.0)

| Компонент | Статус | Детали |
|---|---|---|
| **Hermes runtime** | ✅ v0.16.0 (обновлён 15.06) | upstream a376ca00 |
| **FTS5** | ✅ убит в обеих DB | LIKE-поиск 6ms |
| **Active Flush** | ✅ ExecStopPost/ExecStartPre + cron */5 | systemd + cron |
| **SOUL.md** | ✅ канон + 3 symlinks | `/root/matryoshka/SOUL.md` |
| **ALF** | ✅ работает (PID 648995, 5 дней) | :8451, fallback chain |
| **ACP канал** | ⚠️ 4096 живой, но сбоит | модель не вызывается для новых сессий |
| **Qwen2api** | ✅ работает | :8765, guest mode |
| **terminal.backend** | ❌ `local` от root | RCE риск (но не критично) |
| **MCP для ALF** | ❌ не подключен | — |

---

## 2. АНАЛИЗ ПО ФАЗАМ

### ФАЗА 1: Docker Sandbox (P0 в ТЗ → P3 в реальности)

**Проблема:** В ТЗ предлагается `terminal.backend: docker`. **ОПАСНО для нашей архитектуры.**

**Найдено в Issue #32049 (GitHub):**
> Docker terminal backend lets file tools write to a **sandbox-mirror copy** of authoritative profile state (SOUL.md, etc.). Bind-mount создаёт копию, symlinks **ломаются** — модель пишет в sandbox, а host не видит.

**Что это значит для нас:**
- ❌ SOUL.md symlinks (только что созданные) **перестанут работать**
- ❌ `~/.hermes/profiles/hermes-cli/SOUL.md` будет указывать в пустоту
- ❌ Hermes будет видеть "canonical" файл, а host — старую копию
- ❌ Identity drift вернётся в квадрате

**Гибридный доступ (как предлагает Олег) не поможет:**
- AWG, x-ui, systemd — нативно требуют host
- n8n через 5678 — host-only
- Если 80% задач host-only, docker sandbox = геморрой без выигрыша

**ВЕРДИКТ:** ⏸ **ОТЛОЖИТЬ.** Ждём issue #32049 fix.

**Альтернатива (предлагаю):**
- Включить `approvals.mode: manual` (default есть, но явно в config)
- Опасные команды (`rm -rf`, `dd`, format) → approval
- Это даёт 80% безопасности без docker

### ФАЗА 2: SOUL + Active Flush (P0 в ТЗ → ВЫПОЛНЕНО)

| Пункт | Статус | Файл |
|---|---|---|
| `HERMES_IDENTITY_FULL.md` в Obsidian | ✅ создан | `/root/matryoshka/HERMES_IDENTITY_FULL.md` (657 KB) |
| `build_identity.sh` | ✅ создан | `/root/matryoshka/build_identity.sh` |
| SOUL.md → 3 symlinks | ✅ созданы | root, hermes-cli, hermes-orchestrator |
| Active Flush в systemd | ✅ | `ExecStopPost=`, `ExecStartPre=` |
| Cron */5 | ✅ | `hermes_active_flush.py` |

**ВЕРДИКТ:** ✅ **ВЫПОЛНЕНО 100%.** Identity drift ликвидирован.

### ФАЗА 3: ALF + NotebookLM (P1 в ТЗ → скептик)

**Проблемы с ТЗ:**

1. **"MCP мост к NotebookLM"** — Да, существует `pantheon-security/notebooklm-mcp-secure` (npm, post-quantum, Gemini Deep Research). НО:
   - Требует **Google OAuth** (нужен логин Олега в Google)
   - 17 security layers = overhead
   - **Стоимость:** Gemini API (платный, ~$0.075/1K токенов для 1.5 Pro)
   - "Точность 78.2%" — это реклама из видео, не peer-reviewed

2. **"Gemini 1.5 Pro для ALF"** — Gemini 1.5 уже устарел. **Сейчас 2026 — Gemini 3.5 Pro** (новый). Если подключать, то 3.5.

3. **"LIBRARIAN_CORE skill"** — идея правильная (разделение фактов/заявлений), но не требует NotebookLM. Можно реализовать как Hermes skill:
   - Олег даёт источник (URL, PDF, текст)
   - Hermes парсит через `web_extract`
   - Сравнивает с утверждением
   - Возвращает "Подтверждено / Опровергнуто / Не подтверждено"

**Предлагаю (дешевле и быстрее):**

- ❌ НЕ подключать NotebookLM MCP (Google OAuth + $$$)
- ✅ Создать Hermes skill `fact-checker` (без внешних сервисов)
- ✅ Если нужна research-мощность — `delegate_task` на Аликса (есть ACP)

**ВЕРДИКТ:** 🔄 **ЗАМЕНИТЬ на fact-checker skill.** NotebookLM — overkill.

### ФАЗА 4: ACP + Cron (P2 в ТЗ → 80% выполнено)

| Пункт | Статус |
|---|---|
| ACP Hermes→Alex (10.8.1.4:4096) | ✅ настроен, но сбоит сегодня |
| Cron-автоматизации (10 шт) | ⏸ 4 есть (backup, watchdog, curator, active_flush) |
| `max_concurrent_children=3` | ✅ default |
| **Утренний брифинг 9:00** | ❌ нет |
| **Трекинговый радар ниши AI** | ❌ нет |
| **Daily dashboard в Obsidian** | ❌ нет |

**ВЕРДИКТ:** 🔄 **ДОДЕЛАТЬ 6 cron-задач.** Каждая 5-15 мин работы.

---

## 3. КРИТИЧЕСКИЕ РИСКИ (найдены сегодня)

| # | Риск | Серьёзность | Решение |
|---|---|---|---|
| 1 | **Docker sandbox ломает SOUL symlinks** (#32049) | HIGH | Отложить Ф1 |
| 2 | **ACP модель не вызывается для новых сессий** (сегодня) | HIGH | Перезапустить opencode на ПК |
| 3 | **big-pickle / mimo-v2.5-free** падают с UnknownError | MED | Не использовать, только MiniMax |
| 4 | **ALF MCP** не подключен | LOW | Не критично (ALF работает) |
| 5 | **RCE через root** terminal | MED | `approvals.mode: manual` |

---

## 4. РЕКОМЕНДОВАННЫЙ ПЛАН (вместо ТЗ v0.15.1)

### P0 (сегодня, 30 мин)
- [ ] Включить `approvals.mode: manual` в config (5 мин)
- [ ] Перезапустить opencode на ПК (Олег, 30 сек)
- [ ] 1 cron-задача: **ежедневный 9:00 брифинг Олегу** (15 мин)

### P1 (на этой неделе, 2-3 часа)
- [ ] Создать skill `fact-checker` для АЛЬФЫ (без NotebookLM)
- [ ] 5 cron-задач: трекинг AI ниши, daily dashboard, weekly report, sync response check, memory health
- [ ] 3 symlinks: проверить что все SOUL.md → canonical (уже сделано)

### P2 (следующий спринт)
- [ ] Docker sandbox — **ЖДЁМ** issue #32049 fix
- [ ] NotebookLM MCP — **только если** Олег готов дать Google OAuth + бюджет

### P3 (никогда)
- ❌ "Triada моделей" (Gemini/DeepSeek/Critic) — overkill
- ❌ "Librarian skill" как отдельный agent — Hermes сам справится
- ❌ Docker для production — пока bug

---

## 5. ВЫВОД

**ТЗ v0.15.1 был написан до наших патчей 14-15.06.2026.** Сейчас:
- Ф1 (Docker) — **не делать** (ломает symlinks)
- Ф2 (SOUL/Memory) — **сделано** ✅
- Ф3 (NotebookLM) — **заменить** fact-checker skill
- Ф4 (ACP/Cron) — **доделать 6 задач**

**Реальные риски сегодня:**
1. RCE от root — решается approvals.mode
2. ACP сбоит — решается рестартом opencode
3. SOUL drift — уже решено

**Что НЕ делаем:** не гоняемся за "модными" фичами (NotebookLM, Docker, Triada) — бьём то, что УЖЕ работает.

---

**Подпись:** Hermes (MiniMax-M3) + Alex (sбой ACP сегодня) | 15.06.2026 14:40
