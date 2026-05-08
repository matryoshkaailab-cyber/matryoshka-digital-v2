# KIMI K2.6 — УСТАНОВКА АГЕНТА
## Дата: 08.05.2026

---

## 1. ЧТО ТАКОЕ KIMI K2.6

**Kimi K2.6** — флагманская модель Moonshot AI с открытыми весами.

### Характеристики
- **Параметры:** 1 триллион (MoE архитектура)
- **Активные параметры:** 32 миллиарда на инференс
- **Контекст:** 256K токенов
- **SWE-Bench:** 80.2% (сопоставимо с GPT-5.4, Claude Opus 4.6)

### Сильные стороны
- Tool calling — лучший среди open-source моделей
- Multi-step task planning
- Agentic workflows — до 300 параллельных агентов
- Мультиязычность (CJK + English)

---

## 2. ПОДКЛЮЧЕНИЕ ЧЕРЕЗ OPENROUTER

### Конфиг для OpenClaw (openclaw.json)
```json
{
  "provider": "openrouter",
  "model": "moonshot/kimi-k2-6",
  "apiKey": "sk-or-v1-..."
}
```

### Установка OpenClaw
```bash
npm install -g openclaw
npx openclaw start
```

---

## 3. ПОДКЛЮЧЕНИЕ НАПРЯМУЮ ЧЕРЕЗ KIMI API

### Переменные окружения
```bash
export MOONSHOT_BASE_URL="https://api.moonshot.ai/v1"
export MOONSHOT_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

### Python пример
```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxxx",
    base_url="https://api.moonshot.ai/v1"
)

response = client.chat.completions.create(
    model="k2.6",
    messages=[{"role": "user", "content": "Привет"}]
)
```

---

## 4. ДОСТУПНЫЕ ИНСТРУМЕНТЫ KIMI K2.6

| Инструмент | Описание |
|------------|----------|
| web-search | Поиск в интернете |
| code_runner | Выполнение Python кода |
| fetch | Извлечение содержимого URL |
| memory | Хранение контекста |
| excel | Анализ CSV/Excel |

---

## 5. ДЛЯ АГЕНТА КИМ2,6 НА СЕРВЕРЕ

Агент будет работать на Windows ПК с доступом к серверу 85.137.166.209

### SSH
```
ssh root@85.137.166.209
```

### GitHub
```
git@github.com:matryoshkaailab-cyber/matryoshka-digital-v2.git
```

### API ключ
Нужен OpenRouter или Kimi API ключ — спросить у Олега

---

## 6. ВИДЕО ИЗУЧЕНО

https://www.youtube.com/watch?v=9IaS0kin2dI

Рекомендация: использовать OpenClaw + Kimi K2.6 через OpenRouter — быстрая настройка за 5 минут.