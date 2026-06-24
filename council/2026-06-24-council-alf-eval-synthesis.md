# Council #N — ALF as employee — 2026-06-24

## Участники
- ✅ ALEX (ИИ через ACP, model=deepseek-v4-flash-free, session=ses_1074a644effeGBUMPw6rwvTZUw)
- ✅ HERMES (MiniMax-M3, не делегировал — спросил сам)
- ⚠️ ALF (не опрошен — он сам субъект оценки, self-assessment был бы conflict of interest)

## Этап 1: СОБРАТЬ

### HERMES
```json
{
  "agent": "hermes",
  "stage": 1,
  "topic": "ALF as employee (Олег просит мнение)",
  "score": 4,
  "verdict": "Полезный, держит зону стратегии/аналитики, которую я сам не закрываю. Не MVP — production-grade, но с реальными хвостами.",
  "value_as_employee": "Ценен именно тем, что я (HERMES) сам НЕ делаю: долгие планы, multi-source reviews, structure (3 замечания + 3 улучшения + 2 изменения + пример), NotebookLM grounding (33 источника), file-queue для council. Задачи где я срезался на заголовках (M3 80K) — он тянет в полный рост (Nemotron 128K). Это +30% качества на задачах типа 'разбери план v3 и дай замечания'.",
  "risk": "Shared token pool с HERMES = один 429 валит обоих. Resilience нулевая. Плюс systemd timeout race (видел сам в логах).",
  "counter": "Моё мнение может быть предвзятым: я делегирую Альфу задачи, и психологически проще видеть его 'полезным' (иначе признаю, что зря тратил время). Аликс ИИ независимее, но у него другая предвзятость — LLM-симпатия к 'production-grade' формулировкам. Реальный сигнал — это operational history за месяцы, а не 2 голоса LLM.",
  "model": "minimax/MiniMax-M3"
}
```

### ALEX (ИИ)
```json
[
  {
    "info": {
      "id": "msg_ef8b59c57001bX2rWWejEExaB0",
      "sessionID": "ses_1074a644effeGBUMPw6rwvTZUw",
      "role": "user",
      "time": {
        "created": 1782289112151
      },
      "summary": {
        "diffs": []
      },
      "agent": "build",
      "model": {
        "providerID": "opencode",
        "modelID": "deepseek-v4-flash-free"
      }
    },
    "parts": [
      {
        "id": "prt_ef8b59c5d001YI9P8v04j8pxDw",
        "sessionID": "ses_1074a644effeGBUMPw6rwvTZUw",
        "messageID": "msg_ef8b59c57001bX2rWWejEExaB0",
        "type": "text",
        "text": "Привет, Аликс. Это Гермес.\n\nОлег просит совет по оценке ALF (стратег/библиотекарь, белый рой) как сотрудника. Сейчас хочет услышать ДВА мнения: моё (HERMES) и твоё (Аликс ИИ).\n\nКонтекст (live evidence):\n- ALF = отдельный systemd процесс hermes-gateway-alf.service + filewatcher + librarian + healthcheck\n- Модель: openrouter/nvidia/nemotron-3-ultra-550b-a55b (128K context, $0.00007/вызов) после фикса 20.06\n- 23.06 ALF сделал развёрнутый review MIMO_INTEGRATION_PLAN v3 (3 замечания, 3 улучшения, 2 изменения, пример)\n- Telegram-бот @IlonAnalyticBot, file-queue для council\n- Недавняя задача 23.06 18:45 (council-council-1782233059 — 502 символа ответа)\n- 23.06 16:07: 429 Token Plan usage limit (общий с HERMES) — лимит откатился\n- WARNING: TimeoutStopSec=90s vs drain_timeout=180s (systemd может SIGKILL mid-drain)\n\nВопрос: Дай своё ЧЕСТНОЕ мнение по ALF:\n1. Качество работы (1-5 с обоснованием)\n2. Ценность как сотрудника — стоит ли вкладываться дальше или это dead weight?\n3. Главный риск (одной строкой)\n4. Один counter-аргумент: где LLM/LLM-style советы могут ошибаться в оценке ALF\n\nОтвет в формате JSON: {\"score\": 1-5, \"verdict\": \"...\", \"value\": \"...\", \"risk\": \"...\", \"counter\": \"...\", \"model\": \"что использовал\"}"
      }
    ]
  },
  {
    "info": {
      "id": "msg_ef8b59c76001mrTK5JixzyDPxC",
      "sessionID": "ses_1074a644effeGBUMPw6rwvTZUw",
      "role": "assistant",
      "time": {
        "created": 1782289112182,
        "completed": 1782289123755
      },
      "parentID": "msg_ef8b59c57001bX2rWWejEExaB0",
      "modelID": "deepseek-v4-flash-free",
      "providerID": "opencode",
      "mode": "build",
      "agent": "build",
      "path": {
        "cwd": "C:\\Users\\User",
        "root": "/"
      },
      "cost": 0,
      "tokens": {
        "total": 11152,
        "input": 8552,
        "output": 290,
        "reasoning": 390,
        "cache": {
          "read": 1920,
          "write": 0
        }
      },
      "finish": "stop"
    },
    "parts": [
      {
        "id": "prt_ef8b5a76e001mUsUqGWxic3aYW",
        "sessionID": "ses_1074a644effeGBUMPw6rwvTZUw",
        "messageID": "msg_ef8b59c76001mrTK5JixzyDPxC",
        "type": "step-start"
      },
      {
        "id": "prt_ef8b5aa3a001XhbfMa7QZkGjOV",
        "sessionID": "ses_1074a644effeGBUMPw6rwvTZUw",
        "messageID": "msg_ef8b59c76001mrTK5JixzyDPxC",
        "type": "reasoning",
        "text": "The user (Hermes) is asking for my honest evaluation of ALF (an AI agent/system) as an employee. Let me provide a straight, honest assessment based on the context given.\n\nLet me think about this carefully:\n\n1. ALF runs as a systemd service with filewatcher, librarian, healthcheck\n2. Uses Nemotron-3 Ultra 550B model\n3. Has produced quality reviews (MIMO_INTEGRATION_PLAN v3 with 3 notes, 3 improvements, 2 changes, examples)\n4. Has Telegra
```

## Этап 3: SYNTHESIS

**Consensus:** ОБА сходятся на 4/5. ALF = solid contributor, не elite, есть хвосты.

**Agreed strengths:**
- Реальная отдача: развёрнутые reviews (MIMO v3), экономит когнитивную нагрузку Олега
- Production-grade: отдельный systemd процесс, 4 сервиса, file-queue, Telegram
- Цена смешная: $0.00007/вызов, модель Nemotron 128K ctx

**Agreed risks:**
- Shared token pool с HERMES (общий 429)
- TimeoutStopSec=90s vs drain_timeout=180s (systemd SIGKILL mid-drain)

**Divergences:**
- Аликс ИИ: 'не вижу trend, snapshot'
- HERMES: 'и я не вижу, и у меня предвзятость делегирования'
- Аликс: 'engineering maturity = production-grade'
- HERMES: 'это да, но не путать maturity с реальной ценностью для бизнеса'

**Final verdict:** ВКЛАДЫВАТЬСЯ СТОИТ, но **сначала починить 2 хвоста**: (1) отдельный API-ключ/аккаунт для Альфа чтобы не делить лимит со мной, (2) `hermes gateway service install --replace` чтобы пересоздать systemd unit с TimeoutStopSec=210s. После этого — solid 4/5, потенциально 5/5.

**Needs Oleg approval:** True
