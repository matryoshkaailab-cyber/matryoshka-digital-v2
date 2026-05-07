# N8N — Воркфлоу и автоматизация

## Расположение
```
C:\matryoshka\n8n\
├── workflows/          ← JSON файлы воркфлоу
└── Описание воркфлоу.txt
```

## Что自动化руется (примеры)
- Обработка заказов
- Уведомления клиентам
- Интеграция с ЮKassa
- Выдача VPN доступов

## Управление n8n
```bash
# Статус
ssh vpn-serger "systemctl status n8n"

# Логи
ssh vpn-serger "journalctl -u n8n -n 50"

# Рестарт
ssh vpn-serger "systemctl restart n8n"
```

## Переменные окружения
```bash
ssh vpn-serger "cat /opt/n8n/.env"
```

## Важно
- n8n работает как systemd сервис
- Webhook URL: смотреть в `.env`
- База: SQLite или PostgreSQL (зависит от конфига)
