---
created: 2026-05-12
updated: 2026-05-12
tags: [datalink, vpn, project]
---

# DATALINK PRO — VPN Сервис

**Статус:** Продакшен ✅
**Обновлён:** 2026-05-04

---

## Суть
Коммерческий VPN сервис для клиентов в РФ. Продажа через Telegram бот.

---

## Контакты
- **Бот:** @datalink_pro_bot
- **Домен:** xn----7sbaowmfrljlq.xn--p1ai (даталинк-про.рф)
- **Telegram:** @sergeiborodi (приём платежей вручную)

---

## Тех Стек
- **Протокол:** VLESS + Reality + XTLS-Vision (порт 443)
- **SNI:** www.microsoft.com | fp: chrome | flow: xtls-rprx-vision
- **UUID:** 4ea33e69-8a88-4811-b1f7-e433b46b8f5a
- **Сервер:** 85.137.166.209 (Host-Telecom CZ)
- **Клиент:** v2rayNG (НЕ Hiddify — заблокирован)

---

## Файлы
- **Бот:** /opt/vpn_bot/bot.py
- **Webhook:** /opt/vpn_bot/webhook_server.py (port 8443)
- **База:** /opt/vpn_bot/users.db

---

## YooKassa
- **Shop ID:** 1313515
- **Секрет:** live_GyxzG0AJEt9UzL9UnETQU0z8jl1MdSibrxU1Ct1xBMg

---

## Тарифы
| Период | Цена |
|--------|------|
| 1 месяц | 300₽ |
| 3 месяца | 800₽ |
| 6 месяцев | 1500₽ |

---

## ⚠️ Важно
- x-ui ПЕРЕЗАПИСЫВАЕТ конфиг при рестарте
- При падении VPN — КРИТИЧНО

---

## Активные задачи
- [ ] Доработать дашборд экономики
modified $(Get-Date -Format HH:mm:ss)
