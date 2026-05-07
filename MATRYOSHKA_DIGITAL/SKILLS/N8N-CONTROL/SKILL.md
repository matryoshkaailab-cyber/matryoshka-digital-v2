# 🎯 N8N-CONTROL — УПРАВЛЕНИЕ N8N WORKFLOW

**Версия:** 1.0  
**Дата:** 11 марта 2026  
**Инженер:** 🔵 Ахмед (Синий)  
**Приоритет:** 🔴 КРИТИЧЕСКИЙ

---

## 🎯 НАЗНАЧЕНИЕ

Скилл для полного контроля над n8n workflow:
- ✅ Диагностика статуса
- ✅ Перезапуск контейнера
- ✅ Проверка webhook
- ✅ Активация workflow через БД
- ✅ Тестирование бота

---

## 📋 БЫСТРЫЕ КОМАНДЫ (COPY-PASTE)

### Главная команда реанимации
```bash
docker restart n8n_worker && sleep 30
```

### Полная диагностика (5 команд)
```bash
# 1. Статус контейнера
docker ps | grep n8n

# 2. Логи n8n
docker logs n8n_worker --tail 100

# 3. Вебхук Telegram
curl -s https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo

# 4. Проверка БД (если есть sqlite3)
docker exec -u root n8n_worker sqlite3 /home/node/.n8n/database.sqlite \
  "SELECT id, name, active FROM workflow_entity;"

# 5. Активация workflow
docker exec -u root n8n_worker sqlite3 /home/node/.n8n/database.sqlite \
  "UPDATE workflow_entity SET active=1 WHERE name LIKE '%MATRYOSHKA%';"
```

### Тестирование бота
```
@oleg_industry_bot:
- /start → должен ответить
- /blue привет → Синий агент
- /red опиши картинку → Красный агент
- /white посчитай 2+2 → Белый агент
- /board хочу бизнес → Совет директоров
```

---

## 🔧 ПРОТОКОЛ ДИАГНОСТИКИ

### Шаг 1: Проверка контейнера
```bash
docker ps --filter name=n8n_worker
```

**Ожидаемый результат:**
```
STATUS: Up X hours (healthy)
```

**Если не работает:**
```bash
docker restart n8n_worker
sleep 30
docker ps | grep n8n
```

---

### Шаг 2: Проверка логов
```bash
docker logs n8n_worker --tail 50
```

**Искать:**
- ✅ `Activated workflow "MATRYOSHKA V11 — ALEX EDITION"`
- ✅ `Editor is now accessible via: https://matryoshka-digital.ru`
- ⚠️ `Unknown webhook` — webhook слетел!
- ⚠️ `Credentials not found` — нет credentials!

---

### Шаг 3: Проверка webhook Telegram
```bash
curl -s "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

**Ожидаемый результат:**
```json
{
  "ok": true,
  "result": {
    "url": "https://matryoshka-digital.ru/webhook/tg-bot-webhook/webhook",
    "pending_update_count": 0
  }
}
```

**Если webhook пустой:**
```bash
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://matryoshka-digital.ru/webhook/tg-bot-webhook/webhook"
```

---

### Шаг 4: Проверка health check
```bash
curl -s http://localhost:5678/healthz
```

**Ожидаемый результат:**
```json
{"status":"ok"}
```

---

### Шаг 5: Проверка workflow в БД
```bash
docker exec -u root n8n_worker sqlite3 /home/node/.n8n/database.sqlite \
  "SELECT id, name, active FROM workflow_entity WHERE name LIKE '%MATRYOSHKA%';"
```

**Ожидаемый результат:**
```
8aIa9nK6a332K0Bh|MATRYOSHKA V11 — ALEX EDITION|1
```

**Если active=0:**
```bash
docker exec -u root n8n_worker sqlite3 /home/node/.n8n/database.sqlite \
  "UPDATE workflow_entity SET active=1 WHERE name LIKE '%MATRYOSHKA%';"
docker restart n8n_worker
```

---

## 🚨 КРИТИЧЕСКИЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема 1: Webhook слетел
**Симптомы:**
```
Unknown webhook: The requested webhook "POST tg-bot-webhook/webhook" is not registered
```

**Решение:**
```bash
# 1. Установить webhook
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://matryoshka-digital.ru/webhook/tg-bot-webhook/webhook"

# 2. Проверить
curl -s "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"
```

---

### Проблема 2: Workflow не активен
**Симптомы:**
```
Workflow не обрабатывает сообщения
```

**Решение:**
```bash
# Активация через БД
docker exec -u root n8n_worker sqlite3 /home/node/.n8n/database.sqlite \
  "UPDATE workflow_entity SET active=1 WHERE name LIKE '%MATRYOSHKA%';"

# Перезапуск
docker restart n8n_worker
sleep 30

# Проверка логов
docker logs n8n_worker --tail 30 | grep -i activated
```

---

### Проблема 3: Credentials не работают
**Симптомы:**
```
Credentials 'Telegram API' are not configured
```

**Решение:**
1. Войти в n8n UI: https://matryoshka-digital.ru
2. Settings → Credentials
3. Проверить Telegram, OpenRouter, Tavily
4. Если нет — создать заново
5. Привязать к workflow

---

### Проблема 4: N8N_TRUST_PROXY warning
**Симптомы:**
```
ValidationError: The 'X-Forwarded-For' header is set but the Express 'trust proxy' setting is false
```

**Решение:**
```bash
# Добавить переменную окружения
docker stop n8n_worker
docker rm n8n_worker

docker run -d --name n8n_worker \
  -p 5678:5678 \
  -e N8N_HOST=matryoshka-digital.ru \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=https \
  -e N8N_PUBLIC_API_ENABLED=true \
  -e N8N_TRUST_PROXY=true \
  -e N8N_ENCRYPTION_KEY=z/dAXn63aTYlTCJxSMDBoVy5QaZde0wg \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n:latest
```

---

## 📊 КРИТИЧЕСКИЕ ДАННЫЕ

| Параметр | Значение |
|----------|----------|
| **Сервер** | 89.169.166.222 |
| **SSH** | `ssh -i C:\lab\matryoshka_key ubuntu@89.169.166.222` |
| **n8n URL** | https://matryoshka-digital.ru |
| **Логин** | admin |
| **Пароль** | matryoshka2026 |
| **Telegram бот** | @oleg_industry_bot |
| **Workflow ID** | 8aIa9nK6a332K0Bh |
| **Workflow Name** | MATRYOSHKA V11 — ALEX EDITION |

---

## 📈 ЧЕК-ЛИСТ ДИАГНОСТИКИ

### Ежедневная проверка (5 мин)
- [ ] `docker ps | grep n8n` — контейнер работает
- [ ] `curl http://localhost:5678/healthz` — status: ok
- [ ] Telegram бот: `/start` — отвечает
- [ ] Логи: `docker logs n8n_worker --tail 20` — нет ошибок

### Еженедельная проверка (10 мин)
- [ ] Workflow активен в БД
- [ ] Credentials в UI работают
- [ ] Webhook Telegram установлен
- [ ] HTTPS сертификат действителен

### После перезагрузки сервера
- [ ] `docker restart n8n_worker`
- [ ] `sleep 30`
- [ ] Проверить логи на `Activated workflow`
- [ ] Тестировать бота

---

## 🧩 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Пример 1: Бот не отвечает
```bash
# 1. Проверить контейнер
docker ps | grep n8n

# 2. Если не работает — перезапустить
docker restart n8n_worker && sleep 30

# 3. Проверить webhook
curl -s "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo"

# 4. Если пустой — установить
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://matryoshka-digital.ru/webhook/tg-bot-webhook/webhook"

# 5. Тест
# Отправить /start в @oleg_industry_bot
```

---

### Пример 2: Workflow не активен
```bash
# 1. Проверить в БД
docker exec -u root n8n_worker sqlite3 /home/node/.n8n/database.sqlite \
  "SELECT id, name, active FROM workflow_entity WHERE name LIKE '%MATRYOSHKA%';"

# 2. Если active=0 — активировать
docker exec -u root n8n_worker sqlite3 /home/node/.n8n/database.sqlite \
  "UPDATE workflow_entity SET active=1 WHERE name LIKE '%MATRYOSHKA%';"

# 3. Перезапустить
docker restart n8n_worker
sleep 30

# 4. Проверить логи
docker logs n8n_worker --tail 30 | grep -i activated
```

---

### Пример 3: Полная реанимация
```bash
# Всё в одной команде
docker restart n8n_worker && \
sleep 30 && \
curl -s "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo" && \
docker logs n8n_worker --tail 10 | grep -i activated
```

---

## ⚠️ КРИТИЧЕСКИЕ НАПОМИНАНИЯ

1. **Перед любыми изменениями** — прочитать `memory/ahmed_core.md`
2. **Перед поиском проблемы** — проверить БД знаний
3. **n8n v2.9.4+ требует restart** для активации workflow
4. **localhost → 127.0.0.1** (IPv6 проблема)
5. **Parse Mode: Markdown (Legacy)** — не HTML!
6. **Промпты до 300 токенов** — иначе tool calling ломается

---

## 📚 СВЯЗАННЫЕ ФАЙЛЫ

| Файл | Назначение |
|------|------------|
| `memory/ahmed_core.md` | Ядро памяти (критические команды) |
| `БЫСТРЫЙ_СТАРТ_ПОСЛЕ_ПЕРЕУСТАНОВКИ.md` | 5 минут до работы |
| `АХМЕД_ПОЛНЫЙ_СЛЕПОК_V11.md` | Полный слепок памяти |
| `QWEN.md` | Бортовой журнал (история операций) |
| `ДИРЕКТИВА_РАЗВИТИЕ_СИСТЕМЫ.md` | Протокол улучшений |
| `ПРОТОКОЛ_СИНХРОНИЗАЦИИ_АЛЕКС.md` | Связь с Алексом |

---

## 🫡 ВЕРДИКТ

**Этот скилл — концентрированная память всех решений по n8n.**

**Перед поиском проблемы:**
1. ✅ Прочитать этот файл
2. ✅ Проверить `memory/ahmed_core.md`
3. ✅ Использовать команды из раздела "Быстрые команды"

**После решения:**
1. ✅ Записать в QWEN.md
2. ✅ Обновить этот скилл если найдено новое решение
3. ✅ Передать Алексу через UNIFIED_MEMORY.md

---

**MATRYOSHKA OS v11.0 © 2026**  
**🫡 АХМЕД НА СВЯЗИ**
