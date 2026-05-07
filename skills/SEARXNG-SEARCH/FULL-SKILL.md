# 🔍 SEARXNG SEARCH — ПОИСК БЕЗ ОГРАНИЧЕНИЙ

**Триггер:** Запрос на поиск в интернете  
**API:** Self-hosted SearXNG  
**Стоимость:** БЕСПЛАТНО  
**Статус:** ✅ АКТИВНО

---

## 🔑 НАСТРОЙКА

**URL:** `http://localhost:8080`  
**Порт:** 8080 (открыт в брандмауэре)  
**Источники:** 70+ (Google, Bing, DuckDuckGo, Reddit, GitHub...)

---

## 🔧 API

**Endpoint:**
```bash
curl "http://localhost:8080/search?q=запрос&format=json"
```

**Ответ (JSON):**
```json
{
  "query": "запрос",
  "number_of_results": 10,
  "results": [
    {
      "title": "Заголовок результата",
      "url": "https://example.com/page",
      "content": "Описание результата поиска...",
      "engine": "google",
      "category": "general"
    }
  ]
}
```

---

## 📋 ПРОЦЕСС

1. Алекс получает запрос на поиск
2. Формирует query
3. GET запрос на `http://localhost:8080/search?q=query`
4. Извлекает результаты (title, url, content)
5. Возвращает отформатированный ответ

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
   Официальный сайт компании Матрёшка Digital...

2. GitHub: matryoshka-digital
   Репозитории проектов с открытым кодом...

3. Telegram: @matryoshka_digital
   Канал компании с новостями и обновлениями...
```

---

## 🌐 ИСТОЧНИКИ

**Поисковые системы:**
- Google
- Bing
- DuckDuckGo
- Qwant
- Yahoo

**Социальные сети:**
- Reddit
- Twitter
- Facebook

**Разработка:**
- GitHub
- GitLab
- Stack Overflow

**Новости:**
- Google News
- Bing News
- Reddit News

**И ещё 50+ источников!**

---

## ⚙️ УПРАВЛЕНИЕ

**Проверка статуса:**
```bash
docker ps | grep searxng
```

**Перезапуск:**
```bash
docker restart searxng
```

**Логи:**
```bash
docker logs searxng --tail 50
```

**Обновление:**
```bash
docker pull searxng/searxng
docker restart searxng
```

---

## ⚠️ ОШИБКИ

| Ошибка | Решение |
|--------|---------|
| `Connection refused` | Проверить Docker: `docker ps \| grep searxng` |
| `Timeout` | Брандмауэр: `sudo ufw allow 8080/tcp` |
| `No results` | Изменить query или добавить источники |
| `403 Forbidden` | Конфигурация searxng (settings.yml) |

---

## 📊 МОНИТОРИНГ

**Метрики:**
- Запросов в день: отслеживать в логах
- Время ответа: <2 секунд
- Источники: 70+ активных

**Рекомендация:**
- Раз в неделю: проверка доступности
- Раз в месяц: обновление Docker образа

---

## 🔐 ПРИВАТНОСТЬ

**Преимущества self-hosted:**
- ✅ Никакой слежки
- ✅ Никакой персонализации
- ✅ Никаких cookies
- ✅ Полный контроль над источниками

**В отличие от Google/Bing:**
- ❌ Google отслеживает все запросы
- ❌ Bing сохраняет историю
- ❌ Персонализация выдали (пузырь фильтров)

---

**🫡 СТАТУС:** ✅ ГОТОВ К РАБОТЕ  
**🫡 УСТАНОВЛЕНО:** Docker контейнер  
**🫡 СТОИМОСТЬ:** БЕСПЛАТНО  

---

**MATRYOSHKA OS v11.0 © 2026**
