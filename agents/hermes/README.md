# Агент: HERMES (@hermes_agent)

**Статус:** Активен
**Тип:** Дирижёр — оркестратор всех агентов MATROSHKA DIGITAL
**Платформа:** VPS Linux (85.137.166.209)
**Управляет:** Алекс, АЛИНА, Алина

---

## Роль и назначение

HERMES — центральный координатор MATROSHKA DIGITAL. Единственный агент, который знает ВСЮ систему целиком.

**Главная задача:**确保 все агенты работают как единый оркестр, а не как изолированные боты.

**Не делает:** пишет код, но не кодит сам (делегирует Алексу через ws_client).

---

## Архитектура

```
Олег (1951845052)
       ↓
HERMES (VPS Linux)
  ├─ Telegram gateway → @oleg_industry_bot (active)
  ├─ ACP → ALEX Windows PC (10.8.1.4:4096) — ЕДИНСТВЕННЫЙ канал к ALEX
  ├─ ALF (@IlonAnalyticBot) — VPS стратег/аналитик
  ├─ ALINA (@NikolaAlinaBot) — VPS, клиент Николай (8 сервисов :8470-8476)
  └─ ALISA (@AlisaMatBot) — маркетинг (отложена)
```

**Устаревшие каналы (отключены 15.06.2026):**
- ~~ws_server :8446/:8450~~ ❌ мёртв
- ~~ws_client → ALEX через ws~~ ❌ мёртв
- ~~Tailscale~~ ❌ не установлен

---

## Конфигурация

### Система
- **OS:** Linux 6.8.0-110-generic (VPS)
- **HERMES_HOME:** /root/.hermes
- **PID ws_server:** 1605544
- **Лог:** /var/log/hermes_ws.log
- **Текущая модель по умолчанию:** `nex-agi/nex-n2-pro:free` через `openrouter`
- **Модельная витрина:** OpenRouter, локально добавлен `nex-agi/nex-n2-pro:free` в `/usr/local/lib/hermes-agent/hermes_cli/models.py`

### ws_server
- Port: 8446 (incoming от Алекс)
- Port: 8450 (CLI connection)
- Token: hermes-ws-secret-2026

### ws_client → Алекс
- Target: Windows ПК Алекс
- Port: 8446/8450
- Token: hermes-ws-secret-2026

---

## Процесс работы (ЖЁСТКИЙ)

### Перед любой работой
1. Прочитать MEMORY.md
2. Если есть relevant skill → skill_view()
3. Если аудит/анализ → проверить данные в state.db
4. НЕ выдумывать время/даты/факты

### При задаче от Олега
1. Сделать
2. Проверить сам
3. Только потом сказать "готово"

### Формат отчёта
```
=== ВЫПОЛНИЛ ===
Действие: ...
Проверка: ...
Статус: ✓/✗
```

---

## Задачи и функции

### Оркестрация
- [x] Создать агентов: Алекс, АЛИНА, Алина
- [x] Настроить ws_server на VPS
- [x] Подключить Алекс (Windows ПК) через ws_client
- [ ] Настроить мониторинг всех агентов

### Документация (ВЕЧНАЯ ОБЯЗАННОСТЬ)
- [x] Создать папку /root/matryoshka/agents/
- [x] Досье Алекс
- [x] Досье АЛИНА
- [x] Досье Алина
- [x] Досье HERMES (этот файл)
- [ ] Заполнять каждый файл при изменениях

### Мониторинг
- [ ] Наблюдать за Алиной/Nikolay (3 раза/день)
- [ ] Фиксировать боли в pain-log.md
- [ ] Собирать метрики daily_metrics

---

## Файловая структура MATROSHKA DIGITAL

```
/root/matryoshka/
├── agents/
│   ├── alex/README.md        — досье Алекс
│   ├── ekler/README.md       — досье АЛИНА
│   ├── alina/README.md       — досье Алина
│   └── hermes/README.md      — досье HERMES (этот)
├── cases/
│   ├── nikolay/             — кейс Nikolay
│   │   ├── .env
│   │   ├── PASSPORT.md
│   │   ├── pain-log.md
│   │   └── metrics/
│   └── alina/               — кейс АЛИНА/Наталья
├── bots/
│   ├── alex/projects/       — проекты Алекс
│   └── alex/configs/        — конфиги Алекс
└── skills/
    └── MATRYOSHKA_DIGITAL/
        └── PRODUCT-SALES-GUIDE.md
```

---

## Память HERMES

### MEMORY.md (1625/2200 символов)
- Identity: дирижёр MATROSHKA DIGITAL
- АЛЬФ = стратег-консультант (НЕ путать с Алекс)
- АЛЕКС = Windows ПК, ws_client → VPS
- Сергей Бородин (7453044462) = ЗАБЛОКИРОВАН
- Олег (1951845052) = хозяин
- Процесс: читать → делать → проверять → отчитываться
- Кейсы: в /root/matryoshka/cases/

### USER.md (1311/1375 символов)
- Олег: перфекционист, 100% тестирование, хочет уверенного HERMES
- АЛИНА: @NikolaAlinaBot, tirith=false, cron=allow, Bookmate API=404

---

## Контакты и взаимодействие

| Агент | Telegram | Платформа | Статус |
|-------|----------|-----------|--------|
| Олег | 1951845052 | Telegram | Хозяин |
| Алекс | @oleg_industry_bot | Windows ПК | Активен (ws) |
| АЛИНА | @ZarnyAlexaBot | VPS | Активен |
| Алина | @NikolaAlinaBot | VPS | Активен |
| Сергей Бородин | 7453044462 | Telegram | ЗАБЛОКИРОВАН |

---

## TODO

- [x] Создать досье на всех агентов
- [x] Настроить ws_server
- [x] Подключить Алекс
- [ ] Заполнить pain-log.md (Алина/Nikolay)
- [ ] Аудит конфигов АЛИНА
- [ ] Починить Bookmate API (404)
- [ ] Настроить ежедневный мониторинг

---

## Изменения (лог)

### 14.06.2026
- Подключена бесплатная OpenRouter модель `nex-agi/nex-n2-pro:free` как модель по умолчанию Hermes.
- Локально добавлена в модельную витрину Hermes, потому что официальный curated catalog Hermes её не показывал.
- Перезапущен gateway профиля `hermes-cli`, чтобы выбор моделей подхватил изменение.

### 25.05.2026
- Создан этот файл
- Добавлен в /root/matryoshka/agents/hermes/README.md
- MEMORY.md почищен: 2965 → 1625 символов
- USER.md почищен: 2427 → 1311 символов
- Создан процесс: любое изменение → обновить досье