# OPEN DESIGN — ПОЛНЫЙ ГАЙД ДЛЯ АЛЕКСА

## ЧТО ЭТО

Open Design — локальный аналог Claude Design. Генерирует HTML/CSS/JS прототипы через AI агентов.

**URL:** http://85.137.166.209:3000
**Агент:** Claude Code 2.1.119 (локально)
**Альтернатива:** Hermes Agent v0.13

---

## ИНТЕРФЕЙС

### ВЕРХНЯЯ ПАНЕЛЬ
- Логотип "Open Design"
- Ссылки: Designs / Examples / Design systems / Image templates
- Вкладки: Prototype / Live artifact / Slide deck / From template
- Кнопка Settings (шестерёнка)
- Индикатор "Saving..."

### ЛЕВАЯ ПАНЕЛЬ — СОЗДАНИЕ ПРОЕКТА

#### New Prototype
1. **Project name** — название проекта
2. **Design system** — какой дизайн-системой пользоваться:
   - Neutral Modern (default)
   - Stripe
   - Minimal
   - Linear
   - Vercel
   - и 120+ других
3. **Fidelity** — качество:
   - Wireframe (быстро, черновик)
   - High fidelity (полноценный дизайн)
4. **"+ Create"** — создать проект (ГЛАВНАЯ КНОПКА)

#### Под полем Create:
- "Import Claude Design ZIP" — импорт проекта
- Путь к папке проекта
- "Open folder" — открыть папку
- "Only you can see your project by default"

#### Нижняя часть:
- "Adopt a pet" — питомец-помощник
- Agent info: "Local CLI Claude Code - 2.1.119"

### ПРАВАЯ ПАНЕЛЬ — SETTINGS

#### Media providers (КЛЮЧЕВОЕ!)
| Провайдер | Назначение | API Endpoint |
|------------|-------------|---------------|
| FishAudio | TTS / voice clone | https://api.fish.audio |
| MiniMax | TTS / video-01 | https://api.minimaxi.chat/v1 |
| Nano Banana | Google Gemini images | https://generativelanguage.googleapis.com |
| OpenAI | gpt-image-2 / dall-e-3 | https://api.openai.com/v1 |
| Stub | Заглушка | - |

**Статус:** Все показывают "Integrated" = настроены

#### Configure execution mode
- **Local CLI / BYOK** — использует локального агента (Claude Code)
- Можно переключить на облако

#### Agents (КОГО ВЫБРАТЬ)
| Агент | Доступен | Модель |
|-------|----------|--------|
| Claude Code | ✅ | Sonnet/Opus/Haiku |
| Hermes | ✅ | MiniMax-M2.7 (ЭТО МЫ!) |
| Gemini CLI | ✅ | gemini-2.5-pro/flash |
| OpenCode | ❌ | - |
| Kimi CLI | ❌ | - |

**ДЛЯ НАШЕЙ СВЯЗКИ:** Выбрать **Hermes** чтобы HERMES управлял!

#### Connectors
- GitHub
- и др.

#### Orbit
- Daily connector summary

#### MCP server
- Expose Open Design as MCP server — можно подключить внешние инструменты

#### External MCP
- GitHub
- Higgsfield
- и др.

#### Language
- English / другие языки

#### Appearance
- Light / Dark / System

---

## DESIGN SYSTEMS (120+)

Категории:
- **AI & LLM:** claude, cohere, mistral-ai, replicate, elevenlabs
- **Developer Tools:** cursor, vercel, linear-app, framer, supabase, posthog
- **Productivity:** notion, figma, miro, airtable, intercom
- **Fintech:** stripe, coinbase, binance, kraken, revolut
- **E-Commerce:** shopify, airbnb, uber, nike, starbucks
- **Automotive:** tesla, bmw, ferrari, lamborghini

**Для DATALINK PRO:** stripe, minimal, linear-app

---

## КАК СОЗДАТЬ ПРОЕКТ

1. Открыть http://85.137.166.209:3000
2. Ввести название (например "DATALINK Landing")
3. Выбрать Design system (например "stripe")
4. Выбрать Fidelity (High fidelity)
5. Нажать **"+ Create"**
6. В появившемся чате написать промт:
   ```
   Design a VPN service landing page with dark navy theme (#0a1628) and gold accents (#c9a227). Hero section with shield icon. Features: protection, speed, global network. Pricing: $9.99/mo, $24.99/3mo, $59.99/12mo. Download buttons for iOS, Android, Windows, macOS.
   ```
7. Claude Code/Hermes сгенерирует HTML
8. Результат появится в правой части экрана
9. Можно экспортировать / скачать

---

## SKILLS (ЧТО УМЕЕТ)

### Prototype Mode
- web-prototype — веб-прототипы
- saas-landing — SaaS лендинги
- dashboard — дашборды
- pricing-page — страницы цен
- mobile-app — мобильные приложения
- и 20+ других

### Deck Mode
- guizang-ppt — презентации
- simple-deck — минимальные презентации

---

## ЭКСПОРТ

После генерации можно:
- Preview — посмотреть
- Download — скачать HTML/CSS
- Copy code — скопировать код
- Export to PDF/PPTX/MP4

---

## АРХИТЕКТУРА

```
Браузер (Next.js :3000)
    ↓ API
Daemon (Express + SQLite)
    ↓
Local agents (Claude Code / Hermes / etc)
    ↓
Internet (для генерации изображений)
```

Daemon запущен на VPS, браузер подключается к нему.

---

## TROUBLESHOOTING

### "Agent not available"
- Агент не установлен локально
- Установить: `npm install -g @open-designer/agent-name`

### "Media provider not configured"
- Зайти в Settings → Media providers
- Вставить API ключ
- Нажать "Save"

### Проект не создаётся
- Проверить что название введено
- Проверить что выбран Design system
- Обновить страницу

### Пустой экран после Create
- Подождать 10-30 секунд
- Проверить консоль браузера (F12)
- Перезапустить daemon: `cd /root/open-design && docker compose restart`

---

## КАК МЫ БУДЕМ РАБОТАТЬ

### СХЕМА:
```
ОЛЕГ (задача в Telegram)
    ↓
HERMES (анализ, промт)
    ↓
OPEN DESIGN (Алекс или Hermes агент)
    ↓
Результат в /root/matryoshka/results/
    ↓
HERMES → ОЛЕГ (результат)
```

### ЗАДАЧИ ДЛЯ АЛЕКСА:
1. Изучить весь интерфейс
2. Протестировать создание проекта
3. Попробовать разные Design Systems
4. Настроить связку Hermes (когда понадобится)
5. Экспортировать результаты

---

## КОНТАКТЫ

**Hermes (HERMES):** Я управляю через Telegram
**Open Design:** http://85.137.166.209:3000
**Daemon:** работает на VPS

---

## СЛЕДУЮЩИЕ ШАГИ ДЛЯ АЛЕКСА

1. ✅ Открыть http://85.137.166.209:3000
2. ✅ Понять интерфейс (этот гайд)
3. ⬜ Создать тестовый проект "Test Landing"
4. ⬜ Попробовать промт: "Simple landing page with hero and pricing"
5. ⬜ Сохранить результат
6. ⬜ Доложить Олегу что всё работает

---

**Гайд подготовлен HERMES для АЛЕКСА**
*MATROSHKA DIGITAL — ANVAJENS PROTOCOL*