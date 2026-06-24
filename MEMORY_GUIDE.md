# MEMORY GUIDE — Как работает моя память в MATRYOSHKA
**Дата создания:** 12.06.2026
**Версия:** 1.0
**Для:** Олега + будущих сессий

---

## 1. ГДЕ ЛЕЖИТ ПАМЯТЬ

Hermes использует **3 слоя памяти**:

| Слой | Путь | Назначение | Срок |
|------|------|------------|------|
| **MEMORY.md** | `/root/.hermes/profiles/hermes-cli/memories/MEMORY.md` | Долговременная память (уроки, факты, константы) | Постоянно |
| **USER.md** | `/root/.hermes/profiles/hermes-cli/memories/USER.md` | Профиль пользователя (кто Олег, привычки, стиль) | Постоянно |
| **Holographic facts DB** | `/root/.hermes/profiles/hermes-cli/memories/fact_store.json` | Структурированные факты с entity resolution | Постоянно |
| **.current_context.md** | `/root/matryoshka/.current_context.md` | Контекст текущей сессии | Обновляется при выходе |
| **Session DB** | `/root/.hermes/profiles/hermes-cli/sessions.db` | FTS5 по всем сессиям | Постоянно |
| **.bak** | `/root/.hermes/profiles/hermes-cli/memories/MEMORY.md.bak.*` | Бэкапы перед каждым изменением | Ротация |

⚠️ **НЕ СУЩЕСТВУЕТ:** `/root/matryoshka/memory/` (это неправильный путь)

---

## 2. ЧТО В КАЖДОМ ФАЙЛЕ

### 2.1. MEMORY.md (мой личный блокнот)
**Лимит:** 2200-5000 символов (конфигурируется)
**Структура:** §-разделённые записи, начинается с даты `[DD.MM.YYYY]`
**Что писать:**
- ✅ Уроки (что выучил)
- ✅ Ошибки (что обосрался, как исправлюсь)
- ✅ Константы проекта (порты, ID, настройки)
- ✅ Правила (мандаты Олега)
- ❌ НЕ логи задач (через session_search)
- ❌ НЕ PR/issue номера (протухают)

### 2.2. USER.md (профиль Олега)
**Лимит:** 1375-3000 символов
**Что писать:**
- ✅ Кто Олег (роль, проект, стиль)
- ✅ Привычки (голосовые 5-30 сек, прямой команды)
- ✅ Триггеры ярости ("заебал", "витаю в облаках")
- ✅ Мандат 08.06 (5 функций цифрового помощника)
- ❌ НЕ технические детали (это в MEMORY)

### 2.3. fact_store (структурированные факты)
**Инструменты:** `fact_store` tool (probe, search, reason, add)
**Возможности:**
- `add(content, tags, category)` — добавить факт
- `search(query)` — найти по ключевому слову
- `probe(entity)` — все факты про сущность
- `related(entity)` — что связано
- `reason(entities=[...])` — факты на стыке
- `contradict()` — найти противоречия

**Категории:** user_pref, project, tool, general
**Trust score:** 0.0-1.0, факт_feedback обновляет

---

## 3. КОГДА ОБНОВЛЯТЬ

### 3.1. MEMORY.md обновлять КОГДА:
- ✅ Олег поправил меня (новое правило)
- ✅ Выучил что-то новое (урок)
- ✅ Открыл новую константу (порт, ID, путь)
- ✅ Перед `compaction` (сжатие контекста)
- ✅ Перед уходом / окончанием сессии

### 3.2. USER.md обновлять КОГДА:
- ✅ Олег рассказал о себе новое
- ✅ Изменились привычки / предпочтения
- ✅ Сменился стиль общения

### 3.3. .current_context.md обновлять КОГДА:
- ✅ При выходе ("ухожу", "пока", "спокойной ночи")
- ✅ Каждые 2-3 часа длинной сессии
- ✅ Перед сменой темы проекта

### 3.4. fact_store обновлять КОГДА:
- ✅ Факт будет полезен через неделю
- ✅ Связь между сущностями (person, project, tool)
- ✅ Trust score < 0.5 (отзыв Олега)

---

## 4. ЛИМИТЫ (конфигурация)

В `/root/.hermes/profiles/hermes-cli/config.yaml`:
```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true        # MUST be true для persistent memory
  memory_char_limit: 5000           # было 2200, увеличили
  user_char_limit: 3000             # было 1375, увеличили
  path: /root/.hermes/profiles/hermes-cli/memories/MEMORY.md
```

**Если лимит превышен** → memory tool вернёт ошибку `Refusing to write MEMORY.md: file on disk has content that wouldn't round-trip`.

**Решение:** убрать старые записи, или увеличить лимит (но не > 8000, иначе prompt будет огромный).

---

## 5. КАК ВОССТАНОВИТЬ ПОСЛЕ ПОТЕРИ

### 5.1. Если MEMORY.md потерян:
```bash
ls /root/.hermes/profiles/hermes-cli/memories/MEMORY.md.bak.*
# Бэкапы ротируются — последний .bak самый свежий
cp /root/.hermes/profiles/hermes-cli/memories/MEMORY.md.bak.1234567890 /root/.hermes/profiles/hermes-cli/memories/MEMORY.md
```

### 5.2. Если session DB corrupt:
```bash
sqlite3 /root/.hermes/profiles/hermes-cli/sessions.db "PRAGMA integrity_check;"
# Если "ok" — не критично
# Если "database disk image is malformed" — нужен recovery
```

### 5.3. Если нужно пересоздать с нуля:
```bash
# Прочитать AGENTS.md и recent session_search → собрать контекст
# Создать чистый MEMORY.md через write_file
# Не забыть записать в .current_context.md
```

---

## 6. СВЯЗАННЫЕ СИСТЕМЫ

### 6.1. Curating skills (curator)
**Cron:** автоматически раз в 48ч проверяет использование skills
**Действия:**
- `stale_after_days` → архивирует
- `archive_after_days` → удаляет (но НЕ удаляет, только архивирует)
- Создаёт backup tar.gz перед изменениями

**Pinned skills** (закреплённые) не архивируются.

### 6.2. Session search
**FTS5** по `sessions.db` — полнотекстовый поиск по прошлым сессиям.
**Когда использовать:** Олег говорит "помнишь?", "что было вчера", "что решили".

### 6.3. .current_context.md
**Путь:** `/root/matryoshka/.current_context.md`
**Что внутри:** что обсуждали, какие файлы, какие решения
**Когда читать:** в начале каждой сессии (ОБЯЗАТЕЛЬНО по мандатам Олега)

---

## 7. CHECKLIST ПЕРЕД ВЫХОДОМ

```
□ Записал новые уроки в MEMORY.md
□ Обновил .current_context.md
□ Записал сессию через session_search
□ Если менял skills — обновил bundle_manifest
□ Если добавлял cron — добавил в .current_context.md
```

---

## 8. PITFALLS

1. **Memory tool откажется писать** если файл изменили вручную (patch, shell, editor)
2. **Write_file маскирует секреты** в .env (видит `***` в выводе)
3. **НЕ ПИСАТЬ** в memory: PR номера, commit SHA, "сделал X" (через session_search)
4. **Лимит символов реален** — не копить 50KB
5. **USER.md ≠ MEMORY.md** — не путать
6. **fact_store ≠ memory** — это разные инструменты

---

## 9. СВЯЗАННЫЕ ФАЙЛЫ

- `~/.hermes/profiles/hermes-cli/memories/MEMORY.md` — активная память
- `~/.hermes/profiles/hermes-cli/memories/USER.md` — профиль Олега
- `~/.hermes/profiles/hermes-cli/memories/fact_store.json` — структурированные факты
- `~/.hermes/profiles/hermes-cli/sessions.db` — FTS5 история
- `~/.hermes/profiles/hermes-cli/config.yaml` — конфиг лимитов
- `/root/matryoshka/.current_context.md` — контекст сессии
- `~/.hermes/profiles/hermes-cli/skills/hermes/never-lose-context/SKILL.md` — подробнее

---

## 10. БЫСТРЫЕ КОМАНДЫ

```bash
# Где моя память?
ls -la /root/.hermes/profiles/hermes-cli/memories/

# Лимиты
grep -A 5 "memory:" /root/.hermes/profiles/hermes-cli/config.yaml

# Проверить целостность
sqlite3 /root/.hermes/profiles/hermes-cli/sessions.db "PRAGMA integrity_check;"

# Бэкапы
ls -lt /root/.hermes/profiles/hermes-cli/memories/*.bak | head -5

# Сколько символов
wc -c /root/.hermes/profiles/hermes-cli/memories/MEMORY.md
```
