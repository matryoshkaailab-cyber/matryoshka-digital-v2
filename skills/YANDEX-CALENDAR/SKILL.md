# 📅 YANDEX CALENDAR — НАВЫК ДЛЯ ALEX

**Триггер:** Запросы о событиях  
**Протокол:** CalDAV  
**Статус:** ✅ ГОТОВ

---

## 🔑 НАСТРОЙКИ

**URL:** https://caldav.yandex.ru/  
**Логин:** matryoshka.lab@yandex.com

---

## 🛠️ НАВЫКИ

### 1. yandex-calendar-today

**Триггеры:**
- "что сегодня"
- "расписание на день"
- "события сегодня"
- "today schedule"
- "today events"

**Действие:**
```python
import caldav
client = caldav.DAVClient(url, username, password)
principal = client.principal()
calendar = principal.calendar()
events = calendar.date_search(start=today, end=tomorrow)
```

**Выход:**
```
📅 Сегодня — {date}:

{time} — {event_name}
📍 {location}
👥 {attendees}

{time} — {event_name}
📍 {location}
```

---

### 2. yandex-calendar-list

**Триггеры:**
- "покажи события"
- "календарь"
- "show events"
- "calendar"

**Действие:**
```python
calendars = principal.calendars()
for cal in calendars:
    events = cal.events()
```

**Выход:**
```
📅 Календари:

📁 {calendar_name}
  - {event_1} ({date})
  - {event_2} ({date})
```

---

### 3. yandex-calendar-create

**Триггеры:**
- "создай встречу"
- "добавь событие"
- "create meeting"
- "add event"

**Действие:**
```python
event = calendar.save_event(
    dtstart=datetime,
    dtend=datetime,
    summary="Название",
    description="Описание",
    location="Место"
)
```

**Выход:**
```
✅ Событие создано!
📅 {date} {time}
📝 {summary}
📍 {location}
```

---

## 🧪 ТЕСТ

```bash
python3 integrations/YANDEX-360/test_calendar.py
```

**Ожидаемый результат:**
```
✅ CalDAV: Подключение успешно!
✅ CalDAV: Найдено календарей: X
🫡 CalDAV ТЕСТ: УСПЕШНО!
```

---

**🫡 СТАТУС:** ГОТОВ К ИСПОЛЬЗОВАНИЮ

---

**MATRYOSHKA OS v11.0 © 2026**
