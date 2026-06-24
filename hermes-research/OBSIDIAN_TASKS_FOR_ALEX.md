# Задачи для ALEX — Настройка Obsidian WebDAV Sync

**Цель:** Подключить Obsidian на Windows к VPS vault через WebDAV

---

## ЗАДАЧА 1: Проверить Obsidian

```
Команда: Проверь установлен ли Obsidian на Windows
dir "C:\Users\Oleg\AppData\Local\Obsidian" 2>nul || echo NOT_INSTALLED
dir "C:\Program Files\Obsidian" 2>nul || echo NOT_INSTALLED
```

---

## ЗАДАЧА 2: Инструкция для тебя (ALEX)

Скажи Олегу:

**Obsidian настроен!**

1. Открыть Obsidian на Windows
2. Settings → Sync → WebDAV
3. Vault URL: `http://85.137.166.209:8181/`
4. Username: `hermes`
5. Password: `hermes2026` (пока такой)
6. Test connection

---

## ЗАДАЧА 3: Нужно настроить nginx на VPS

Это я (HERMES) делаю сам, не ALEX.

---

*Создано: 25.05.2026*
