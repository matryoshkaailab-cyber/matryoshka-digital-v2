# 🛠️ SKILL: N8N-MANAGER

**Версия:** 1.0  
**Дата:** 10 марта 2026 г.  
**Статус:** ✅ АКТИВЕН

---

## 📋 ОПИСАНИЕ

Управление n8n workflow через API.

**Возможности:**
- ✅ Активация/деактивация workflow
- ✅ Проверка статуса
- ✅ Запуск workflow (execute)
- ✅ Проверка логов
- ✅ Управление webhook

---

## 🔑 ДОСТУПНЫЕ ДАННЫЕ

**n8n API:**
```
URL: https://matryoshka-digital.ru
API: https://matryoshka-digital.ru/api/v1
Workflow ID: 8aIa9nK6a332K0Bh
Workflow Name: "MATRYOSHKA V11 — ALEX EDITION"
```

**API Key:**
```
X-N8N-API-KEY: n8n_api_matryoshka_2026_secure_key_001
```

---

## 🎯 КОМАНДЫ

### 1. ПРОВЕРИТЬ СТАТУС WORKFLOW

**Команда:**
```
/n8n status
```

**Выполнение:**
```bash
curl -s https://matryoshka-digital.ru/api/v1/workflows/8aIa9nK6a332K0Bh \
  -H "X-N8N-API-KEY: n8n_api_matryoshka_2026_secure_key_001"
```

**Ответ:**
```json
{
  "id": "8aIa9nK6a332K0Bh",
  "name": "MATRYOSHKA V11 — ALEX EDITION",
  "active": true,
  "createdAt": "2026-03-09T...",
  "updatedAt": "2026-03-10T..."
}
```

---

### 2. АКТИВИРОВАТЬ WORKFLOW

**Команда:**
```
/n8n activate
```

**Выполнение:**
```bash
curl -s -X POST https://matryoshka-digital.ru/api/v1/workflows/8aIa9nK6a332K0Bh/activate \
  -H "X-N8N-API-KEY: n8n_api_matryoshka_2026_secure_key_001"
```

**Ответ:**
```json
{
  "active": true,
  "message": "Workflow activated"
}
```

---

### 3. ДЕЗАКТИВИРОВАТЬ WORKFLOW

**Команда:**
```
/n8n deactivate
```

**Выполнение:**
```bash
curl -s -X POST https://matryoshka-digital.ru/api/v1/workflows/8aIa9nK6a332K0Bh/deactivate \
  -H "X-N8N-API-KEY: n8n_api_matryoshka_2026_secure_key_001"
```

---

### 4. ЗАПУСТИТЬ WORKFLOW (TEST)

**Команда:**
```
/n8n run
```

**Выполнение:**
```bash
curl -s -X POST https://matryoshka-digital.ru/api/v1/workflows/8aIa9nK6a332K0Bh/run \
  -H "X-N8N-API-KEY: n8n_api_matryoshka_2026_secure_key_001" \
  -H "Content-Type: application/json" \
  -d '{
    "startNodes": ["Telegram"],
    "data": {
      "query": "тест",
      "chat_id": "1951845052",
      "mode": "blue"
    }
  }'
```

---

### 5. ПРОВЕРИТЬ WEBHOOK

**Команда:**
```
/n8n webhook
```

**Выполнение:**
```bash
curl -s https://matryoshka-digital.ru/api/v1/webhooks \
  -H "X-N8N-API-KEY: n8n_api_matryoshka_2026_secure_key_001"
```

**Ожидаемый webhook:**
```
POST /webhook/tg-bot-webhook
```

---

### 6. ПРОВЕРИТЬ ЛОГИ

**Команда:**
```
/n8n logs
```

**Выполнение:**
```bash
ssh -i C:/lab/matryoshka_key ubuntu@89.169.166.222 \
  "docker logs n8n_worker --tail 50"
```

---

## 📊 СТАТУСЫ

| Статус | Значение |
|--------|----------|
| **active: true** | ✅ Workflow активен |
| **active: false** | ❌ Workflow деактивирован |
| **error** | ⚠️ Ошибка выполнения |

---

## 🔧 ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### Проблема 1: Workflow не активен

**Решение:**
```bash
/n8n activate
```

---

### Проблема 2: Webhook не работает

**Проверка:**
```bash
curl -s https://matryoshka-digital.ru/webhook/tg-bot-webhook
```

**Решение:**
```bash
# Перезапустить n8n
docker restart n8n_worker
sleep 30

# Проверить логи
docker logs n8n_worker --tail 50
```

---

### Проблема 3: API key не работает

**Решение:**
```bash
# Создать новый API key в n8n UI
https://matryoshka-digital.ru/settings/api
```

---

## ✅ ЧЕК-ЛИСТ ПРОВЕРКИ

- [ ] 1. Workflow активен?
- [ ] 2. Webhook зарегистрирован?
- [ ] 3. Логи чистые (нет ошибок)?
- [ ] 4. Telegram бот отвечает?
- [ ] 5. Подагент "Анна" работает?

---

## 🫡 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Пример 1: Проверка статуса

**Олег:** "Ахмед, проверь n8n"

**Ахмед:**
```
🫡 ПРОВЕРЯЮ N8N!

/n8n status

✅ Workflow: MATRYOSHKA V11 — ALEX EDITION
✅ Status: Active
✅ Webhook: Зарегистрирован
✅ Логи: Чистые

🎯 Всё работает!
```

---

### Пример 2: Активация workflow

**Олег:** "Ахмед, активируй workflow"

**Ахмед:**
```
🫡 АКТИВИРУЮ N8N!

/n8n activate

✅ Workflow активирован
✅ Webhook перерегистрирован
✅ Готов к работе!

🎯 Жду команду!
```

---

### Пример 3: Тестирование

**Олег:** "Ахмед, протестируй схему"

**Ахмед:**
```
🫡 ТЕСТИРУЮ N8N!

/n8n run

✅ Workflow запущен
✅ Telegram webhook: OK
✅ Обработка: OK
✅ Ответ: OK

🎯 Схема работает!
```

---

## 📁 ФАЙЛЫ

**Skill:**
```
skills/N8N-MANAGER/SKILL.md (этот файл)
```

**Конфиг:**
```
integrations/N8N-CREDENTIALS.md
```

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

1. ✅ Skill создан
2. ⏳ Протестировать команды
3. ⏳ Добавить в Алекс (автоматическое использование)
4. ⏳ Настроить мониторинг

---

**MATRYOSHKA OS v11.0 © 2026**
