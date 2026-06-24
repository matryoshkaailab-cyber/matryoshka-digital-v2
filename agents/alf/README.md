# Агент: ALF (@IlonAnalyticBot)

**Статус:** Активен
**Тип:** Стратег-консультант (НЕ путать с АЛЕКС)
**Платформа:** VPS (Hermes)
**Telegram:** @IlonAnalyticBot, ID: 8941776316
**Назначение:** Стратегический аналитик, консультант для Олега

---

## Роль и назначение

ALF — ИИ-стратег для MATRYOSHKA DIGITAL. Помогает Олегу с:
- Стратегическими вопросами бизнеса
- Анализом данных
- Консультациями по кейсам (DATALINK PRO, ЛЕГИОН, НИКОЛАЙ+АЛИНА)
- Долгосрочным планированием

**НЕ путать с АЛЕКС** — АЛЕКС это Windows ПК (инженер), ALF это VPS стратег.

---

## Архитектура

```
ALF (VPS Linux)
├─ alf_telegram_bot.py (PID 939) — Telegram-бот
│  └─ слушает @IlonAnalyticBot через long polling
│
└─ alf_server.py (PID 980) — HTTP API на порту 8451
   └─ /health, /v1/chat/completions (OpenAI-compatible)
      └─ → Qwen 3.7 Max (локально через node на 8765)
```

---

## Конфигурация

### Система
- **Путь:** /root/matryoshka/alf/
- **alf_telegram_bot.py** — Telegram-интерфейс
- **alf_server.py** — HTTP API
- **.env** — секреты (alf/.env)
- **PID:** 939 (alf_telegram_bot), 980 (alf_server)

### Модель
- **Brain:** qwen3.7-max (НЕ MiniMax!)
- **Endpoint:** http://127.0.0.1:8765/v1 (локальный node)
- **Fallback:** MiniMax-M3 (если Qwen недоступен)

### systemd
- **alf-telegram.service** — главный сервис
- **hermes-alf.service** (порт 8451) — HTTP API
- **Активность:** оба running

### Telegram
- **Bot:** @IlonAnalyticBot
- **ID:** 8941776316
- **Назначение:** стратегические консультации

---

## Связь с другими агентами

| Агент | Связь |
|---|---|
| HERMES | вызывает ALF через hermes-alf API (8451) |
| ОЛЕГ (ПК) | общается через @IlonAnalyticBot |
| АЛИНА | независима, оба VPS |

---

## TODO

- [x] Создать досье (этот файл)
- [x] Настроить systemd alf-telegram + hermes-alf
- [ ] Добавить метрики использования
- [ ] Проверить fallback на MiniMax

---

## Изменения (лог)

### 09.06.2026
- Создан /root/matryoshka/agents/alf/README.md
- Зафиксирована архитектура: ALF (VPS) + Qwen 3.7 Max (локально)
- Подтверждено что ALF ≠ АЛЕКС (стратег ≠ инженер)

| HERMES |
