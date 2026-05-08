# KIMI K2.6 — ПОЛНОЕ ИССЛЕДОВАНИЕ
## Источник: youtube.com/watch?v=9IaS0kin2dI + docs
## Дата: 08.05.2026

---

## 1. ЧТО ТАКОЕ KIMI K2.6

**Kimi K2.6** — флагманская open-source модель от Moonshot AI, оптимизированная для agentic workflows.

### Характеристики
- **Архитектура:** Mixture-of-Experts (MoE)
- **Параметры:** 1 триллион всего / 32 миллиарда активируются на инференс
- **Контекст:** 256K токенов
- **Benchmarks:**
  - SWE-Bench: 80.2%
  - Humanity's Last Exam: LIDER
  - DeepSearchQA: LIDER
  - SWE-Bench Pro: LIDER
- **Улучшение кода:** +20% vs K2.5
- **Среднее количество шагов на задачу:** -35%

### Стоимость
- **1/8 от Claude Opus 4.6** для agent workloads

---

## 2. КЛЮЧЕВЫЕ ВОЗМОЖНОСТИ

### AgentSwarm (до 300 агентов)
Координатор-агент запускает десятки специализированных subagents работающих параллельно.

### Tool Calling
- web-search — поиск в интернете
- code_runner — выполнение Python
- fetch —提取 URL контент
- memory — хранение контекста
- excel — анализ данных

### Самостоятельность
K2.6 **сам решает** когда использовать инструменты. Не нужно указывать в промпте какие инструменты использовать.

---

## 3. СОВМЕСТИМЫЕ SHELLS (от Kimi Team)

Kimi официально рекомендует:
1. **OpenClaw** — быстрая настройка, легкие агенты
2. **Hermes Agent** — полноценный workspace

Также поддерживает:
- Claude Code
- OpenCode

---

## 4. ПОДКЛЮЧЕНИЕ

### Вариант A: AtlasCloud (рекомендуемый)
```bash
# API Endpoint
https://api.atlascloud.ai/v1

# Model ID
moonshot/kimi-k2.6
```

### Вариант B: Kimi Direct
```bash
# Base URL
https://api.moonshot.ai/v1

# API Key
sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 5. НАСТРОЙКА OPENCLAW

### Конфиг: ~/.openclaw/openclaw.json

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "custom-api-atlascloud-ai/moonshot/kimi-k2.6"
      }
    }
  },
  "models": {
    "providers": {
      "custom-api-atlascloud-ai": {
        "baseUrl": "https://api.atlascloud.ai/v1",
        "api": "openai-completions",
        "apiKey": "apikey-xxx",
        "models": [
          {
            "id": "moonshot/kimi-k2.6",
            "name": "Kimi K2.6",
            "api": "openai-completions"
          }
        ]
      }
    }
  }
}
```

### Запуск:
```bash
# Terminal 1
openclaw gateway

# Terminal 2
openclaw tui
```

---

## 6. НАСТРОЙКА HERMES AGENT

```bash
hermes setup
```

**Ввод:**
1. Provider: `custom`
2. Base URL: `https://api.atlascloud.ai/v1`
3. API Key: `apikey-xxx`
4. Model ID: `moonshot/kimi-k2.6`

⚠️ ВАЖНО: Включить `moonshot/` префикс. Без него — 404.

---

## 7. НАСТРОЙКА OPENCODE

**Файл:** ~/.config/opencode/config.json

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "atlascloud": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "AtlasCloud",
      "options": {
        "baseURL": "https://api.atlascloud.ai/v1",
        "apiKey": "apikey-xxx"
      },
      "models": {
        "moonshot/kimi-k2.6": { "name": "Kimi K2.6" }
      }
    }
  },
  "model": "atlascloud/moonshot/kimi-k2.6"
}
```

⚠️ Использовать `@ai-sdk/openai-compatible` провайдер — стандартный openai провайдер обрезает префикс.

---

## 8. РЕЗУЛЬТАТЫ ТЕСТОВ

### Тест: "Research the web for the latest AI news today"

**Результат:**
- ✅ Быстрый ответ
- ✅ 3 свежие новости
- ✅ Чистое изложение
- ✅ Без "Based on my research..." болтовни
- ✅ Просто новости

### Тест: "Check what happened today in AI automation"

- ✅ Взял web tool
- ✅ Использовал правильно
- ✅ Дал актуальную информацию

---

## 9. STABILITY TEST

**Тест:** 23 агента одновременно, 26 сессий

**Результат:** Ноль ошибок 429 (rate limit)

> "Стабильность — главное. Не 'может ли модель хорошо ответить?', а 'может ли она отвечать хорошо — при десятках параллельных задач — без поломки системы?'"

---

## 10. ДЛЯ АГЕНТА КИМ2,6

### Что нужно:
1. **API ключ** — AtlasCloud или Kimi
2. **Shell** — OpenClaw или Hermes

### Быстрый старт:
```bash
# Установка OpenClaw
npm install -g openclaw

# Запуск
openclaw gateway  # Terminal 1
openclaw tui     # Terminal 2

# Конфиг
openclaw configure
```

---

## 11. ВИДЕО SUMMARY

Видео **Kimi K2.6 + OpenClaw - Two AI Agents Build a Full App Together**

Демонстрирует:
- Два Kimi K2.6 агента работающих одновременно через OpenClaw
- Один как архитектор, один как исполнитель
- Результат: готовое full-stack приложение

**Ключевая мысль:** K2.6 создан для agentic workflows — не для болтовни, а для действий.

---

## 12. ВЫВОДЫ

| Критерий | Оценка |
|----------|--------|
| Tool Calling | ⭐⭐⭐⭐⭐ |
| Code Generation | ⭐⭐⭐⭐⭐ |
| Agent Swarm | ⭐⭐⭐⭐⭐ |
| Stability | ⭐⭐⭐⭐⭐ |
| Цена | ⭐⭐⭐⭐⭐ |
| Скорость | ⭐⭐⭐ (медленнее Gemma 4) |

**Идеальный use case:**
- Много параллельных агентов
- Сложные многошаговые задачи
- Research и аналитика
- Генерация кода

**NOT для:**
- Простые быстрые вопросы (Gemma 4 быстрее)
- Локальный безлимитный ран (Gemma 4 локально)