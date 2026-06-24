# n8n WORKFLOW — DATALINK VPN
## MATROSHKA DIGITAL

**Статус:** 📋 ПЛАНИРОВАНИЕ
**Обновлено:** 26.05.2026

---

## ЦЕЛЬ

Автоматизация продаж VPN через Telegram бот:
1. Клиент оплачивает через YooKassa
2. Бот получает webhook
3. Активирует VPN доступ
4. Отправляет конфиг клиенту

---

## АРХИТЕКТУРА

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Telegram    │     │ n8n          │     │ VPS         │
│ @datalink_  │────▶│ (Cloud или  │────▶│ x-ui        │
│ pro_bot     │     │  Self-hosted)│     │ (VLESS)    │
└─────────────┘     └──────────────┘     └─────────────┘
       ▲                  │
       │                  ▼
       │            ┌──────────────┐
       │            │ YooKassa     │
       │            │ Webhook      │◀── Оплата
       │            └──────────────┘
       │
       ▼ (уведомление)
  ┌─────────────┐
  │ Клиент      │
  │ получает    │
  │ конфиг      │
  └─────────────┘
```

---

## НОДЫ WORKFLOW

### 1. Telegram Trigger
```
Webhook URL: https://vpn.xn----7sbaowmfrljlq.xn--p1ai:8443/webhook/yookassa
Method: POST
```

### 2. YooKassa Webhook
```json
{
  "event": "payment.succeeded",
  "object": {
    "id": "...",
    "amount": { "value": "300.00", "currency": "RUB" },
    "metadata": {
      "user_id": "1951845052",
      "period": "month"
    }
  }
}
```

### 3. Обработка
```
- Parse JSON
- Extract: user_id, amount, period, payment_id
- Validate: сумма соответствует тарифу
- логировать в users.db
```

### 4. Активация VPN
```
- Записать в users.db: active=1, expires_at=DATE
- Сгенерировать VLESS ссылку
- Или: использовать trial (если new user)
```

### 5. Telegram Notify
```
Message: 
✅ Оплата получена!

Тариф: 300₽/мес
Период: Май 2026
Статус: АКТИВЕН

🔗 Конфиг: [VLESS ссылка]

Инструкция:
1. Скачай v2rayNG
2. Добавь ссылку
3. Подключайся!
```

---

## ТАРИФЫ

| Период | Цена | YooKassa Item ID |
|--------|------|------------------|
| 1 месяц | 300₽ | (нужен ID) |
| 3 месяца | 800₽ | (нужен ID) |
| 6 месяцев | 1500₽ | (нужен ID) |
| Trial | бесплатно | — |

---

## ФАЙЛЫ

**Webhook сервер:** `/opt/vpn_bot/webhook_server.py`
**База данных:** `/opt/vpn_bot/users.db`
**Telegram Bot:** @datalink_pro_bot

---

## ПЛАН РЕАЛИЗАЦИИ

- [ ] Проверить webhook_server.py (есть ли он)
- [ ] Проверить users.db структуру
- [ ] Создать n8n workflow JSON
- [ ] Протестировать с YooKassa sandbox
- [ ] Перенести в продакшен

---

*n8n workflow будет сохранён в /root/matryoshka/n8n_data/*
