# OPEN DESIGN — ПОЛНЫЙ АНАЛИЗ
## Дата: 08.05.2026 | Источник: youtube.com/watch?v=lgwFdKAyaMM

---

## 1. ЧТО ЭТО

**Open Design** — локальный, open-source аналог Claude Design от Anthropic.
- GitHub: `nexu-io/open-design`
- Stars: **32.8k** (за 6 дней!)
- License: Apache-2.0
- Version: 0.5.0 (07.05.2026)

**Главная фишка:** Не привязан к конкретному агенту. Поддерживает 16+ AI агентов.

---

## 2. КЛЮЧЕВЫЕ ВОЗМОЖНОСТИ

### AI Агенты (16 штук):
```
✅ Claude Code
✅ Codex CLI
✅ OpenCode ← ИСПОЛЬЗУЕТ КИМ2,6!
✅ Gemini CLI
✅ Cursor Agent
✅ Hermes ← МОЙ!
✅ Kimi CLI
✅ Qwen Code
✅ Devin
✅ GitHub Copilot
✅ DeepSeek TUI
✅ Mistral Vibe
✅ Kiro, Kilo, Pi
```

### Навыки (Skills) — 31 штука:
**Прототипы:**
- `web-prototype` — веб-сайты
- `saas-landing` — лендинги SaaS
- `dashboard` — дашборды
- `mobile-app` — мобильные приложения
- `pricing-page` — страницы цен
- `blog-post` — блоги
- `email-marketing` — email рассылки
- `social-carousel` — соцсети
- `magazine-poster` — постеры

**Deck Mode (презентации):**
- `guizang-ppt` — журнальный стиль PPT (по умолчанию)
- `simple-deck` — минимальный deck
- `replit-deck` — product walkthrough
- `weekly-update` — еженедельные обновления

### Дизайн-системы (72+):
```
Airbnb, Stripe, Spotify, Tesla, Figma, Notion,
Linear, Vercel, Shopify, Uber, Nike, и другие
```

### Форматы экспорта:
HTML · PDF · PPTX · MP4 · ZIP · Markdown

---

## 3. ИНТЕГРАЦИЯ С HERMES

### Мой текущий статус:
- Hermes уже в списке поддерживаемых агентов!
- Формат: `acp-json-rpc` через `hermes acp`
- Работает из коробки — НИЧЕГО делать не нужно

### Как это работает:
```
HERMES → Open Design → AI Agent → Artifact → Preview
```

### Схема интеграции:
```
ОЛЕГ
  ↓
HERMES (MiniMax) ← Дирижёр
  ↓
Open Design (design tool) ← Подключаем Kimi K2.6 как агента
  ↓
КИМ2,6 (Kimi CLI / OpenCode) ← Генерирует дизайн
```

---

## 4. КАК ЗАПУСТИТЬ

### Вариант 1: Docker (рекомендуется)
```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design
docker compose up -d
# Открыть http://localhost:7456
```

### Вариант 2: Локально (нужен Node 24)
```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design
corepack enable
pnpm install
pnpm tools-dev
```

---

## 5. НАСТРОЙКА ДЛЯ НАШЕГО СЕРВЕРА

### Подключить Kimi CLI как агент:
1. Установить Kimi CLI на ПК Ким2,6
2. Open Design автоматически найдёт `kimi` в PATH
3. Выбрать "Kimi CLI" в настройках Open Design

### Подключить Hermes:
```bash
# Hermes автоматически определяется
# Выбрать "Hermes" в настройках Open Design
```

---

## 6. ДЛЯ КИМ2,6 — ИНСТРУКЦИЯ

### Шаг 1: Установить Open Design
```bash
# На ПК Ким2,6:
git clone https://github.com/nexu-io/open-design.git
cd open-design
docker compose up -d
```

### Шаг 2: Подключить Kimi CLI
```bash
# Проверить что Kimi CLI установлен
kimi --version
```

### Шаг 3: Использовать
```
1. Открыть http://localhost:7456
2. Выбрать Kimi CLI как агента
3. Выбрать design system (например, Stripe или Airbnb)
4. Написать промт: "Design a VPN service landing page"
5. Kimi генерирует дизайн
```

---

## 7. НАШИ ВОЗМОЖНОСТИ С OPEN DESIGN

### Что можем создавать:
1. **Лендинги** — для DATALINK PRO, MATRYOSHKA DIGITAL
2. **Дашборды** — аналитика, мониторинг
3. **Мобильные прототипы** — приложения
4. **Презентации** — для клиентов, инвесторов
5. **Email маркетинг** — рассылки
6. **Социальные креативы** — посты, карусели

### Интеграция с нашей системой:
```
HERMES → создаёт задачу в Kanban
         ↓
КИМ2,6 → использует Open Design
         ↓ генерирует дизайн
         ↓ сохраняет в /root/matryoshka/results/
         ↓
HERMES → проверяет и передаёт Олегу
```

---

## 8. ВОЗМОЖНОСТЬ ИНТЕГРАЦИИ С HERMES

Hermes уже поддерживается! Но для полной интеграции нужно:

### Вариант A: Hermes + Open Design на разных машинах
```
HERMES (сервер) ← координирует
        ↓ задачи в GitHub
КИМ2,6 (ПК) ← Open Design + Kimi CLI
        ↓ результаты
HERMES (сервер) ← проверяет
```

### Вариант B: Hermes запускает Open Design
```bash
# На сервере:
cd /root/matryoshka
git clone https://github.com/nexu-io/open-design.git
cd open-design
docker compose up -d
# Открыть http://85.137.166.209:7456
```

---

## 9. РЕКОМЕНДАЦИЯ

**Для нашей команды:**

1. **Ким2,6** использует Open Design локально на своём ПК
2. Я (Hermes) координирую через Kanban + GitHub
3. Результаты сохраняем в `/root/matryoshka/results/`

**Выгоды:**
- Дизайны генерирует Kimi K2.6 (80.2% SWE-Bench — лучший кодер)
- Open Design — бесплатный, open-source
- Hermes уже поддерживается
- Можно создавать профессиональные дизайны без дизайнера

---

## 10. КОМАНДЫ ДЛЯ ЗАПУСКА

```bash
# На сервере (опционально)
cd /root/matryoshka
git clone https://github.com/nexu-io/open-design.git
cd open-design
docker compose up -d

# Или локально на ПК Ким2,6
git clone https://github.com/nexu-io/open-design.git
cd open-design
docker compose up -d
# Открыть http://localhost:7456
```

---

## ФАЙЛЫ ПРОЕКТА

- Репозиторий: https://github.com/nexu-io/open-design
- Сайт: https://open-design.ai
- Документация: https://github.com/nexu-io/open-design/blob/main/QUICKSTART.md