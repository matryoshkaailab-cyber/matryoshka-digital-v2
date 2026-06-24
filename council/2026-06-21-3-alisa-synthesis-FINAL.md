
# Council #3 FINAL — ALISA — 21.06.2026 (3 голоса)

**Тема:** Запуск ALISA (маркетинг/контент, Красный рой, @AlisaMatBot)

## 🐝 УЧАСТНИКИ СОВЕТА (3 ГОЛОСА)

| # | Кто | Канал | Ответ | Сильная сторона |
|---|-----|-------|-------|-----------------|
| 1 | **Аликс ИИ** (deepseek-v4-flash-free) | ACP quiet-otter | 3283 chars (8 шагов) | Технический план |
| 2 | **HERMES** (counter-анализ) | self | 5 ошибок найдено | Гигиена + правила |
| 3 | **ALF** (MiniMax-M3) | chat hermes -p alf | 7942 chars | Стратегия + метрики |

## 📊 СРАВНЕНИЕ МНЕНИЙ

| Аспект | Аликс ИИ | Hermes (counter) | ALF (стратег) |
|--------|----------|------------------|---------------|
| **Positioning** | Не упомянул | — | Витрина + Lead-gen + Thought leadership |
| **Sub-roles** | 5 (cw, des, smm, seo, ideol) | Заменить ECLER | 5: ideol, cw, des, smm, **editor_qa** (SEO лишний) |
| **Agent loop judge** | ALEX | HERMES+Олег (правило #0) | **3-уровневый комитет** (ALEX tech + ALF strategy + Олег veto) |
| **First use case** | MATRYOSHKA WEEKLY | — | WEEKLY + мини-кейс, 2 нед manual → loop с 3-й |
| **Model** | DeepSeek V4 Flash (НЕ настроен) | provider=minimax/MiniMax-M3 | Та же что у ALF (MiniMax-M3) |
| **Image gen** | Midjourney/minimax (ошибка) | DALL-E / gemini-image | — (designer sub-role) |
| **Judge кто** | ALEX | HERMES+Олег | КОМИТЕТ (3 слоя) |
| **Metrics** | Не упомянул | — | 5 метрик M1 (накопление assets) |
| **Critical questions** | — | — | 4 (manifesto, pillars, model, ALEX роль) |

## 🎯 ФИНАЛЬНЫЙ ПЛАН ALISA v1.0

### 1. STRATEGIC POSITIONING
- ALISA = **витрина + lead-gen + thought leadership** (НЕ поддержка, НЕ cannibalization ALINA)
- Граница: ALISA пишет **ДЛЯ рынка**, ALINA/ALEX работают **ВНУТРИ** рынка
- Brand manifesto = первое (Олег + ideolog)

### 2. SUB-ROLES (5) — финальный список

| # | Role | Owner | Зачем |
|---|------|-------|-------|
| 1 | **ideolog** | ALISA | Brand voice, manifesto, content pillars. **ПЕРВЫЙ к запуску.** |
| 2 | **copywriter** | ALISA | Producer длинных форм: посты, статьи, лендинги |
| 3 | **designer** | ALISA + gemini-image | Визуал = 80% внимания. Связка cw+des = пост-карточка |
| 4 | **smm** | ALISA | Дистрибуция, время постинга, A/B заголовков, аналитика |
| 5 | **editor_qa** | ALISA | Gate перед публикацией. Ловит галлюцинации (мандат 18.06). NotebookLM fact-check. **Аликс seo заменён на editor_qa.** |

### 3. AGENT LOOP — 3-уровневый комитет

```
producer (ideolog/cw/des)
  ↓
ALEX (tech QA: промпт, tools, формат, API)
  ↓
ALF (strategy QA: brand voice, метрики, NotebookLM fact-check)
  ↓
Олег (veto/approve, 1 раз/день BATCH, не на каждый пост)
```

**Почему комитет:**
- ALEX соло = без бренд-контроля
- HERMES+Олег = bottleneck на Олеге
- ALF в комитете = стратегия + fact-check (мандат 18.06)

### 4. FIRST USE CASE — MATRYOSHKA WEEKLY

- **Формат:** 1 hero-пост (кейс/запуск недели) + 3 коротких карточки (факт, цитата, тизер)
- **Цикл:** weekly (пятница)
- **M1 (2 недели):** ВРУЧНУЮ — накопить golden examples для fine-tuning ideolog
- **M1 (3-я неделя)+:** agent loop (ideolog → cw → des → editor → ALEX → ALF → Олег)
- **Почему weekly:** повторяемость = предсказуемая нагрузка, можно отлаживать loop

### 5. METRICS M1 (накопление assets, НЕ лиды)

| Метрика | Цель M1 | Зачем |
|---------|---------|-------|
| Time-to-publish | <2 часа от идеи | Скорость loop = зрелость |
| Brand voice consistency | ≥80% слепой тест | Если 50% — дрифт |
| Fact error rate | 0 критич, <2 мелких | Мандат 18.06 |
| Iteration count | median 2 на пост | Много = плохой producer |
| Asset accumulation | ≥4 weekly + ≥4 кейса + 1 manifesto | M1 = накопление, не лиды |

### 6. РИСКИ (P0-P2)

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | **Brand drift** (generic-ИИ голос) | P0 | ideolog + ALF fact-check + 5 golden examples + еженедель brand audit |
| 2 | **Олег bottleneck** (1 judge = 5 постов/день) | P1 | 3-уровневый комитет, Олег = veto 1/день batch |
| 3 | **Cannibalization ALINA** (утечка клиентских данных) | P1 | manifesto "контент про продукт, не клиентов" + ALF аудит 1/мес |
| 4 | **Cold start zero metrics** | P2 | M1 = накопление assets, не лиды (лиды с M2-3) |

## 🔧 ТЕХНИЧЕСКИЙ ПЛАН (от Аликс ИИ, уточнённый Hermes)

| # | Шаг | Время | Кто | Файл |
|---|-----|-------|-----|------|
| 1 | **Brand manifesto** (Олег + ideolog) | 30 мин | Олег → ALF | `/root/matryoshka/alisa/manifesto.md` |
| 2 | **Content pillars** (5 тем) | 20 мин | ALF chat | `/root/matryoshka/alisa/pillars.md` |
| 3 | **profile `alisa`** (config + SOUL + IDENTITY style guide) | 30 мин | HERMES | `/root/.hermes/profiles/alisa/` |
| 4 | **sub-agent через delegate_task** (kind=alisa) | 60 мин | HERMES | `/root/matryoshka/bin/alisa_subagent.py` |
| 5 | **Тест: MATRYOSHKA WEEKLY #1** (вручную, golden example) | 30 мин | HERMES+ALF | `/root/matryoshka/alisa_drafts/2026-06-21_weekly-001.json` |
| 6 | **gate editor_qa через NotebookLM** (fact-check) | 30 мин | ALF | fact-check API |

**Пропустить (пока):**
- ❌ Отдельный systemd (Вариант B) — на M1 не нужен
- ❌ @AlisaMatBot — Олег создаёт через @BotFather (когда нужен, не сейчас)
- ❌ 5 sub-roles как отдельные процессы — все через 1 sub-agent kind=alisa
- ❌ Cron scheduled posting — M2-M3

## 📋 CRITICAL QUESTIONS (от ALF, нужно Олег решить)

| # | Вопрос | Рекомендация |
|---|--------|--------------|
| 1 | Brand manifesto — кто пишет? | **Олег** пишет драфт, ALF-ideolog валидирует |
| 2 | Content pillars — когда? | **ДО запуска** (ДО шага 3) |
| 3 | Модель — та же (MiniMax-M3) или своя? | **Та же** (минимизация расходов) |
| 4 | ALEX judge — тех или тон? | **Только тех** (промпт, tools, API) |

## DISSENTING OPINIONS
- Аликс ИИ: SEO нужен — ❌ отвергнут (ALF + Hermes: editor_qa важнее)
- ALF: 3-уровневый комитет — ✅ принят (вместо ALEX соло)
- Hermes: ALISA как sub-agent (Вариант A) — ✅ принят (без отдельного systemd)

## РЕШЕНИЕ
- **Старт через 1-2 дня** по плану выше
- **Первые 2 недели** вручную (накопить golden examples)
- **С 3-й недели** agent loop (3-уровневый комитет)
- **M2**: ALISA как отдельный systemd + @AlisaMatBot (если M1 успешен)
