# 🪆 ALINA — RUNBOOK (оперативные инструкции)

**Версия:** 1.0 (17.06.2026)
**Для кого:** HERMES, Аликс, Олег

---

## 🚨 АВАРИИ (что делать)

### Сценарий 1: Бот не отвечает в Telegram

**Симптомы:** Николай пишет — тишина

**Проверить:**
```bash
systemctl status alina-gateway
curl -s http://localhost:8470/health
```

**Если gateway inactive:**
```bash
systemctl restart alina-gateway
# Подождать 15 сек
curl -s http://localhost:8470/health
```

**Если gateway crashed в цикле:**
```bash
journalctl -u alina-gateway -n 50
# Смотрим ошибку, исправляем, рестарт
systemctl restart alina-gateway
```

**Если watchdog не помог:**
```bash
bash /root/.hermes/profiles/alina/cron/watchdog.sh
# Проверить через 10 сек
systemctl is-active alina-gateway
```

---

### Сценарий 2: HTTP API :8470 не отвечает

**Симптомы:** HERMES не может достучаться до Алины

**Проверить:**
```bash
curl -s http://localhost:8470/health
```

**Если пустой/timeout:**
```bash
systemctl restart alina-server
sleep 5
curl -s http://localhost:8470/health
```

**Если падает снова:**
```bash
journalctl -u alina-server -n 30
# Смотрим Python traceback
# Частая причина: config error
python3.12 -c "import yaml; yaml.safe_load(open('/root/.hermes/profiles/alina/config.yaml'))"
```

---

### Сценарий 3: Модель не отвечает (MiniMax-M3)

**Симптомы:** HTTP API возвращает ok=false, время > 30 сек

**Проверить MiniMax-M3:**
```bash
curl -s -X POST https://api.minimax.io/v1/chat/completions \
  -H "Authorization: Bearer $(grep MINIMAX_API_KEY /root/.hermes/profiles/alina/.env | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M3","messages":[{"role":"user","content":"ping"}]}' | head -c 200
```

**Если MiniMax упал — fallback автоматически:**
- M2.7 → Gemini Flash → Claude Haiku → Qwen local
- Если все 5 упали → возвращаем `ok=false`, **HERMES получает ошибку**

**Если нужен ручной fallback:**
```bash
# Через HTTP API (можно указать модель):
curl -s -X POST http://localhost:8470/chat \
  -H "Content-Type: application/json" \
  -u alina:<UUID> \
  -d '{"message":"...","model":"gemini-flash"}'
```

---

### Сценарий 4: Много лишних skills (после рестарта)

**Симптомы:** `ls /root/.hermes/profiles/alina/skills/` показывает > 10 папок

**Причина:** Gateway auto-discovery восстанавливает категории при старте

**Фикс:**
```bash
systemctl start alina-skills-cleanup.service
# Или руками:
bash /root/matryoshka/cases/nikolay/alina_skills_cleanup.sh
```

**Проверить что сработало:**
```bash
ls /root/.hermes/profiles/alina/skills/ | wc -l
# Должно быть ≤ 8
```

---

### Сценарий 5: Telegram бот "Forbidden"

**Симптомы:** Gateway лог: `Forbidden: the bot can't send messages to the bot`

**Причина:** `TELEGRAM_HOME_CHANNEL` = id самого бота (7734670302) вместо человека

**Фикс:**
```bash
# Проверить .env
grep HOME_CHANNEL /root/.hermes/profiles/alina/.env
# Должно быть 146881168 (Николай) или 1951845052 (Олег)
sed -i 's/TELEGRAM_HOME_CHANNEL=7734670302/TELEGRAM_HOME_CHANNEL=146881168/' \
  /root/.hermes/profiles/alina/.env
systemctl restart alina-gateway
```

---

### Сценарий 6: Avito парсер 404

**Симптомы:** `/var/log/alina_avito.log` показывает `Apify error: HTTP Error 404`

**Причина:** Actor ID `epctex/avito-scraper` не существует или заблокирован

**Фикс:**
1. Проверить Apify UI: https://console.apify.com/actors
2. Найти рабочий Avito actor
3. Обновить `actor_id` в `/root/.hermes/profiles/alina/cron/avito_monitor.py`

**Workaround (пока не починен):** Алина работает, но без парсинга лотов.

---

## 🔧 ОБСЛУЖИВАНИЕ

### Ежедневно (автоматически)

| Cron | Что делает |
|------|-----------|
| 02:00 | `backup.py` — бэкап на Яндекс.Диск |
| 03:00 | `kb_sync.py` — обновление базы знаний |
| 09:00 / 15:00 / 21:00 | `avito_monitor.py` — парсинг Авито |
| 21:00 | `finance_daily.py` — daily report → Telegram |
| Каждые 2 мин | `watchdog.sh` + `bridge_to_hermes.py` |
| Каждые 5 мин | `alina_status.sh` — JSON для HERMES |

### Еженедельно (вручную)

| День | Задача |
|------|--------|
| Понедельник 09:00 | `weekly_plan.py` — план на неделю |
| Воскресенье | Проверить логи: `tail -100 /var/log/alina_*.log` |

### Ежемесячно (вручную)

- Проверить VPS диск: `df -h`
- Проверить RAM: `free -m`
- Проверить Яндекс.Диск: достаточно ли места для бэкапов
- Обновить skills если есть новые

---

## 🛠 КОМАНДЫ (шпаргалка)

### Управление сервисами

```bash
# Статус
systemctl status alina-gateway
systemctl status alina-server
systemctl status alina-skills-loop

# Рестарт
systemctl restart alina-gateway
systemctl restart alina-server

# Логи (live)
journalctl -u alina-gateway -f
journalctl -u alina-server -f
tail -f /var/log/alina-gateway.log
tail -f /var/log/alina_server.log

# Остановить (на время ТО)
systemctl stop alina-gateway
systemctl stop alina-server
```

### Проверка работоспособности

```bash
# 1. Health
curl -s http://localhost:8470/health

# 2. Чат
curl -s -X POST http://localhost:8470/chat \
  -H "Content-Type: application/json" \
  -u alina:$(grep ALINA_API_UUID /root/.hermes/profiles/alina/.env | cut -d= -f2) \
  -d '{"message":"ping"}'

# 3. Telegram (через bot API)
TOKEN=$(grep TELEGRAM_BOT_TOKEN /root/.hermes/profiles/alina/.env | cut -d= -f2)
curl -s "https://api.telegram.org/bot$TOKEN/getMe"

# 4. Skills (должно быть 7-8)
ls /root/.hermes/profiles/alina/skills/ | wc -l

# 5. Cron (должно быть 9 алинских)
ls /etc/cron.d/ | grep alina
```

### Ручной запуск cron-скриптов

```bash
# Парсинг Авито
python3.12 /root/.hermes/profiles/alina/cron/avito_monitor.py

# Финансы
python3.12 /root/.hermes/profiles/alina/cron/finance_daily.py

# План
python3.12 /root/.hermes/profiles/alina/cron/weekly_plan.py

# Бэкап
python3.12 /root/.hermes/profiles/alina/cron/backup.py

# Мост
python3.12 /root/.hermes/profiles/alina/cron/bridge_to_hermes.py

# Статус
bash /root/.hermes/profiles/alina/cron/alina_status.sh

# Watchdog
bash /root/.hermes/profiles/alina/cron/watchdog.sh
bash /root/.hermes/profiles/alina/cron/watchdog_server.sh
```

---

## 📊 МОНИТОРИНГ (от HERMES)

Каждые 5 мин `/root/matryoshka/cron/alina_monitor.py` проверяет:

```bash
# Читает alina_status.json
cat /root/matryoshka/alina_tasks/alina_status.json
```

Если что-то не так — алерт в `HERMES_ALERTS.log`.

**Поля мониторинга:**
- `gateway` (active/inactive)
- `server` (active/inactive)
- `api` (JSON от /health)
- `cron[]` (список cron-ов с статусом)
- `alina_tasks_count` (количество задач от HERMES)

---

## 🔄 ОБНОВЛЕНИЕ (deployment)

### Обновить код alina_server.py

```bash
# 1. Редактируем
nano /root/matryoshka/alina/alina_server.py

# 2. Валидация
python3.12 -c "import ast; ast.parse(open('/root/matryoshka/alina/alina_server.py').read())"

# 3. Рестарт
systemctl restart alina-server
sleep 3

# 4. Тест
curl -s http://localhost:8470/health
```

### Обновить SOUL.md (тон Алины)

```bash
# 1. Редактируем
nano /root/.hermes/profiles/alina/SOUL.md

# 2. Рестарт gateway
systemctl restart alina-gateway
sleep 5
```

### Обновить skills (добавить новый)

```bash
# 1. Создаём symlink
ln -s /root/.hermes/profiles/hermes-cli/skills/matryoshka/НОВЫЙ-СКИЛЛ \
      /root/.hermes/profiles/alina/skills/НОВЫЙ-СКИЛЛ

# 2. Добавляем в whitelist cleanup
nano /root/matryoshka/cases/nikolay/alina_skills_cleanup.sh
# В KEEP добавить "НОВЫЙ-СКИЛЛ"

# 3. Рестарт
systemctl restart alina-gateway
```

---

## 📞 КОНТАКТЫ

| Роль | Telegram | ID |
|------|----------|-----|
| Директор (Олег) | @oleglab22 | 1951845052 |
| Пользователь (Николай) | @VarnakovNikolai | 146881168 |
| HERMES (дирижёр) | @oleg_industry_bot | — |
| Бот Алины | @NikolaAlinaBot | 7734670302 |

---

## 📝 CHANGELOG

### 17.06.2026 (v2.0)
- **Cleanup:** 45 → 7 skills
- **Toolsets:** 12 → 10 (убраны delegation, browser, cronjob)
- **HTTP API:** ThreadingHTTPServer (теперь параллельный)
- **Fix:** HOME_CHANNEL = id Николая (не бота)
- **Fix:** qwen-local: model = qwen3.7-plus (не max)
- **Fix:** SOUL.md загружается как default system prompt
- **Loop watchdog:** чистит лишние skills каждые 30 сек
- **Полный тест-драйв:** smoke, stress, нагрузка, fallback, watchdog
