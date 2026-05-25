---
name: matryoshka-self-audit
description: Полный самоаудит HERMES — проверить статус системы, найти проблемы, исправить
triggers:
  - Олег просит "аудит" или "проверь себя"
  - После каждого обновления Hermes
  - Раз в неделю (cron)
category: matryoshka
platforms: [linux]
---

# MATRYOSHKA SELF-AUDIT — Проверка HERMES

## Когда запускать

1. Олег просит "аудит", "проверь себя", "анализ"
2. После обновления Hermes (`hermes update`)
3. Cron: раз в неделю (каждый понедельник 09:00)

## Процесс аудита

### Шаг 1: Проверить версию и обновления

```bash
hermes --version
hermes update --check 2>/dev/null || echo "check failed"
```

### Шаг 2: Проверить процессы

```bash
ps aux | grep hermes | grep -v grep
```

Должны быть:
- hermes gateway run --profile hermes-cli (Олег)
- hermes gateway run --profile nikolay (Алина)
- ws_server.py (ALEX connection)

### Шаг 3: Проверить память

```bash
wc -c ~/.hermes/memories/MEMORY.md
wc -c ~/.hermes/memories/USER.md
```

Лимиты: MEMORY.md ≤ 2200, USER.md ≤ 1375

### Шаг 4: Проверить toolsets

```bash
grep -A20 "toolsets:" ~/.hermes/profiles/hermes-cli/config.yaml
```

Должно быть минимум 10: hermes-cli, image_gen, search, browser, delegation, cronjob, memory, session_search, vision, tts, todo

### Шаг 5: Проверить checkpoints

```bash
grep "checkpoints:" -A5 ~/.hermes/profiles/nikolay/config.yaml
```

checkpoints.enabled должен быть true

### Шаг 6: Проверить skills

```bash
ls ~/.hermes/skills/
ls /root/matryoshka/skills/MATRYOSHKA_DIGITAL/
```

Минимум: session-audit, matryoshka-agent-dossier

### Шаг 7: Сравнить с документацией

Документация: https://hermes-agent.nousresearch.com/docs

Проверить:
- Memory system — работает?
- Skills — создаются?
- Session search — работает?
- Checkpoints — включены?
- Web UI — запущен?

### Шаг 8: Записать результаты

В файл /root/matryoshka/sessions/YYYY-MM-DD.md:
```
### AUDIT [timestamp]

Версия: v0.14.0
Процессы: OK/ПРОБЛЕМА
Память: X/2200, Y/1375
Toolsets: OK/НЕДОСТАТОЧНО
Checkpoints: enabled/disabled
Skills: N штук
Problems: ...
Fixes: ...
```

## Формат ответа Олегу

Table format, ALL data на экране:

```
| Проверка | Результат | Статус |
|----------|-----------|--------|
| Version | v0.14.0 | OK/⚠️ |
| Processes | 4 running | OK |
| Memory | 1856/2200 | OK |
| Toolsets | 11 configured | OK |
| Checkpoints | enabled | OK |
```

**Problems:** перечислить
**Fixes:** что сделано