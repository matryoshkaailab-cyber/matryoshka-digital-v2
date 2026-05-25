---
name: matryoshka-system-fix
description: P0 fixes для MATROSHKA — включить checkpoints, toolsets, memory saving
triggers:
  - после чистки памяти
  - после потери данных из-за compaction
  - Олег говорит "не сохраняешь результаты"
category: matryoshka
platforms: [linux]
---

# MATRYOSHKA P0 FIXES — Что делать после аудита

## Исправления выполненные 25.05.2026

### 1. Checkpoints nikolay — ВКЛЮЧИТЬ

**Было:**
```yaml
checkpoints:
  enabled: false
```

**Стало:**
```yaml
checkpoints:
  enabled: true
  max_snapshots: 20
  max_total_size_mb: 500
  auto_prune: true
  retention_days: 7
  min_interval_hours: 1
```

**Файл:** `/root/.hermes/profiles/nikolay/config.yaml`

**Проверка:**
```bash
grep "enabled: true" /root/.hermes/profiles/nikolay/config.yaml
```

### 2. Toolsets — расширить до 11

**Было (hermes-cli):**
```yaml
toolsets:
  - hermes-cli
  - image_gen
  - search
```

**Стало:**
```yaml
toolsets:
  - hermes-cli
  - image_gen
  - search
  - browser
  - delegation
  - cronjob
  - memory
  - session_search
  - vision
  - tts
  - todo
```

**Аналогично для nikolay profile**

**Проверка:**
```bash
grep -c "hermes-cli\|browser\|delegation" /root/.hermes/profiles/hermes-cli/config.yaml
```

### 3. Memory saving — процесс

**ПРАВИЛО:**
После каждого "=== ВЫПОЛНИЛ ===" делать:
1. memory add в /root/matryoshka/sessions/YYYY-MM-DD.md
2. Проверить MEMORY.md / USER.md на переполнение

**Лимиты:**
- MEMORY.md: 2200 символов
- USER.md: 1375 символов

**Если переполняется:**
```bash
# Читать текущее
cat ~/.hermes/memories/MEMORY.md

# Чистить: объединять похожие записи, удалять устаревшее
# Правило: 1 запись = 1 факт, коротко
```

### 4. Session audit — защита от compaction

**Файл:** `/root/matryoshka/sessions/YYYY-MM-DD.md`

**Формат:**
```
### [timestamp] — [что делали]

**Сессия:** [session_id]

**Что сделали:**
1. [шаг 1]
2. [шаг 2]

**Результат:**
- [результат 1]
- [результат 2]

**Ошибки:**
- [ошибка 1]

**Статус:** ✓/❌
```

## Как применять эти fixes

1. **При чистке памяти** — сразу восстанавливать важные факты через memory add
2. **При изменении конфига** — обновлять досье агента
3. **При запуске новой сессии** — читать /root/matryoshka/sessions/YYYY-MM-DD.md

## Verification

```bash
# Проверить что checkpoints включены
grep "enabled: true" /root/.hermes/profiles/nikolay/config.yaml

# Проверить toolsets
grep -A15 "toolsets:" /root/.hermes/profiles/hermes-cli/config.yaml | wc -l

# Проверить memory
wc -c ~/.hermes/memories/MEMORY.md
wc -c ~/.hermes/memories/USER.md
```