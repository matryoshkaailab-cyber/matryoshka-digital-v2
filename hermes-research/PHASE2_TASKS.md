# ФАЗА 2 — Obsidian + Memory + Backup
## MATROSHKA DIGITAL — Задачи для ALEX

**Статус:** В РАБОТЕ
**Дата:** 25.05.2026
**Исполнители:** ALEX (Windows) + HERMES (VPS)

---

## ЗАДАЧИ ФАЗЫ 2

### 1. Obsidian — Настройка Vault

**Цель:** Создать центральную базу знаний MATROSHKA

**Структура папок:**
```
MATRYOSHKA_VAULT/
├── clients/           # Клиенты (DATALINK, Nikolay, etc.)
├── projects/          # Проекты (VPN, VR Club, etc.)
├── leads/             # Лиды и воронка продаж
├── analytics/        # Аналитика и метрики
├── agents/           # Досье агентов
└── daily/            # Ежедневные заметки
```

**Ты (ALEX):**
- Открой Obsidian на Windows
- Создай vault `MATRYOSHKA_DIGITAL`
- Создай структуру папок
- Добавь README.md в каждую папку с описанием

**HERMES:**
- Установить Obsidian на VPS (если нужно)
- Подключить через skill obsidian
- Настроить sync

---

### 2. Yandex Disk — Backup

**Цель:** Автоматический backup в Yandex Disk

**Задачи:**
- Настроить WebDAV синхронизацию
- Создать cron job: ежедневно в 03:00
- Бекапить: configs, memories, SOUL.md, tracking

**Команда:**
```bash
# Проверить яндекс диск
curl -u "oauth_token" https://webdav.yandex.ru/
```

---

### 3. Memory System — Внедрение

**Цель:** Сделать память Hermes долгосрочной

**Компоненты:**
- fuzzy index для быстрого поиска
- peer cards для агентов
- session history

**Файлы:**
- `/root/.hermes/profiles/hermes-cli/memories/memory.md` — обновить
- `/root/matryoshka/MEMORY_GUIDE.md` — создать

---

## КОНТРОЛЬНЫЕ ТОЧКИ

| Задача | Статус | Дата выполнения |
|--------|--------|-----------------|
| Vault создан | ⏳ | |
| Структура папок | ⏳ | |
| WebDAV настроен | ⏳ | |
| Cron backup | ⏳ | |
| Memory обновлён | ⏳ | |

---

## КАНАЛ СВЯЗИ

- ALEX → HERMES: через ws_server
- HERMES → ALEX: отчёты сюда в Telegram

---

*Обновлено: 25.05.2026 21:15*