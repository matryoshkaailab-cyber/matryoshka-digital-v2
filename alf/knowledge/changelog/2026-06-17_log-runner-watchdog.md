---
title: "Инфраструктура: log-runner + watchdog + service-manager"
date: 2026-06-17
type: changelog
tags: [infrastructure, log-runner, watchdog, ci, service-manager]
---

# Новая инфраструктура управления сервисами ALEX

## Что сделано (внедрено 17.06.2026)

### 1. Log-runner — единая обёртка запуска процессов
- `scripts/log-runner.js` — запускает любой процесс (python, node, .bat) с detached spawn
- Пишет: `logs/<name>.log` (stdout), `logs/<name>.err.log` (stderr), `logs/<name>.pid`, `logs/<name>.meta.json`
- Защита от дублей: refuse если PID жив, авто-чистка stale pid
- `scripts/kill-service.js` — читает .pid → `taskkill /F /T /PID`
- `scripts/status.js` — таблица: имя, PID, RUNNING/DEAD, uptime, размер лога, команда

### 2. package.json — npm-скрипты для всех сервисов
Сервисы: `acp`, `acp-bridge`, `bridge`, `router`, `relay`, `supervisor`, `stack`, `ws`, `proxy`

Команды:
```bash
npm run status                     # кто жив
npm run start:<name>:log           # запуск с логом+PID
npm run stop:<name>                # остановка по PID
npm run restart:<name>             # stop + start
npm run logs:<name>                # tail лога
npm run check:all                  # status + ci-smoke
```

**Жёсткое правило**: только `stop:<name>`. `taskkill /F /IM python.exe` — запрещено (убивает все python процессы).

### 3. Watchdog — авторестарт упавших сервисов
- `scripts/watchdog.js` + `scripts/watchdog.json`
- Каждые 30с проверяет JSON статус критических сервисов (acp, bridge, router)
- DEAD сервисы автоматически перезапускаются через log-runner API
- >3 падений за 5 минут → отключает авторестарт (защита от бесконечного цикла)
- Некритические (relay, stack) не запускает авто, только перезапускает если упали

```bash
npm run start:watchdog:log    # запустить
npm run stop:watchdog         # остановить
```

### 4. CI-smoke — проверка целостности проекта
- `scripts/ci-smoke.js` — проверяет: package.json, ключевые файлы, .env не в git, npm scripts
- `npm run ci:smoke` — exit 0 если всё ок
- `.github/workflows/smoke.yml` — GitHub Actions при каждом пуше

### 5. Навык service-manager для ALEX
- `.opencode/skills/service-manager/SKILL.md` — пошаговая инструкция:
  1. `npm run status` — диагностика
  2. `Get-Content logs/<name>.err.log -Tail 30` — хвост ошибок
  3. `npm run restart:<name>` — перезапуск
  4. `npm run status` — верификация
- Обновлён `.opencode/commands/fix.md` — теперь использует service-manager

### 6. readme-for-agents.md — новая оперативная сводка
14 разделов: команды, порты, протоколы (ACP, HTTP Bridge), SSH, энв-переменные, hard rules, быстрые шорткаты. Без философии.

### 7. AGENTS.md — рефакторинг
Убраны дублирующиеся технические детали (порты, команды, протоколы). Добавлена ссылка на readme-for-agents.md. Сохранено: ролевая архитектура, цепочка управления, история решений.

## Что не сделано (сознательно)
- Прямая интеграция навыка service-manager в ответ ALEX — это настраивается через `.opencode.json` отдельно
- CI/CD с деплоем на VPS — нет self-hosted runner

## Ссылки
- Исходники: `C:\matryoshka\scripts\log-runner.js`, `C:\matryoshka\scripts\watchdog.js`
- Навык: `.opencode\skills\service-manager\`
- Проектные правила: `AGENTS.md`
- Оперативная сводка: `readme-for-agents.md`
