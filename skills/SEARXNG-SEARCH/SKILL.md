# 🔍 SEARXNG SEARCH

**Триггер:** Запрос на поиск в интернете  
**API:** Self-hosted SearXNG (бесплатно)  
**Приватность:** Полная

---

## 📋 ПРОЦЕСС

1. Сформировать search query
2. GET запрос на localhost:8080
2. Извлечь результаты (title, url, content)
3. Вернуть Алексу

---

## 🔧 API

**Endpoint:**
```bash
curl "http://localhost:8080/search?q=запрос&format=json"
```

**Ответ:**
```json
{
  "results": [
    {
      "title": "Заголовок",
      "url": "https://example.com",
      "content": "Описание результата..."
    }
  ]
}
```

---

## 📁 УСТАНОВКА

**Docker:**
```bash
docker run -d \
  --name searxng \
  -p 8080:8080 \
  -e SEARXNG_BASE_URL="http://localhost:8080/" \
  searxng/searxng
```

**Брандмауэр:**
```bash
sudo ufw allow 8080/tcp
```

**Проверка:**
```bash
curl "http://localhost:8080/search?q=test&format=json"
```

---

## 🔑 НАСТРОЙКА

**Добавить в TOOLS.md:**
```markdown
## SearXNG
- URL: http://localhost:8080
- Поиск: без ограничений
- Приватность: полная
- Интеграция: HTTP API
```

---

## 🧪 ТЕСТ

**Запрос:**
```
Найди информацию про MATRYOSHKA Digital
```

**Ожидаемый результат:**
```
🔍 ПОИСК: MATRYOSHKA Digital

1. matryoshka-digital.ru
   Официальный сайт компании...

2. GitHub: matryoshka-digital
   Репозитории проектов...

3. Telegram: @matryoshka_digital
   Канал компании...
```

---

## ⚠️ ОШИБКИ

| Ошибка | Решение |
|--------|---------|
| `Connection refused` | Проверить Docker |
| `Timeout` | Брандмауэр |
| `No results` | Изменить query |

---

**🫡 СТАТУС:** ГОТОВ К УСТАНОВКЕ  
**🫡 СТОИМОСТЬ:** БЕСПЛАТНО  
**🫡 ВРЕМЯ:** 1 час

---

**MATRYOSHKA OS v11.0 © 2026**
