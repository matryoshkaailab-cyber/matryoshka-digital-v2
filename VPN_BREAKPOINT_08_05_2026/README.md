# DATALINK PRO VPN — Рабочий бэкап от 08.05.2026 00:53

## Статус: ПРОВЕРЕНО РАБОТАЕТ ✅

## Версии
- Xray: 26.4.25 (go1.26.2 linux/amd64)
- Дата бэкапа: 08.05.2026
- VPS: 85.137.166.209

## VLESS ссылка (РАБОЧАЯ)
```
vless://28625ddc-ce9b-4086-b4b8-9a77b9a448ec@85.137.166.209:443?encryption=none&flow=xtls-rprx-vision&type=tcp&security=reality&sni=www.microsoft.com&fp=chrome&pbk=XyQdNYCSG7b3qzBWMiCPtWILI6OhhcOvLzzcMIAQTWs&sid=4818db014702038b#DATALINK_PRO
```

## Ручные параметры
- UUID: 28625ddc-ce9b-4086-b4b8-9a77b9a448ec
- PrivateKey: UJAUyqjT2CvAmsthrC3y46m0VATjYF8SkXVEBRdvIGE
- PublicKey: XyQdNYCSG7b3qzBWMiCPtWILI6OhhcOvLzzcMIAQTWs
- SNI: www.microsoft.com
- Flow: xtls-rprx-vision
- Short ID: 4818db014702038b
- Port: 443

## АРХИТЕКТУРА
- Xray запущен ВРУЧНУЮ (НЕ через x-ui)
- x-ui ОСТАНОВЛЕН и ОТКЛЮЧЁН
- Конфиг: /usr/local/x-ui/bin/config.json
- Бинарник: /usr/local/x-ui/bin/xray-linux-amd64
- Логи: /var/log/xray/access.log, error.log

## ВАЖНО
- НЕ использовать x-ui restart — он ПЕРЕЗАПИСЫВАЕТ config.json
- Если xray упал — запускать вручную:
  ```
  /usr/local/x-ui/bin/xray-linux-amd64 run -config /usr/local/x-ui/bin/config.json
  ```

## ПРОБЛЕМА С МОБИЛЬНЫМИ
- xtls-rprx-vision НЕ работает на v2rayNG Android
- Для мобильных нужен отдельный inbound с пустым flow ("")
- Решение: добавить второй inbound на порт 2053 с flow: ""
