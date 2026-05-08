# КООРДИНАЦИЯ HERMES → КИМ2,6
## Дата: 08.05.2026

---

## СХЕМА РАБОТЫ

```
ОЛЕГ
  ↓
HERMES (MiniMax M2.7) ← Дирижёр
  ↓ создаёт задачи (push в GitHub)
КИМ2,6 (OpenCode, Kimi K2.6) ← Инженер
  ↓ результаты (push в GitHub)
HERMES ← проверяет, контролирует
```

---

## СТРУКТУРА ПАПОК

```
/root/matryoshka/
├── tasks/          ← сюда я пишу задачи для агента
├── results/        ← сюда агент пишет результаты
├── scripts/        ← вспомогательные скрипты
└── agents/
    └── kim26/       ← данные для Kim2,6
```

---

## ПРОЦЕСС РАБОТЫ

### 1. Я создаю задачу:
```bash
# Пишу задачу
cat > /root/matryoshka/tasks/task_001.md << 'EOF'
# ЗАДАЧА: Установить AmneziaWG
# Приоритет: HIGH
# Дедлайн: сегодня
# Данные: сервер 85.137.166.209, пароль R5t6y7u8i9o0
EOF
# Push в GitHub
git add . && git commit -m "Task for Kim2,6" && git push
```

### 2. Агент делает:
```bash
git pull
# Читает task_001.md
# Делает работу
# Пишет результат в results/result_001.md
git push
```

### 3. Я проверяю:
```bash
git pull
cat /root/matryoshka/results/result_001.md
```

---

## КАНАЛЫ СВЯЗИ

1. **GitHub** — основной (push/pull)
2. **Telegram** — срочные задачи
3. **Kanban** — статус задач

---

## ПЕРВЫЕ ЗАДАЧИ ДЛЯ КИМ2,6

1. Прочитать `/root/matryoshka/cases/datalink-pro/docs/AGENT_HANDOVER_FULL.md`
2. Установить AmneziaWG на сервер (для решения проблемы с мобильным VPN)
3. Настроить синхронизацию с GitHub

---

## КОНТАКТЫ

- **HERMES** — @oleg_industry_bot (Telegram)
- **ОЛЕГ** — @oleglab22 (директор)
- **КИМ2,6** — OpenCode на ПК