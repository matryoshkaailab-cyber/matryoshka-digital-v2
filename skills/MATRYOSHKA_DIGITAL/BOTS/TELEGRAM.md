# Telegram Боты — управление

## Активные боты

### DATALINK PRO Bot
```
@username: @datalink_pro_bot
Token: 8349948703:AAFybtShN5Q6LlVM8nzUbEzTvQK1VrgAc5I
Версия на сервере: v12 (генерирует AmneziaWG .conf)
Версия локальная: v13
Функция: выдача VPN конфигов, оплата через ЮKassa
```

## Быстрые команды бота (диагностика)
```bash
# Проверить работает ли
ssh vpn-serger "ps aux | grep datalink"

# Логи
ssh vpn-serger "tail -100 /tmp/datalink_v12.log"

# Рестарт
ssh vpn-serger "pkill -f datalink_pro_bot && nohup python3 /root/datalink_pro_bot_v12.py &"
```

## Другие боты в проекте
```
vpn_business/bot.py        — VPN бизнес (x-ui)
alex_bot.py               — бот Алексы
datalink_pro_bot_v*.py    — версии DATALINK PRO
```

## Файлы ботов на сервере
```
/root/datalink_pro_bot_v12.py  — основной
/root/datalink_bot.db           — база бота
```

## Если бот не отвечает
1. Проверить `ps aux | grep datalink`
2. Проверить логи `tail -100 /tmp/datalink_v12.log`
3. Проверить Telegram token (не истёк ли)
4. Проверить интернет на сервере
