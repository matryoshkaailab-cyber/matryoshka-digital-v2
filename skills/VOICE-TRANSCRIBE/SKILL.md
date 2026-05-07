# 🎤 VOICE TRANSCRIBE — УНИВЕРСАЛЬНЫЙ

**Триггер:** Голосовое сообщение в Telegram  
**API:** Groq Whisper ИЛИ MiniMax ASR  
**Точность:** 90-95%+

---

## 🔑 API КЛЮЧИ

### Groq Whisper (рекомендуется)
```
URL: https://console.groq.com/keys
Формат: gsk_xxxxxxxxxxxxxxxxxxxxx
Лимит: 6000 запросов/месяц (бесплатно)
```

### MiniMax ASR (альтернатива)
```
URL: https://platform.minimaxi.com/
Формат: xxxxxxxxxxxxxxxxxxxxx (без префикса)
Лимит: Бесплатно для тестов
```

---

## 🔧 НАСТРОЙКА

**1. Добавить в .env:**
```bash
# Выбрать один вариант:
VOICE_API_PROVIDER=groq
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# ИЛИ
VOICE_API_PROVIDER=minimax
MINIMAX_API_KEY=xxxxxxxxxxxxxxxxxxxxx
```

**2. Обновить TOOLS.md:**
```markdown
## Voice Transcribe
- Провайдер: Groq Whisper / MiniMax ASR
- Форматы: .ogg, .mp3, .wav, .m4a
- Точность: 90-95%+
- Лимит: 6000/мес (Groq) / ? (MiniMax)
```

---

## 🎤 GROQ API

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
  "text": "расшифрованный текст"
}
```

---

## 🤖 MINIMAX API

**Endpoint:**
```bash
curl https://api.minimax.chat/v1/asr \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@voice.ogg" \
  -F "model=voice-transcription"
```

**Ответ:**
```json
{
  "data": {
    "text": "расшифрованный текст"
  }
}
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
| `429 Too Many Requests` | Превышен лимит |
| `400 Bad Request` | Неверный формат |

---

## 📊 СРАВНЕНИЕ ПРОВАЙДЕРОВ

| Параметр | Groq | MiniMax |
|----------|------|---------|
| **Цена** | Бесплатно | Бесплатно* |
| **Лимит** | 6000/мес | ? |
| **Точность** | 95%+ | 90%+ |
| **Форматы** | .ogg,.mp3,.wav,.m4a,.flac | .ogg,.mp3,.wav |
| **Регион** | США | Китай |

*MiniMax может требовать верификацию

---

**🫡 СТАТУС:** ГОТОВ К ПОДКЛЮЧЕНИЮ  
**🫡 API КЛЮЧ:** ТРЕБУЕТСЯ (Groq ИЛИ MiniMax)  
**🫡 СТОИМОСТЬ:** БЕСПЛАТНО

---

**MATRYOSHKA OS v11.0 © 2026**
