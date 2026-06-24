
# Council #3 (Этап 2-3) — ALISA — 21.06.2026

**Тема:** Запуск ALISA (маркетинг/контент агент, Красный рой, @AlisaMatBot)

## УЧАСТНИКИ
- ✅ Аликс ИИ (deepseek-v4-flash-free) — ОТВЕТИЛ
- ❌ ALF (Telegram + chat timeout) — МОЛЧИТ
- ✅ Hermes (дирижёр, я) — counter-анализ + synthesis

## ЭТАП 1: ОТВЕТ АЛИКСА ИИ (полный)

**plan (8 шагов):**
1. PROFILE: .opencode/profiles/alisa/identity.md + opencode.jsonc (DeepSeek V4 Flash)
2. SYSTEMD: /etc/systemd/system/hermes-alisa.service (Type=simple, Restart=always)
3. BOT: @AlisaMatBot токен 8960236150, alisa_telegram_bot.py
4. MODEL: DeepSeek V4 Flash (opencode) + Minimax/DALL-E для графики
5. TOOLS: content-pipeline, graphic-assets, smm-scheduler
6. FIRST USE CASE: MATRYOSHKA WEEKLY (пост-карточка 1080x1080)
7. SUB-AGENTS: 5 sub-ролей
8. AGENT LOOP: builder+judge с ALEX как judge

**sub_roles (5):** copywriter, designer, smm, seo, ideolog
**agent_loop:** ALISA генерит → ALEX judge → score → доработка → аппрув
**risks (4):** DeepSeek не делает изображения / нет UX-дизайнера / контент без верификации / polling conflict
**first_use_case:** MATRYOSHKA WEEKLY через ECLER (проверка фактов)

## ЭТАП 2: COUNTER-АНАЛИЗ HERMES

### 🔴 5 КРИТИЧЕСКИХ ОШИБОК:
1. **ECLER** = ALINA = изолирована, нельзя использовать для MATRYOSHKA
2. **minimax = LLM, не image gen** → нужен DALL-E / gemini-image
3. **ALEX = технарь, не judge контента** → judge = HERMES + Олег
4. **DeepSeek V4 Flash на VPS не настроен** → нужен provider=minimax
5. **ALF молчит** → сначала фикс ALF, потом ALISA

### 🟡 5 НЕДОСКАЗАННЫХ РИСКОВ:
6. Нет @AlisaMatBot — Олег должен создать
7. Нет shared_brain хуков → ALISA забудет контекст
8. Нет жёсткого style guide в profile
9. Нет аппрув-цепочки (кто публикует?)
10. Cron Вс 03:00 cleanup может удалить draft'ы

## ЭТАП 3: SYNTHESIS (финальный план)

### ВАРИАНТ A: "ALISA как sub-agent внутри HERMES" (РЕКОМЕНДУЮ)
- profile = `alisa` внутри hermes-cli (НЕ отдельный systemd)
- model = `provider=minimax/MiniMax-M3` (тот же что у ALF librarian)
- gateway = `hermes-cli-gateway.service` (уже работает)
- sub-agents: copywriter, designer, smm, ideolog (4, без seo пока)
- agent_loop: HERMES сам = judge, Олег = аппрув
- first_use_case: MATRYOSHKA WEEKLY (пост-карточка через gemini-image)
- **PRO:** 1 профиль вместо отдельного systemd, всё в одном gateway
- **CON:** нет отдельного Telegram bot, всё через @oleg_industry_bot

### ВАРИАНТ B: "ALISA как отдельный systemd" (классика, как ALF)
- profile = `alisa` ОТДЕЛЬНЫЙ systemd unit `hermes-alisa-gateway.service`
- model = `provider=minimax/MiniMax-M3`
- Отдельный Telegram bot (Олег создаёт через @BotFather)
- sub-agents: 5 (полный набор)
- agent_loop: ALF (стратег) = judge, Олег = аппрув
- **PRO:** полная изоляция, отдельный TG
- **CON:** новый systemd = новые риски, надо создать bot, надо ещё 1 venv

### 🏆 РЕШЕНИЕ: ВАРИАНТ A (sub-agent) — БЫСТРЫЙ СТАРТ

**ПОЧЕМУ A:**
1. Не нужно создавать systemd (минимум рисков)
2. Не нужно создавать @AlisaMatBot (это отдельная задача Олега)
3. Использует уже работающий provider=minimax
4. agent_loop через HERMES = никаких новых race conditions
5. shared_brain хуки уже подключены для hermes-cli

**ПЛАН A (4 шага, 1-2 дня):**

| # | Шаг | Время | Кто |
|---|-----|-------|-----|
| A1 | Создать /root/.hermes/profiles/alisa/ (config.yaml + SOUL.md + IDENTITY.md style guide) | 30 мин | HERMES |
| A2 | Создать IDENTITY.md (tone: дерзкий-техно, colors: белый/синий/красный, шрифт Montserrat) | 20 мин | HERMES |
| A3 | Создать bin/alisa_subagent.py (вызов через Hermes delegate_task с sub-agent kind=alisa) | 60 мин | HERMES |
| A4 | Тест: запустить alisa_subagent с задачей "сгенери идею для MATRYOSHKA WEEKLY" → проверить | 15 мин | HERMES |

**ПЛАН B (отложен, через 1-2 недели):**
- B1: Олег создаёт @AlisaMatBot через @BotFather
- B2: Отдельный systemd unit
- B3: Отдельный Telegram gateway
- B4: 5 sub-agents

**ПЕРЕД СТАРТОМ:**
- ⚠️ ALF НЕ РАБОТАЕТ (Telegram + chat timeout) — это критично.
  Без ALF рой = 1 голос (только Аликс ИИ через ACP).
  Рекомендую сначала council по фиксу ALF (отдельный этап).

## DISSENTING OPINIONS
- Аликс ИИ: не упомянул что minimax = LLM (ошибка), judge = ALEX (неверно)
- ALF: нет ответа (timeout)
- Hermes: рекомендую Вариант A (sub-agent) для быстрого старта

## РЕШЕНИЕ (нуждается в одобрении Олега)
