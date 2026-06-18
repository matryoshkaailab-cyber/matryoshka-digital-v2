# 📚 Per-Profile Skills Strategy — MATRYOSHKA DIGITAL

**Дата:** 2026-06-19
**Автор:** ALF
**Статус:** ✅ УЖЕ работает (по docs)

---

## Главный вывод

**Per-profile skills работают by design в Hermes Agent.**

Два уровня:
- `~/.hermes/skills/` — **общие** (single source of truth)
- `~/.hermes/profiles/<X>/skills/` — **специфичные** для профиля (override)

---

## Текущая структура (18.06.2026)

| Директория | Skills | Назначение |
|-----------|--------|------------|
| `/root/.hermes/skills/` | 41 | Общие (bundled + user) |
| `/root/.hermes/profiles/alf/skills/` | 26 | ALF-специфичные (ALF созданные) |
| `/root/.hermes/profiles/alex/skills/` | 18 | ALEX-специфичные |
| `/root/.hermes/profiles/alina-prod/skills/` | 49 | ALINA prod (Николай, самый большой) |
| `/root/.hermes/profiles/alina/skills/` | 20 | ALINA dev |
| `/root/.hermes/profiles/alisa/skills/` | 24 | ALISA |
| `/root/.hermes/profiles/default/skills/` | 24 | Default fallback |
| `/root/.hermes/profiles/hermes-cli/skills/` | 38 | HERMES CLI |
| `/root/.hermes/profiles/hermes-orchestrator/skills/` | 24 | Orchestrator |
| `/root/.hermes/profiles/nikolay/skills/` | 23 | Nikolay |

**Принцип:** общие skills (как `notebooklm`, `gitask`, `cache-cleaner`) лежат в `/root/.hermes/skills/` и доступны всем. Специфичные (как ALF `orchestration`, ALINA `iphone-avito`) — в профиле.

---

## Правила (что где класть)

### Положить в `~/.hermes/skills/` (общее)

✅ Подходит:
- Инструменты для всех (cache-cleaner, github-pr-workflow)
- Knowledge workers (notebooklm, ocr-and-documents)
- Утилиты (file_search, text_replace)
- Memory management (curator, memory-cleaner)
- Cron утилиты (matryoshka-specific)

❌ НЕ подходит:
- Skills зависящие от конкретного API ключа профиля
- Skills с per-profile путями
- Skills которые должны быть недоступны другим

### Положить в `~/.hermes/profiles/<X>/skills/` (специфичное)

✅ Подходит:
- Skills конкретного агента (ALF → `orchestration/ALF_patterns.md`)
- Skills которые могут конфликтовать (например, два skill для одного Telegram бота)
- Skills завязанные на конкретный systemd сервис
- Skills которые Олег явно хочет изолировать

❌ НЕ подходит:
- Generic tools которые нужны всем

---

## Что у нас реально

### ALF skills (alf)
**26 специфичных**, основные категории:
- `autonomous-ai-agents/` — multi-agent workflows
- `devops/` — server admin (stt-faster-whisper-shim я создал)
- `github/` — code review, PRs
- `hermes-*` — hermes-specific
- `matryoshka-*` — наш проект
- `notebooklm/` — symlink на общий
- `orchestration/` — ALF паттерны
- `software-development/` — TDD, debug

**Рекомендация:** Оставить как есть. Это правильная изоляция.

### HERMES CLI skills (hermes-cli)
**38 специфичных** — это самый большой профиль после ALINA-prod.

**Рекомендация:** HERMES-CLI используется как "главный дирижёр". Имеет свой набор orchestration skills. Это правильно.

### ALINA prod (Николай)
**49 skills** — самый большой набор.

**Рекомендация:** Это клиентский бот с кучей специфичных skills (avito, iphone, finance). Изолировано правильно — Николай не видит MATRYOSHKA skills.

---

## Потенциальные улучшения

| # | Улучшение | Зачем |
|---|-----------|-------|
| 1 | **Audit skills alina-prod** — там 49, может есть устаревшие | Чистота |
| 2 | **Sync orchestration/ между alf и hermes-cli** — могут быть разные версии | Consistency |
| 3 | **Doc per-skill** — какие skills доступны для каждого профиля | Onboarding |
| 4 | **Skill 'bundled' marker** — отличать штатные от созданных агентами | Auditing |
| 5 | **Auto-cleanup** — удалять skills которые не используются >30 дней | Storage |

Но всё это — polish. **Система работает.**

---

## Как добавить новый skill

### Общий (для всех):
```bash
# Создать директорию
mkdir -p /root/.hermes/skills/<category>/<skill-name>/

# Создать SKILL.md
cat > /root/.hermes/skills/<category>/<skill-name>/SKILL.md <<'EOF'
---
name: my-skill
description: Что делает
---

# My Skill
...
EOF

# Verify
hermes skills list | grep my-skill
```

### Специфичный (для одного профиля):
```bash
# Создать директорию
mkdir -p /root/.hermes/profiles/<profile>/skills/<category>/<skill-name>/

# Создать SKILL.md (тот же формат)

# Verify
HERMES_PROFILE=<profile> hermes skills list | grep my-skill
```

---

## Bundled vs Custom

Из docs:
> **Primary directory:** `~/.hermes/skills/` (single source of truth)
> - Bundled skills are copied from the repo on fresh install
> - Hub-installed and agent-created skills also live here

**Bundled** — это штатные skills от Nous Research (41 штук). 
**Custom** — это созданные агентами или пользователем (ALF создал `stt-faster-whisper-shim`).

**Различить:** сравнить файл с upstream (`git diff upstream/main -- ~/.hermes/skills/`). Если идентично — bundled.

---

## Связанные ресурсы

- **Docs:** https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- **SKILL.md format:** YAML frontmatter + markdown body
- **Progressive disclosure:** Level 0/1/2 (skills_list / skill_view / file)
- **Hub:** agentskills.io (open standard)

---

## Рекомендация стратега (ALF)

**Оставить как есть.** Per-profile skills работают. Улучшения (sync, audit, docs) — polish на потом.

Главное правило для команды:
- **Утилиты (общие)** → `/root/.hermes/skills/`
- **Специфика (агент)** → `/root/.hermes/profiles/<X>/skills/`
- **Создаёшь skill — подумай**: кому он нужен? Если всем — общий. Если одному — per-profile.

---

*ALF — 2026-06-19. Per-profile skills strategy задокументирована. Система работает.*