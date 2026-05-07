# 📁 YANDEX DISK — НАВЫК ЭКЛЕРА

**Версия:** 1.0
**Статус:** ✅ АКТИВЕН

---

## 🔑 ТВОЙ ТОКЕН

```
YANDEX DISK OAuth: y0__xDGyP1mGN3UPiD8m4XdFnOnoOJAYQxNmR4hkcjn0DwLWfTF
```

**У ТЕБЯ ЕСТЬ ДОСТУП К ЯНДЕКС.ДИСКУ!**

---

## 📂 ТВОИ ПАПКИ

```
/Matryoshka_Alex_Share/
├── reports/
│   ├── alex/           # Отчёты Алекса (ЧИТАЙ)
│   │   └── daily/
│   └── eclair/         # ТВОИ отчёты (ПИШИ СЮДА)
│       └── daily/
├── Alexa/              # Твои файлы
│   ├── ALEXA_SNAPSHOT.md
│   └── memory/
└── shared/             # Общие файлы
```

---

## 🛠️ КОМАНДЫ

### Прочитать файл:
```bash
curl "https://cloud-api.yandex.net/v1/disk/resources/download?path=/Matryoshka_Alex_Share/reports/alex/daily/test.md" \
  -H "Authorization: OAuth y0__xDGyP1mGN3UPiD8m4XdFnOnoOJAYQxNmR4hkcjn0DwLWfTF"
```

### Записать файл:
```bash
# 1. Получить ссылку
curl -X POST "https://cloud-api.yandex.net/v1/disk/resources/upload?path=/Matryoshka_Alex_Share/reports/eclair/daily/test.md&overwrite=true" \
  -H "Authorization: OAuth y0__xDGyP1mGN3UPiD8m4XdFnOnoOJAYQxNmR4hkcjn0DwLWfTF"

# 2. Загрузить файл
curl -X PUT "<URL>" -T file.md
```

### Список файлов:
```bash
curl "https://cloud-api.yandex.net/v1/disk/resources?path=/Matryoshka_Alex_Share/" \
  -H "Authorization: OAuth y0__xDGyP1mGN3UPiD8m4XdFnOnoOJAYQxNmR4hkcjn0DwLWfTF"
```

---

## 📋 ТВОИ ОТЧЁТЫ

**Пиши сюда:** `/Matryoshka_Alex_Share/reports/eclair/daily/YYYY-MM-DD_evening.md`

**Формат:**
```markdown
# Отчёт Эклера → Алексу

**Дата:** 21.03.2026 20:00

## 📊 Работа за день
Клиентов: X
Записей: Y

## ❓ Вопросы для Алекса
1. [Вопрос]

---
Эклер 🔴
```

---

## ✅ ЗАПОМНИ

1. **У ТЕБЯ ЕСТЬ ДОСТУП К ЯНДЕКС.ДИСКУ!**
2. **Токен:** y0__xDGyP1mGN3UPiD8m4XdFnOnoOJAYQxNmR4hkcjn0DwLWfTF
3. **Пиши отчёты:** /reports/eclair/daily/
4. **Читай отчёты Алекса:** /reports/alex/daily/

---

**MATRYOSHKA OS v11.0 © 2026**
