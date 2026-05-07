# 📧 YANDEX MAIL — НАВЫК ДЛЯ ALEX

**Триггер:** Запросы о почте  
**Протокол:** IMAP/SMTP  
**Статус:** ✅ ГОТОВ

---

## 🔑 НАСТРОЙКИ

**Email:** matryoshka.lab@yandex.com  
**IMAP:** imap.yandex.ru:993 (SSL)  
**SMTP:** smtp.yandex.ru:465 (SSL)

---

## 🛠️ НАВЫКИ

### 1. yandex-mail-unread

**Триггеры:**
- "прочитай почту"
- "новые письма"
- "сколько непрочитанных"
- "check mail"
- "unread emails"

**Действие:**
```python
import imaplib
mail = imaplib.IMAP4_SSL("imap.yandex.ru", 993)
mail.login(email, password)
mail.select("inbox")
status, messages = mail.search(None, "UNSEEN")
unread_count = len(messages[0].split())
```

**Выход:**
```
📧 Непрочитанных писем: {count}

Последние 5:
1. От: {sender} — Тема: {subject}
2. От: {sender} — Тема: {subject}
...
```

---

### 2. yandex-mail-read

**Триггеры:**
- "прочитай письмо"
- "открой письмо"
- "read email"
- "read message"

**Действие:**
```python
# IMAP подключение + чтение последнего письма
```

**Выход:**
```
📧 Письмо от: {sender}
Тема: {subject}
Дата: {date}

{body}
```

---

### 3. yandex-mail-send

**Триггеры:**
- "отправь письмо"
- "напиши письмо"
- "send email"
- "send message"

**Действие:**
```python
import smtplib
from email.mime.text import MIMEText
# SMTP отправка
```

**Выход:**
```
✅ Письмо отправлено!
Кому: {recipient}
Тема: {subject}
```

---

## 🧪 ТЕСТ

```bash
python3 integrations/YANDEX-360/test_mail.py
```

**Ожидаемый результат:**
```
✅ IMAP: Подключение успешно!
✅ IMAP: Непрочитанных писем: X
🫡 IMAP ТЕСТ: УСПЕШНО!
```

---

**🫡 СТАТУС:** ГОТОВ К ИСПОЛЬЗОВАНИЮ

---

**MATRYOSHKA OS v11.0 © 2026**
