# Alina watchlist — что слежу и сообщаю когда станет критично

## Сервисы (systemd)
- [HIGH] alina-server.service упал — порт занят (Address already in use), watchdog не может поднять
- [HIGH] alina-gateway.service inactive

## Парсеры
- [MEDIUM] Apify (avito_monitor.py) — HTTP 404, скорее всего сменился actorId
- [MEDIUM] Fallback парсер (Yandex + DuckDuckGo) — 0 результатов, антибот

## Backup
- [LOW] backup.py не использует YANDEX_DISK_TOKEN (пишет local only), хотя токен живой

## Когда сообщать
- Сервис лёг >2 раз подряд без восстановления → сообщить
- Парсер не находит результаты 3+ дня подряд → сообщить
- Новые issues/PR в репо → сообщить (если настроены webhooks)
- Открытие новой ниши или товара в памяти → предложить создать issues
