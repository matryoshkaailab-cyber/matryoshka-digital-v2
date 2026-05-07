# 🫡 SKILL: БЫСТРЫЙ SSH ВХОД НА СЕРВЕР

**Версия:** 1.0  
**Дата:** 13 марта 2026 г.  
**Статус:** ✅ БОЕВОЙ НАВЫК

---

## 🎯 НАЗНАЧЕНИЕ

Быстрый вход на сервер MATRYOSHKA без запросов и ошибок.

---

## 🔑 КОМАНДА ДЛЯ ВХОДА

```bash
ssh -i C:\lab\matryoshka_key -o StrictHostKeyChecking=accept-new -T ubuntu@89.169.166.222 < команда
```

**Или для скрипта:**
```bash
ssh -i C:\lab\matryoshka_key -o StrictHostKeyChecking=accept-new ubuntu@89.169.166.222 "bash /home/ubuntu/script.sh"
```

**Или SCP для файлов:**
```bash
scp -i C:\lab\matryoshka_key -o StrictHostKeyChecking=accept-new файл ubuntu@89.169.166.222:/home/ubuntu/
```

---

## ⚙️ ПАРАМЕТРЫ

| Параметр | Значение |
|----------|----------|
| **Ключ** | `C:\lab\matryoshka_key` |
| **Пользователь** | `ubuntu` |
| **Сервер** | `89.169.166.222` |
| **Опция** | `-o StrictHostKeyChecking=accept-new` |
| **Опция** | `-T` (для команд) |

---

## 📋 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### 1. Проверка контейнеров:
```bash
ssh -i C:\lab\matryoshka_key -o StrictHostKeyChecking=accept-new ubuntu@89.169.166.222 "docker ps"
```

### 2. Логи n8n:
```bash
ssh -i C:\lab\matryoshka_key -o StrictHostKeyChecking=accept-new ubuntu@89.169.166.222 "docker logs n8n_worker --tail 50"
```

### 3. Перезапуск контейнера:
```bash
ssh -i C:\lab\matryoshka_key -o StrictHostKeyChecking=accept-new ubuntu@89.169.166.222 "docker restart n8n_worker"
```

### 4. Загрузка файла:
```bash
scp -i C:\lab\matryoshka_key -o StrictHostKeyChecking=accept-new c:\matryoshka\script.sh ubuntu@89.169.166.222:/home/ubuntu/
```

### 5. Выполнение скрипта:
```bash
ssh -i C:\lab\matryoshka_key -o StrictHostKeyChecking=accept-new -T ubuntu@89.169.166.222 < c:\matryoshka\script.sh
```

---

## ⚠️ ВАЖНО

1. **НЕ спрашивать разрешение** — выполнять сразу
2. **НЕ жаловаться на ключи** — опция `StrictHostKeyChecking=accept-new` решает
3. **НЕ говорить что не работает** — использовать `-T` для команд
4. **Всегда использовать IP 89.169.166.222** — актуальный адрес

---

## 🧪 ПРОВЕРКА

```bash
# Быстрая проверка что сервер доступен
ssh -i C:\lab\matryoshka_key -o StrictHostKeyChecking=accept-new ubuntu@89.169.166.222 "echo 'Ахмед на связи!'"
```

---

**MATRYOSHKA OS v11.0 © 2026**

**🫡 АХМЕД НА СВЯЗИ!**
