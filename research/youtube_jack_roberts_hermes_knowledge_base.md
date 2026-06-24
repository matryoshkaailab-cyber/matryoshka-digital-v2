# Jack Roberts — "Build a Hermes Knowledge Base That Self-Improves"

**URL:** https://www.youtube.com/watch?v=D3dQqqDx2V4
**Автор:** Jack Roberts (AI-бизнес после Somalethic startup)
**Длина:** 14:29 (869 сек)
**Источник идей:** Andrej Karpathy (сооснователь OpenAI, ex-Tesla AI, Eureka Labs) — концепция "LLM working / Obsidian RAG"

---

## TL;DR (главная мысль за 30 сек)

У Hermes отличная conversational memory (`memory.md`/`user.md`), но Hermes **знает только то, что ты ему сказал**. Inbox, звонки, документы, экспертные видео — для него невидимы.

**Решение:** подключить к Hermes внешнюю self-improving wiki (по концепции Karpathy), куда Hermes и ты можете писать двусторонне. Wiki переписывает сама себя, ищет связи, флаг противоречий, и растёт как "Wikipedia твоего мира". Hermes читает её перед ответом → суперсила.

---

## Ключевые идеи

### 1. Проблема Hermes memory
- Hermes пишет в `memory.md`, `user.md`, facts → помнит разговоры
- НЕ помнит: inbox, calls, docs, research, экспертные видео, заметки
- Это "conversation-only memory" — слепое пятно на правой стороне стены

### 2. Karpathy LLM Wiki (Obsidian RAG)
- Wiki, которая **переписывает сама себя по мере роста**
- Каждый новый файл → wiki читает → создаёт source page → обновляет связанные страницы → флаг contradictions
- Не просто RAG (поиск по вектору), а **active reorganization**
- Файлы структурированы, ссылки видимы — можно визуализировать граф знаний в dashboard

### 3. Архитектура решения
```
[ Ты + Hermes ]  ←→  [ LLM Wiki на Obsidian ]  ←→  [ Внешние источники ]
     ↑                      ↓
  Conversational       Self-improving
    memory             knowledge base
```
- Hermes = про тебя (личное)
- Wiki = про твой мир (эксперты, встречи, заметки, статьи)
- Вместе = агент, который отвечает с полным контекстом

### 4. Практический pipeline (шаги из видео)

**Шаг 1 — Setup wiki:**
- Скачать/склонить шаблон LLM wiki (Jack даёт URL в видео, `clod.md` — инструкция для агента)
- Создать desktop-папку `obsidian_wiki/`
- Внутри — структура страниц + ingestion workflow (`clod.md` говорит агенту: read → discuss → write source page → update affected pages → flag contradictions)

**Шаг 2 — Подключить к Hermes:**
- В Personas → создать новый persona "LLM Wiki"
- System prompt: "Reference my Obsidian wiki при любых вопросах про стратегию / встречи / контекст"
- Альтернатива: попросить Hermes собрать этот skill самому

**Шаг 3 — Ingest контента:**
- Скопировал статью → кинул в чат с Hermes → "Index this into my obsidian wiki"
- Hermes читает `clod.md` (правила), создаёт страницу по правилам

**Шаг 4 — Автоматизация через cron:**
- "Каждое утро в 9:00 проверяй Granola (записи встреч), новые встречи индексируй в wiki"
- Hermes создал cron job → wiki растёт сама
- NotebookLM → тоже коннектится, ингест экспертных видео → wiki получает 50-100 источников разом

### 5. Двусторонняя связь (главная фишка)
- **Ты → wiki → Hermes:** добавил статью → wiki обновилась → Hermes видит в следующем ответе
- **Hermes → wiki:** большая беседа → "index this into my wiki" → wiki растёт
- **Auto-ingest:** cron подтягивает встречи/почту/ноутбук без твоего участия
- **Не засоряя memory.md** — wiki хранит "мир", memory.md хранит "тебя"

### 6. Универсализация (operating system)
- Claude Code тоже читает ту же wiki (через skill "obsidian-ask")
- Hermes, Claude Code, любой другой агент имеют доступ к **одному и тому же корпусу знаний**
- Не "тысяча интерфейсов для тысячи тулов" — один граф знаний, много консьюмеров

---

## Что это значит для MATRYOSHKA / Hermes у Олега

### У нас уже есть похожее:
- **Obsidian vault** на VPS (nginx-webdav-skill) — точка хранения
- **`never-lose-context` skill** — про перенос контекста между сессиями
- **memory store** через `~/.hermes/profiles/hermes-cli/memories/` — memory.md эквивалент
- **fact_store** — структурированная holographic memory, в отличие от flat memory.md

### Что можно взять из видео прямо сейчас:

**А) Подключить Obsidian vault к Hermes как wiki:**
- Nix уже развернул webdav
- Создать skill `obsidian-wiki-reader` который читает vault по ключевым словам и подмешивает в контекст
- В fact_store / skills указать "wiki location"

**Б) Двусторонняя автоматизация:**
- Cron: "раз в день пройдись по новым встречам/задачам и добавь в vault"
- В чате Олег может сказать "запиши это в вики" → Hermes пишет .md в vault

**В) Self-improving ingestion rules:**
- Создать `clod.md` аналог — инструкция для себя "как структурировать новую страницу"
- При пополнении vault — проверять связи и противоречия

**Г) Personas / Skill из видео:**
- В Hermes уже есть профили (`profiles/nikolay/`, `profiles/ecler/`) — это и есть personas-эквивалент
- Можно сделать "wiki persona" который принудительно подгружает vault-контекст

### Что не нужно:
- Granola, notebookLM — это их инфра; у нас свой VPS + Obsidian + n8n

---

## Цитаты (заметные моменты)

- 0:00 — "Permis has the best memory of any AI agent... But there's one thing it can't do."
- 2:38 — "Hermis knows you, but it doesn't know your inbox."
- 3:00 — "[Karpathy's] core idea with Hermis Agent as it rewrites itself as it grows."
- 7:00 — "Hermi's knows everything about you. And then we have this LLM wiki, what Hermi's itself can just send things over there."
- 11:30 — "Set up a recurring task on every day... adds new meetings to my wiki."
- 14:00 — "Memory is great, but it's only one part of the puzzle."

---

## Вывод

Jack Roberts продаёт capsule-идею: **Karpathy's LLM wiki + Hermes = универсальная память агента**. Технически просто (Obsidian + skill + cron), но архитектурно сильно: разделяет "что Hermes знает про тебя" (memory.md/user.md) и "что Hermes знает про мир" (wiki). Делает memory масштабируемой за пределы диалогов.

Для MATRYOSHKA — это roadmap-пункт: подключить Obsidian vault как двустороннюю wiki к Hermes уже сейчас. Технических блокеров нет.
