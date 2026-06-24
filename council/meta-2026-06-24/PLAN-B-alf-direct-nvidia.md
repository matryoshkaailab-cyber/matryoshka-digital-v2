# ПЛАН Б — filewatcher → прямой NVIDIA API
**Дата:** 2026-06-24 | **Заказчик:** Олег | **Совместная работа:** HERMES + ALEX (ИИ через ACP)

---

## 0. SURF (Этап 1 по алгоритму Олега)

**Источники:**
- **GitHub** (10+ репозиториев из council-workflow-oleg meta-анализа): DIVYANSH-675/LLM-Council, hideki5123/multi-agent-council, nityatimalsina/council-consensus, focuslead/ai-council-framework, andrewvaughan/agent-council — все используют **прямой OpenAI-compatible API** (без обёрток)
- **Официальные доки NVIDIA:** `https://docs.nvidia.com/nim/.../nemotron-3-nano-omni-30b-a3b-reasoning/api.html` — подтверждает OpenAI compatibility + extra_body для reasoning
- **NVIDIA NIM для разработчиков** (`decodethefuture.org/en/nvidia-nim-api-explained`): бесплатный tier = 1,000 credits + **40 RPM** + no credit card + nvapi- key
- **YouTube (NVIDIA Developer, 215K subs):** "How to Use Nemotron 3 Nano" — OpenAI-compatible endpoint + thinking mode on/off
- **openai Python SDK** (`github.com/openai/openai-python/issues/547`): кастомный `base_url` через `OpenAI(base_url=...)` — стандартный паттерн
- **AI SDK** (`ai-sdk.dev/providers/openai-compatible-providers/nim`): официальный провайдер для NVIDIA NIM

**Ключевые находки SURF:**
1. **Все production multi-agent frameworks используют прямой API**, не обёртки (agent-council, hideki5123, focuslead — все на direct OpenAI-compatible)
2. **NVIDIA API** — OpenAI-compatible, `base_url="https://integrate.api.nvidia.com/v1"`, key = `nvapi-...`
3. **Thinking/reasoning** — через `extra_body={"chat_template_kwargs": {"enable_thinking": True}, "reasoning_budget": 16384}` (NVIDIA-специфика)
4. **Rate limit бесплатного tier ~5-40 RPM** (разные источники, надо проверить live)
5. **openai 2.43.0 уже в venv** (`/usr/local/lib/hermes-agent/venv/`)

---

## 1. ТЕКУЩАЯ ПРОБЛЕМА

`alf_filewatcher.py:50-67` — функция `call_alf()`:
```python
def call_alf(question: str, timeout: int = ALF_TIMEOUT) -> tuple[str, str]:
    result = subprocess.run(
        ["hermes", "-p", "alf", "chat", "-q", question, "-Q"],
        capture_output=True, text=True, timeout=timeout
    )
```

**Что не так:**
- `hermes -p alf chat` — чёрный ящик, **теряет `extra_body`** (chat_template_kwargs, reasoning_budget)
- Не передаёт `temperature`, `top_p` из config
- Длинные вопросы (>400 chars) обрезаются до заголовка (M3-style limitation)
- **Live-check доказал:** прямой API с параметрами Олега = 4 сек + reasoning 153 chars. Через Hermes Agent = 50-100 chars только заголовок.

---

## 2. ПЛАН РЕАЛИЗАЦИИ

### Шаг 1: Заменить `call_alf()` на прямой OpenAI SDK вызов

**Файл:** `/root/matryoshka/bin/alf_filewatcher.py`

```python
# Добавить imports
import httpx
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
import time

# Заменить call_alf()
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"  # НЕ менять без одобрения Олега
MAX_RETRIES = 3
TIMEOUT_SEC = 180  # reasoning ответы могут идти долго

def _make_alf_client() -> OpenAI:
    api_key = os.environ.get('NVIDIA_API_KEY')
    if not api_key:
        raise ValueError("NVIDIA_API_KEY not set in env")
    return OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=api_key,
        http_client=httpx.Client(timeout=httpx.Timeout(TIMEOUT_SEC, connect=10.0))
    )

def call_alf(question: str, timeout: int = ALF_TIMEOUT) -> tuple[str, str]:
    """Call ALF via direct NVIDIA API (Nemotron 550B, OLEG params)."""
    client = None
    last_error = ""
    for attempt in range(MAX_RETRIES):
        try:
            if client is None:
                client = _make_alf_client()
            resp = client.chat.completions.create(
                model=NVIDIA_MODEL,
                messages=[{"role": "user", "content": question}],
                temperature=1,
                top_p=0.95,
                max_tokens=16384,  # Олег: max_tokens=16384
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": True},
                    "reasoning_budget": 16384  # Олег: reasoning_budget=16384
                }
            )
            content = resp.choices[0].message.content or ""
            reasoning = resp.choices[0].message.reasoning_content or ""
            full = (reasoning + "\n\n" + content).strip() if reasoning else content
            finish = resp.choices[0].finish_reason
            if finish == "length":
                full = f"[TRUNCATED at {resp.usage.completion_tokens} tokens] " + full
            return full, ""
        except RateLimitError as e:
            last_error = f"RATE_LIMIT (attempt {attempt+1}/{MAX_RETRIES}): {str(e)[:200]}"
            time.sleep(2 ** attempt)  # exponential backoff
        except APITimeoutError as e:
            last_error = f"TIMEOUT (attempt {attempt+1}/{MAX_RETRIES}): {str(e)[:200]}"
            time.sleep(2 ** attempt)
        except APIError as e:
            last_error = f"API_ERROR (attempt {attempt+1}/{MAX_RETRIES}): {str(e)[:200]}"
            time.sleep(2 ** attempt)
        except Exception as e:
            last_error = f"EXC: {type(e).__name__}: {str(e)[:200]}"
            break
    return "", last_error
```

**Что НЕ меняем:**
- atomic claim, retry механику, WAL append, .sent/, process_inbox() — всё работает
- ALF_TIMEOUT (300s) — это верхний предел для subprocess-level timeout, остаётся как fallback

### Шаг 2: Установить `httpx` если нет (зависимость openai SDK)

```bash
pip show httpx  # уже есть (transitively через openai)
```

### Шаг 3: Тесты (5 unit-тестов от Аликса)

**Файл:** `/root/matryoshka/bin/tests/test_alf_direct.py`

1. `test_ping` — модель отвечает, токены > 0
2. `test_model_identity` — модель знает "Nemotron/NVIDIA/llama"
3. `test_long_response` — > 200 слов при `max_tokens=4096`
4. `test_rate_limit_retry` — 2 фейковых 429 + 1 success = 3 вызова
5. `test_timeout_retry` — 1 фейковый timeout + 1 success

### Шаг 4: Live-валидация после patch

```bash
# 1. Backup
cp /root/matryoshka/bin/alf_filewatcher.py /root/matryoshka/bin/alf_filewatcher.py.bak.$(date +%Y%m%d_%H%M%S)

# 2. Patch (через patch tool или write_file)
# 3. Test 1 — прямой test
python3 -c "from alf_filewatcher import call_alf; print(call_alf('ping'))"

# 4. Restart ALF (через cron-job — sandbox блокирует изнутри)
# 5. Live-тест через file-queue (ping с правильным форматом)
```

### Шаг 5: Обновить документы

- `ALF_FULL.md` — записать что `call_alf()` теперь прямой API
- `SOUL.md` — убрать упоминания "Hermes Agent CLI"
- `ALF_CURRENT_STATE_24.06.md` — новый changelog

---

## 3. РИСКИ (от Аликса, проверено)

| Риск | Вероятность | Действие |
|---|---|---|
| **NVIDIA API 429** (rate limit) | Medium | exponential backoff (2-30s), 3 retries |
| **NVIDIA API 503/5xx** | Low | retry → fallback на старый subprocess |
| **API key revoked** | Low | AuthenticationError → WAL + Telegram alert |
| **Network partition** | Low | retry → fallback |
| **Reasoning не работает на Nemotron 3 Ultra 550B** | Low (live-check показал что работает) | тест #2 покажет |
| **xai_filewatcher.py не существует** (Аликс галлюцинировал) | Done — пишем с нуля по openai 2.43.0 API | — |
| **tenacity не установлен** | Решено — свой retry через `for` + `time.sleep` | — |

---

## 4. ЧТО ПОЛУЧИМ ПОСЛЕ

| Метрика | Сейчас (Hermes Agent) | После (прямой API) |
|---|---|---|
| Время ответа на "ping" | 30-50 сек | **4-5 сек** |
| Полнота длинного ответа | 50-100 chars (только заголовок) | **полный** (16384 tokens max) |
| Reasoning работает | ❌ нет (теряется в обёртке) | ✅ **да** (153+ chars в live-check) |
| Температура/Top_p | берутся defaults | ✅ 1/0.95 как Олег |
| Extra body (chat_template_kwargs) | ❌ теряется | ✅ передаётся |
| Health monitoring | через Hermes healthcheck | через try/except в retry |
| Fallback на старый путь | — | нужен добавить |

---

## 5. КОНКРЕТНЫЕ ДЕЙСТВИЯ (что я делаю vs Аликс)

| # | Действие | Кто | Время |
|---|---|---|---|
| 1 | Patch `call_alf()` (готовый код выше) | HERMES | 10 мин |
| 2 | Установить httpx если нет | HERMES | 1 мин |
| 3 | Написать 5 unit-тестов | HERMES | 15 мин |
| 4 | Backup + Patch + Smoke-test | HERMES | 5 мин |
| 5 | Restart ALF (через cron-job) | HERMES | 2 мин + 1 мин ждать |
| 6 | Live-тест через file-queue | HERMES + ALF | 5 мин |
| 7 | Code review patch'а | ALEX (ИИ) | 5 мин (отдельный prompt) |
| 8 | Обновить ALF_FULL.md, SOUL.md | HERMES | 5 мин |
| 9 | Финальный acceptance review | ALEX (ИИ) | 5 мин |
| 10 | Доложить Олегу | HERMES | — |

**Итого: ~50 минут** (с учётом тестов + review).

---

## 6. НУЖНА ЛИ ПОДПИСЬ ОЛЕГА

**Да, перед шагом 4 (patch).** Потому что:
- Меняем production filewatcher (downtime ~30 сек)
- Меняем модель взаимодействия (больше не Hermes Agent CLI для ALF)
- Это хвост 2 в "что Альф знает о себе" — после patch SOUL.md надо обновить

**Скажи Олег:**
- **A.** Применяю план как есть, поехали
- **B.** Сначала хочу обсудить риск #1 (5xx fallback на старый subprocess — оставляем или нет?)
- **C.** Сначала Аликс code review patch'а, потом применяю
- **D.** Другое (что?)

---

**Ledger:** `/root/matryoshka/council/meta-2026-06-24/PLAN-B-alf-direct-nvidia.md`
**ALEX opinion:** `/root/matryoshka/council/meta-2026-06-24/alex-plan-b-opinion.txt`
