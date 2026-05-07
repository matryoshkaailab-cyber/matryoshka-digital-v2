# 📁 YANDEX DISK — НАВЫК ДЛЯ ALEX

**Триггер:** Запросы о файлах  
**Протокол:** WebDAV  
**Статус:** ✅ ГОТОВ

---

## 🔑 НАСТРОЙКИ

**URL:** https://webdav.yandex.ru  
**Логин:** matryoshka.lab@yandex.com

---

## 🛠️ НАВЫКИ

### 1. yandex-disk-list

**Триггеры:**
- "покажи файлы"
- "список файлов"
- "list files"
- "show files"

**Действие:**
```python
import requests
response = requests.request('PROPFIND', url, auth=(email, password))
# Парсинг XML
```

**Выход:**
```
📁 Файлы на Яндекс.Диске:

/
├── /Documents/
├── /Photos/
├── /Work/
└── file.txt
```

---

### 2. yandex-disk-read

**Триггеры:**
- "прочитай файл"
- "открой документ"
- "read file"
- "open document"

**Действие:**
```python
response = requests.get(file_url, auth=(email, password))
content = response.text
```

**Выход:**
```
📄 Файл: {filename}

{content}
```

---

### 3. yandex-disk-write

**Триггеры:**
- "сохрани файл"
- "запиши документ"
- "save file"
- "write document"

**Действие:**
```python
response = requests.put(file_url, data=content, auth=(email, password))
```

**Выход:**
```
✅ Файл сохранён: {filename}
🔗 Ссылка: {webdav_url}
```

---

### 4. yandex-disk-upload

**Триггеры:**
- "загрузи файл"
- "отправь на диск"
- "upload file"
- "save to disk"

**Действие:**
```python
with open(local_path, 'rb') as f:
    response = requests.put(webdav_url, data=f, auth=(email, password))
```

**Выход:**
```
✅ Файл загружен: {filename}
📁 Путь: {path}
```

---

## 🧪 ТЕСТ

```bash
python3 integrations/YANDEX-360/test_disk.py
```

**Ожидаемый результат:**
```
✅ WebDAV: Подключение успешно!
✅ WebDAV: Найдено файлов/папок: X
🫡 WebDAV ТЕСТ: УСПЕШНО!
```

---

**🫡 СТАТУС:** ГОТОВ К ИСПОЛЬЗОВАНИЮ

---

**MATRYOSHKA OS v11.0 © 2026**
