# ALF skill: Obsidian memory

**Назначение:** ALF пишет decisions/rules/memory в Obsidian vault (`/root/obsidian-vault/hermes/`).

## Когда использовать

После каждой значимой задачи ALF пишет запись:
- `decisions/<topic>.md` — обоснование выбора (почему X, не Y)
- `rules/<rule>.md` — обязательное правило
- `memory/<date>-<topic>.md` — дневник событий

## Формат

```
# Title

**Date:** 2026-MM-DD
**Author:** ALF (или ALEX, или HERMES)
**Context:** краткое описание

## What
Что сделано

## Why
Почему

## What works
## What doesn't
```

## Команда

```bash
cat > /root/obsidian-vault/hermes/memory/$(date +%Y-%m-%d)-<topic>.md <<X
...
X
```

(obsidian_watcher.sh делает auto-commit + push каждые 5 мин.)
