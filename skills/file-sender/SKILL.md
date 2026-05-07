# 📎 FILE SENDER — Отправка файлов

## РОЛЬ
Ты умеешь отправлять файлы пользователям через Telegram.

## ВОЗМОЖНОСТИ

### 1. Отправка документов
```python
def send_document(chat_id, file_path, caption=None):
    url = f'{TELEGRAM_URL}/sendDocument'
    data = {
        'chat_id': chat_id,
        'caption': caption or 'Документ готов!'
    }
    with open(file_path, 'rb') as doc:
        files = {'document': doc}
        response = requests.post(url, data=data, files=files)
    return response.json()
```

### 2. Отправка фото
```python
def send_photo(chat_id, file_path, caption=None):
    url = f'{TELEGRAM_URL}/sendPhoto'
    data = {
        'chat_id': chat_id,
        'caption': caption or 'Фото готово!'
    }
    with open(file_path, 'rb') as photo:
        files = {'photo': photo}
        response = requests.post(url, data=data, files=files)
    return response.json()
```

### 3. Сохранение и отправка
```python
# Создание документа
from docx import Document
doc = Document()
doc.add_heading('Договор', 0)
doc.add_paragraph('Текст...')
file_path = '/tmp/documents/dogovor.docx'
doc.save(file_path)

# Отправка пользователю
send_document(chat_id, file_path, 'Ваш договор готов!')

# Удаление после отправки
os.remove(file_path)
```

## ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Договор:
```
Пользователь: "Создай договор для Анны"
Ты:
1. Создаёшь /tmp/documents/dogovor_Anna.docx
2. Заполняешь шаблон данными
3. Отправляешь файлом пользователю
4. Удаляешь файл после отправки
```

### Счёт:
```
Пользователь: "Сделай счёт на 4990₽"
Ты:
1. Создаёшь /tmp/documents/schet_4990.pdf
2. Заполняешь реквизиты
3. Отправляешь файлом
4. Удаляешь файл
```

### Отчёт:
```
Пользователь: "Отчёт за неделю"
Ты:
1. Создаёшь /tmp/documents/otchet_week.docx
2. Добавляешь метрики, таблицы
3. Отправляешь файлом
4. Сохраняешь копию на Диск
```

## ОЧИСТКА

### Авто-удаление:
```python
import tempfile
import atexit

# Временная папка
TEMP_DIR = tempfile.mkdtemp()

# Удалить при выходе
atexit.register(lambda: os.system(f'rm -rf {TEMP_DIR}'))
```

### Плановая чистка:
```bash
# Cron: каждые 5 минут
*/5 * * * * find /tmp/documents -type f -mmin +5 -delete
```

## ЛИМИТЫ TELEGRAM

| Тип файла | Макс размер |
|-----------|-------------|
| **Document** | 50 MB |
| **Photo** | 10 MB |
| **Audio** | 50 MB |
| **Video** | 50 MB |

## БЕЗОПАСНОСТЬ

- ✅ Проверка пути файла (только /tmp/)
- ✅ Валидация расширения (.docx, .pdf, .xlsx)
- ✅ Удаление после отправки
- ✅ Логирование отправленных файлов
