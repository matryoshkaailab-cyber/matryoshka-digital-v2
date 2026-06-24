# Кейс 1: VPN DATALINK — коммерческий VPN сервис

## Идентичность
- **Сервис:** DATALINK PRO (коммерческий VPN для клиентов в РФ)
- **Бот продаж:** @datalink_pro_bot
- **Bot Token:** в /opt/vpn_bot/.env
- **YooKassa Shop ID:** 1313515
- **Статус:** Продакшен (Xray 26.4.25, активные клиенты)

## Технический стек
- **Протокол:** VLESS + Reality + XTLS-Vision (порт 443)
- **Сервер:** 85.137.166.209 (Host-Telecom CZ)
- **Домен:** xn----7sbaowmfrljlq.xn--p1ai
- **Webhook URL:** https://vpn.xn----7sbaowmfrljlq.xn--p1ai:8443/webhook/yookassa
- **Конфиг:** /usr/local/x-ui/bin/config.json

## Клиенты
**Текущий список (8 UUID):**
1. legion@reality (UUID 13a935c8-...)
2. oleg@reality (26299c78-...)
3. oleg-pc@reality (c70ff0ad-...)
4. tasya@reality (1ddb06ef-...)
5. sergey@reality (38b9aa97-...)
6. natalya@reality (c7712d93-...)
7. nikolay@reality (87834aa5-...)
8. leonid@reality (fac6d543-...)

**Все:** flow=xtls-rprx-vision

## Тарифы
- 300 ₽/мес
- 800 ₽/3 мес
- 1500 ₽/6 мес

## Процедура подключения
1. Клиент пишет @datalink_pro_bot
2. Бот генерирует trial (3 дня)
3. После оплаты через YooKassa → webhook → бот активирует подписку
4. Клиент получает VLESS-ссылку + инструкцию v2rayNG

## Текущая загрузка
- Xray процессы: PID 98386, 98391 (с 8 июня)
- Активных подключений: 79 (по состоянию на 15.06.2026)

## Известные особенности
- x-ui ПЕРЕЗАПИСЫВАЕТ конфиг при рестарте — kill x-ui перед изменением
- webhook_server.py обновляет trial_used=2 и trial_expires
- Hiddify НЕ работает в РФ — рекомендовать v2rayNG
