# Агент: АЛЕКС (@oleg_industry_bot)

**Статус:** Активен
**Тип:** Технический инженер (Windows ПК)
**Платформа:** Windows (рабочая машина Олега)
**Управляется:** HERMES через ws_client → ws_server (:8446/:8450)

---

## Роль и назначение

АЛЕКС — это Windows ПК Олега с запущенным ws_client. Не бот, а рабочая станция.
- ws_client подключается к VPS HERMES
- HERMES отправляет команды через ws_server
- Алекс выполняет код и возвращает результат

---

## Архитектура подключения

```
HERMES (VPS Linux :8446/:8450)
       ↑ ws_server (token: hermes-ws-secret-2026)
       │
       └─ ws_client (Алекс, Windows ПК)
              ↓
          opencode serve :4096
          ws_server :8446
          @oleg_industry_bot
```

---

## Конфигурация

### ws_server (HERMES VPS)
- Port: 8446 (incoming от Алекс)
- Port: 8450 (CLI connection)
- Token: hermes-ws-secret-2026

### ws_client (Алекс Windows)
- ws://127.0.0.1:8446
- HTTP API: http://127.0.0.1:8450
- Токен: hermes-ws-secret-2026

### Windows пути
```
C:\matryoshka\bots\alex\
├── config/
├── logs/
├── memory/
├── projects/
│   └── nikolay-alina-briefing.md
└── tasks/
```

---

## Проекты Алекс

### nikolay-alina-briefing.md
- Путь: /root/matryoshka/bots/alex/projects/nikolay-alina-briefing.md
- Дата: 21.05.2026
- Статус: Актуальные вводные по проекту Nikolay + Алина

---

## Взаимодействие с HERMES

### Проверка связи
```bash
/root/check_alex.sh
```

### Лог ws_server
```
/var/log/hermes_ws.log (PID 1605544)
```

### Команда перезапуска ws_client на Алекс
(выполняется Олегом вручную на Windows)

---

## Ограничения

- Работает ТОЛЬКО когда Алекс запущен на Windows
- ws_server иногда не отвечает (нужно проверять)
- Не является ботом — это ws_client

---

## TODO

- [ ] Создать real-time мониторинг доступности Алекс
- [ ] Автоматизировать проверку ws_client connection

---

## Изменения (лог)

### 25.05.2026
- Создан /root/matryoshka/agents/alex/README.md
- Добавлена связь: ws_client → VPS (:8446/:8450)
- Добавлен nikolay-alina-briefing.md в проекты