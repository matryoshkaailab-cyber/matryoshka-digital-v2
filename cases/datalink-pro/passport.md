# DATALINK PRO — Технический Паспорт

**Статус:** Продакшен ✅  
**Обновлён:** 2026-05-04

## Суть
Коммерческий VPN сервис для клиентов в РФ. Продажа через Telegram бот.

## Контакты
- Бот: @datalink_pro_bot
- Домен: xn----7sbaowmfrljlq.xn--p1ai (даталинк-про.рф)
- Telegram для связи: @sergeiborodi (приём платежей вручную)

## Тех Стек
- Протокол: VLESS + Reality + XTLS-Vision (порт 443)
- SNI: www.microsoft.com | fp: chrome | flow: xtls-rprx-vision
- UUID: 4ea33e69-8a88-4811-b1f7-e433b46b8f5a
- Сервер: 85.137.166.209 (Host-Telecom CZ)
- Xray конфиг: /usr/local/x-ui/bin/config.json
- Клиент РФ: v2rayNG (НЕ Hiddify — заблокирован)

## Файлы
- Бот: /opt/vpn_bot/bot.py
- Webhook: /opt/vpn_bot/webhook_server.py (port 8443)
- База: /opt/vpn_bot/users.db

## YooKassa
- Shop ID: 1313515
- Секрет: live_GyxzG0AJEt9UzL9UnETQU0z8jl1MdSibrxU1Ct1xBMg
- Webhook URL: https://vpn.xn----7sbaowmfrljlq.xn--p1ai:8443/webhook/yookassa

## Тарифы
- 300₽/мес
- 800₽/3мес
- 1500₽/6мес

## Важно
- x-ui ПЕРЕЗАПИСЫВАЕТ конфиг при рестарте — kill x-ui перед изменением
- При падении VPN — КРИТИЧНО

## Активные задачи
- [ ] Доработать дашборд экономики (rf_economy_premium.html — табы не работают)

## Последняя сессия
**2026-05-03 19:47** — делали дашборд экономики, табы не открывались
**2026-05-04 09:38** — настроили синхронизацию памяти, создали систему кейсов
