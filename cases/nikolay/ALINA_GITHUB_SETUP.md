# 🔧 ИНСТРУКЦИЯ: Алина + Личный GitHub Николая

> **Для кого:** Николай (клиент ALINA)  
> **Когда:** Передашь Олегу → он передаст Алине  
> **Цель:** Алина получает СВОЙ GitHub аккаунт, отвязывается от MATRYOSHKA, работает на полную  
> **Время:** ~10 минут (один раз)

---

## 🎯 ЗАЧЕМ ЭТО НУЖНО

Сейчас Алина работает в "общем проекте" MATRYOSHKA (org `matryoshkaailab-cyber`).  
Нужно: **у Алины свой личный GitHub, свой репозиторий, своя жизнь**.

Что это даёт:
- 🔒 **Изоляция** — данные Алины не в общем репо MATRYOSHKA
- 💾 **Backup** — Алина сама сохраняет свой код, знания, историю
- 🐛 **Issues** — Алина сама создаёт задачи и баг-трекинг
- 📋 **Projects** — канбан-доска для задач Алины
- 📚 **Wiki** — документация, которую Алина ведёт сама
- 🚀 **Releases** — версионирование (Алина v1.0, v2.0, ...)
- ⚡ **Actions** — автоматизация (тесты, деплой)
- 🔔 **Webhooks** — уведомления о событиях

---

## 📋 ЧАСТЬ 1. Что делает Николай (10 минут)

### Шаг 1. Создать ЛИЧНЫЙ GitHub аккаунт

> ⚠️ **ВАЖНО: это должен быть ЛИЧНЫЙ аккаунт Николая, не MATRYOSHKA/org.**

1. Открой https://github.com/signup
2. Введи **свой личный email** (не корпоративный MATRYOSHKA)
3. Username — выбери что-то понятное (например: `nikolay-alina`, `nikolay-petrov`)
4. Пароль
5. Подтверди email

Запиши **свой GitHub username** — он понадобится.

### Шаг 2. Создать Personal Access Token (PAT)

1. Зайди в GitHub → кликни аватар (правый верх) → **Settings**
2. Внизу слева → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. **Generate new token** → **Generate new token (classic)**
5. Заполни:

| Поле | Что ввести |
|------|-----------|
| Note | `alina-bot-token` |
| Expiration | `No expiration` (или 90 дней — потом обновишь) |
| ✅ `repo` | **Обязательно** — полный доступ к репозиториям |
| ✅ `workflow` | Для автозапуска Actions |
| ✅ `write:packages` | Публикация пакетов |
| ✅ `admin:repo_hook` | Webhooks (Алина будет ставить) |
| ✅ `delete_repo` | Если захочешь удалить репо |
| ✅ `project` | Projects (канбан) |
| ✅ `write:discussion` | Discussions (обсуждения) |

6. **Generate token** (внизу страницы)
7. ⚠️ **СКОПИРУЙ ТОКЕН СРАЗУ** — он покажется ОДИН раз!
   - Вид: `ghp_xx...xxxx` (~40 символов)
   - Сохрани в надёжное место

### Шаг 3. Передать токен Алине

Открой Telegram → найди бота Алины.

Напиши ей ровно эту команду (подставив свой токен):

```
/set_github_token ghp_вставь_сюда_свой_токен
```

**Пример:**
```
/set_github_token ghp_aBcD1234XyZ5678...
```

Ожидаемый ответ Алины:
- ✅ "GitHub подключен. Username: nikolay-alina"
- ❌ Если "неверный токен" — проверь что скопировал полностью (начинается с `ghp_`)

---

## ⚙️ ЧАСТЬ 2. Что Алина сделает сама (после получения токена)

Алина автоматически настроит GitHub **по максимуму**. Вот что она сделает:

### Шаг A1. Безопасное хранение токена

```
Запишет токен в /root/.hermes/profiles/alina-prod/.env:
  GITHUB_TOKEN_NIKOLAY=<твой токен>
  GITHUB_USER_NIKOLAY=<твой username>

Добавит в .gitignore чтобы случайно не запушить токен:
  .env
  **/secrets/**
  **/*.key
  **/*.pem
```

### Шаг A2. Создание своего репозитория

```
Создаст на твоём GitHub приватный репозиторий:
  github.com/<твой-username>/alina-personal

Описание: "ALINA — AI assistant for Nikolay (isolated from MATRYOSHKA)"

Структура:
  alina-personal/
  ├── README.md              ← Алина сама напишет
  ├── knowledge/             ← её база знаний
  │   ├── user-preferences.md
  │   ├── daily-context.md
  │   └── learnings.md
  ├── workflows/             ← автоматизация
  │   ├── daily-backup.yml
  │   ├── health-check.yml
  │   └── weekly-report.yml
  ├── issues/                ← шаблоны для багов и задач
  │   ├── bug-template.md
  │   └── feature-template.md
  ├── releases/              ← версии Алины
  │   └── CHANGELOG.md
  └── docs/                  ← документация
      ├── architecture.md
      └── commands.md
```

### Шаг A3. Настройка GitHub Projects (канбан)

```
Создаст Project board: "ALINA Tasks"

Колонки:
  📥 Backlog    — задачи, которые Алина планирует
  🔄 In Progress — Алина сейчас делает
  👀 Review     — задачи на проверке
  ✅ Done       — выполненные

Каждая задача Алины = Issue с label + assign на доску
```

### Шаг A4. Настройка Issues (баг-трекинг)

```
Включит:
  ✅ Bug reports template
  ✅ Feature request template
  ✅ User story template
  ✅ Custom labels:
      🐛 bug
      ✨ enhancement
      📚 documentation
      🔧 maintenance
      💡 idea
      🚀 priority-high
```

### Шаг A5. Auto-backup через GitHub Actions

Создаст workflows:

**`.github/workflows/daily-backup.yml`** — каждый день в 03:00:
```yaml
name: Daily Backup
on:
  schedule: - cron: '0 3 * * *'
jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Commit daily snapshot
        run: |
          git config user.name "ALINA Bot"
          git config user.email "alina-bot@nikolay.local"
          git add .
          git commit -m "📸 Daily backup $(date +%Y-%m-%d)"
          git push
```

**`.github/workflows/health-check.yml`** — каждые 6 часов:
- Пингует Алину
- Если не отвечает — создаёт Issue с label `🚨 down`

### Шаг A6. Webhooks (уведомления)

```
Алина настроит webhooks:
  - Push → уведомление в Telegram Николаю
  - Issue created → уведомление в Telegram
  - Release published → обновление в Obsidian
  - Action failed → алерт в Telegram
```

### Шаг A7. Wiki (документация)

```
Создаст Wiki страницы:
  📖 Home — что умеет Алина
  📖 Commands — все Telegram-команды
  📖 Architecture — как Алина устроена
  📖 Troubleshooting — частые проблемы
  📖 Changelog — история версий
```

### Шаг A8. Releases (версии)

```
Первая версия: v1.0.0 "Genesis"
  - Подключение к GitHub
  - Создание репозитория
  - Настройка Projects/Issues/Actions
  - Auto-backup
  - Webhooks

Будут версии: v1.1.0, v1.2.0, ... — при каждом крупном изменении
```

---

## 🚀 ЧАСТЬ 3. Как Алина будет использовать GitHub МАКСИМАЛЬНО

После настройки Алина **каждый день** будет:

| Действие | Когда | Что даёт |
|----------|-------|----------|
| Push знаний | После каждого обновления knowledge/ | Backup + история |
| Создавать Issue | При обнаружении бага | Баг-трекинг |
| Закрывать Issue | При исправлении | История фиксов |
| Создавать Release | При крупном изменении | Версионирование |
| Обновлять Wiki | При новых командах | Документация |
| Запускать Actions | По расписанию (cron) | Backup, health-check |
| Создавать Projects | Для сложных задач | Канбан |
| Реагировать на Webhooks | При push от других | Уведомления |

**Через 1 месяц** у тебя будет:
- ~30 backup коммитов
- ~10 закрытых issues
- 2-3 релиза
- Полная Wiki
- Работающие Actions

---

## ✅ ЧАСТЬ 4. Проверка что всё работает

### Проверка 1: Спросить Алину
```
/github_status
```
Ожидаемый ответ:
```
✅ GitHub: подключен (username: nikolay-alina)
✅ Репозиторий: github.com/nikolay-alina/alina-personal
✅ Последний push: 2026-06-18 03:00 (auto-backup)
✅ Issues: 0 открытых, 0 закрытых
✅ Projects: 1 board (ALINA Tasks)
✅ Actions: 3 workflow (daily-backup, health-check, weekly-report)
✅ Webhooks: 4 активных
✅ Releases: 1 (v1.0.0 Genesis)
```

### Проверка 2: Зайти в GitHub
1. Открой https://github.com/твой-username/alina-personal
2. Должно быть всё: код, README, workflows, issues templates
3. Кликни **Actions** — должен быть хотя бы один успешный запуск
4. Кликни **Projects** — должен быть board "ALINA Tasks"

### Проверка 3: Проверить что токен работает
1. https://github.com/settings/tokens
2. В списке должен быть `alina-bot-token`
3. В строке должна быть пометка "Last used recently"

---

## 🆘 ЧАСТЬ 5. Если что-то сломалось

| Проблема | Что делать |
|----------|-----------|
| Алина: "неверный токен" | Перепроверь что скопировал токен целиком (начинается с `ghp_`) |
| Алина молчит | Зайди в Telegram → `/start` для перезапуска бота |
| Токен протух (Expiration) | Создай новый токен (Шаг 2 заново), передай через `/set_github_token` |
| Push не проходит (403) | Скорее всего токен потерял scope `repo`. Создай новый (Шаг 2) |
| Не помню username | Зайди https://github.com → правый верх → твой аватар → URL содержит username |
| Алина не использует GitHub | Скажи ей `/github_setup` — она пересоздаст всё с нуля |
| Хочу всё сбросить | Скажи `/github_reset` — Алина удалит репо и начнёт заново |

**Если ничего не помогает — пиши Олегу (HERMES), он починит.**

---

## 🔒 ЧАСТЬ 6. Безопасность

### ⚠️ НИКОГДА:
- Не отправляй токен в обычном чате (только через `/set_github_token`)
- Не показывай токен другим людям
- Не коммить токен в публичный репозиторий
- Не давай токен другим ботам/скриптам

### ✅ МОЖНО:
- Создать токен с expiration (например, 90 дней) — потом обновить
- В любой момент отозвать токен: https://github.com/settings/tokens → Delete
- Создать отдельный токен для Алины (не использовать свой основной)

### 🔄 Рекомендация по обновлению токена:
- Каждые **90 дней** создавай новый токен
- Старый удаляй после того как Алина перешла на новый
- Алина будет напоминать за 7 дней до истечения

---

## 📞 ШПАРГАЛКА

```
┌─────────────────────────────────────────────────────┐
│  1. https://github.com/signup — создать аккаунт     │
│  2. https://github.com/settings/tokens             │
│     → Generate new token (classic)                 │
│     → Scopes: repo, workflow, project,             │
│       admin:repo_hook, delete_repo,                │
│       write:packages, write:discussion             │
│  3. Скопировать токен (ghp_...)                    │
│  4. Алине: /set_github_token ghp_...               │
│  5. Проверить: /github_status                      │
└─────────────────────────────────────────────────────┘
```

**Всё. Алина сделает остальное автоматически.**

---

## 📎 Технические детали для Олега (не передавать Николаю)

### Как Алина хранит токен:
```
/root/.hermes/profiles/alina-prod/.env:
  GITHUB_TOKEN_NIKOLAY=ghp_...
  GITHUB_USER_NIKOLAY=nikolay-alina
```

### Как Алина делает push:
```python
import subprocess
result = subprocess.run(
    ["gh", "repo", "view", f"{user}/alina-personal"],
    env={"GITHUB_TOKEN": token, "PATH": "/usr/local/bin:/usr/bin"},
    capture_output=True, text=True
)
```

### Как Алина создаёт Issues:
```python
gh issue create \
  --repo nikolay-alina/alina-personal \
  --title "Bug: ..." \
  --body "..." \
  --label "bug,priority-high"
```

### Cron для auto-backup:
```cron
0 3 * * * cd /root/alina-personal && git add -A && git commit -m "📸 auto-backup" && git push
```

### Webhook URLs:
- Telegram: POST на `https://api.telegram.org/bot<TOKEN>/sendMessage`
- Obsidian: PUT на `https://85.137.166.209:8181/<path>` (если настроен)

---

*Создано: 2026-06-18 17:30 Олегом через HERMES*  
*Файл: `/root/matryoshka/cases/nikolay/ALINA_GITHUB_SETUP.md`*
