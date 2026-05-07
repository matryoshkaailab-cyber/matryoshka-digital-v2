# 🎤 WHISPER TRANSCRIBE

**Триггер:** Голосовое сообщение в Telegram  
**API:** Groq Whisper (бесплатно, 6000 запросов/мес)  
**Точность:** 95%+

---

## 📋 ПРОЦЕСС

1. Сохранить голосовой файл (.ogg)
2. Отправить POST на Groq API
3. Получить текст транскрипции
4. Вернуть текст Алексу

---

## 🔧 API

**Endpoint:**
```bash
curl https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F "file=@voice.ogg" \
  -F "model=whisper-large-v3"
```

**Ответ:**
```json
{
  "text": "расшифрованный текст сообщения"
}
```

---

## 📁 ФОРМАТЫ

**Поддерживаемые:**
- .ogg (Telegram)
- .mp3
- .wav
- .m4a
- .flac

**Лимиты:**
- Размер: до 25 MB
- Длительность: до 30 мин
- Requests: 6000/месяц (бесплатно)

---

## 🔑 НАСТРОЙКА

**1. Получить API ключ:**
```
https://console.groq.com/keys
```

**2. Добавить в .env:**
```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
```

**3. Обновить TOOLS.md:**
```markdown
## Groq Whisper
- API: https://api.groq.com/openai/v1/audio/transcriptions
- Модель: whisper-large-v3
- Лимит: 6000 запросов/месяц
- Точность: 95%+
```

---

## 🧪 ТЕСТ

**Отправить голосовое в Telegram:**
```
"Привет, Алекс! Это тест расшифровки."
```

**Ожидаемый результат:**
```
🎤 ГОЛОСОВОЕ → ТЕКСТ:

"Привет, Алекс! Это тест расшифровки."
```

---

## ⚠️ ОШИБКИ

| Ошибка | Решение |
|--------|---------|
| `401 Unauthorized` | Проверить API ключ |
| `413 Payload Too Large` | Файл >25MB |
| `429 Too Many Requests` | Лимит 6000/мес |
| `400 Bad Request` | Неверный формат |

---

**🫡 СТАТУС:** ГОТОВ К ПОДКЛЮЧЕНИЮ  
**🫡 API КЛЮЧ:** ТРЕБУЕТСЯ  
**🫡 СТОИМОСТЬ:** БЕСПЛАТНО

---

**MATRYOSHKA OS v11.0 © 2026**
