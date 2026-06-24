# MATRYOSHKA Swarm — архитектура роя

**Цель:** HERMES как дирижёр распределяет задачи по агентам роя через файловые очереди.

## Состав роя

| Рой | Агент | Роль | Profile | Telegram |
|---|---|---|---|---|
| ⚪ Белый | HERMES | Дирижёр | hermes-cli | @oleg_industry_bot |
| ⚪ Белый | ALF | Стратег | alf | @IlonAnalyticBot |
| 🔵 Синий | ALEX | Техник | (на ПК) | — |
| 🔴 Красный | ALISA | Маркетинг (отложена) | alisa | @AlisaMatryBot |

**Клиентский кейс (не часть роя):** ALINA (@NikolaAlinaBot, profile=alina, для Николая)

## Структура директорий

```
/root/matryoshka/swarm/
├── inbox/                  ← ВХОДЯЩИЕ задачи (от HERMES к агентам)
│   ├── alex/               ← для ALEX (синхронизируется с ПК через SCP)
│   ├── alf/                ← для ALF
│   ├── alisa/              ← для ALISA
│   └── hermes/             ← для HERMES (ответы агентов)
├── outbox/                 ← ИСХОДЯЩИЕ ответы (от агентов к HERMES)
│   ├── alex/
│   ├── alf/
│   ├── alisa/
│   └── hermes/
└── archive/                ← завершённые задачи (архив)
```

## Формат задачи (inbox)

Файл: `/root/matryoshka/swarm/inbox/<agent>/<task_id>.json`

```json
{
  "task_id": "task_a3f2e1b9",
  "from": "hermes",
  "to": "alex",
  "command": "ssh root@10.8.1.1 'df -h /'",
  "context": "Олег попросил проверить диск VPS",
  "timeout": 300,
  "created_at": "2026-06-17T23:15:00"
}
```

## Формат ответа (outbox)

Файл: `/root/matryoshka/swarm/outbox/<agent>/<task_id>.json`

```json
{
  "task_id": "task_a3f2e1b9",
  "from": "alex",
  "to": "hermes",
  "status": "done",
  "ok": true,
  "output": "/dev/vda1  49G  35G  12G  75%  /",
  "error": "",
  "executed_by": "ALEX",
  "finished_at": "2026-06-17T23:15:18"
}
```

## Жизненный цикл задачи

```
1. Олег пишет HERMES в Telegram
2. HERMES категоризирует задачу (по SOUL.md SWARM PROTOCOL)
3. HERMES пишет /swarm/inbox/<agent>/<task_id>.json
4. Poller агента подхватывает задачу:
   - ALEX: worker на ПК pollingит через SCP
   - ALF: hook в профиле alf проверяет каждые 30 сек
   - ALISA: hook в профиле alisa (отложена)
5. Агент выполняет, пишет /swarm/outbox/<agent>/<task_id>.json
6. HERMES poller (cron-watchdog) забирает ответ из outbox
7. HERMES формирует отчёт Олегу в Telegram
8. Задача архивируется в /swarm/archive/
```

## Команды

### Отправить задачу вручную (HERMES)
```bash
python3 /root/matryoshka/bin/swarm_send.py alex "команда"
python3 /root/matryoshka/bin/swarm_send.py alf "аналитика"
```

### Проверить pending задачи
```bash
ls /root/matryoshka/swarm/inbox/*/
```

### Проверить ответы
```bash
ls /root/matryoshka/swarm/outbox/*/
```

### Архивировать завершённые
```bash
python3 /root/matryoshka/bin/swarm_archive.py
```

## Safety

- Timeout по умолчанию: 300 сек (5 мин)
- Если agent не ответил → HERMES отмечает `timed_out`, пытается сам или сообщает Олегу
- Опасные команды: subagent_auto_approve=false (по умолчанию)
- Профили изолированы: каждый agent = свой profile Hermes, своя память

## Не часть роя

- **ALINA** (@NikolaAlinaBot) — клиентский бот Николая, отдельный кейс
- Олег не должен писать ALINA напрямую для задач роя
