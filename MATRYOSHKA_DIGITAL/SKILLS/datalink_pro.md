# SKILL: DATALINK PRO — Контекстный якорь

## Триггер
Используй этот скилл когда речь идёт о:
- DATALINK PRO
- VPN боте / @datalink_pro_bot
- Сервере 85.137.166.209
- AmneziaWG / awg0
- Пользователях: Наталья, Олег, Сергей (VPN контекст)
- Боте v11 / v12 / datalink_pro_bot

---

## ПРАВИЛО №1 — ЕДИНСТВЕННЫЙ ИСТОЧНИК ИСТИНЫ

```
C:\matryoshka\DATALINK_PRO_АНАЛИЗ\
```

**При любом вопросе по DATALINK PRO:**
1. Сначала читай `МАСТЕР_АНАЛИЗ_13.04.2026.md` из этой папки
2. Не опирайся на данные из других папок проекта
3. Не придумывай конфиги — только те что есть в `КОНФИГИ\`
4. SSH на сервер только для ПРОВЕРКИ, не для угадывания

---

## СТРУКТУРА ПАПКИ

```
DATALINK_PRO_АНАЛИЗ/
├── МАСТЕР_АНАЛИЗ_13.04.2026.md    ← ГЛАВНЫЙ ДОКУМЕНТ (читать первым!)
├── 00_ПОЛНАЯ_КАРТИНА_2_НЕДЕЛИ_АДА.md
├── КОНФИГИ/
│   ├── sergey_clean.conf           ← Сергей (новый, рабочий)
│   └── oleg_phone_keepalive10.conf ← Олег мобильный (keepalive=10)
├── БОТ/
│   └── datalink_pro_bot_v11.py    ← СТАРЫЙ (для справки)
├── СЕРВЕР/
│   └── SERVER_CONFIG.md
├── ХРОНОЛОГИЯ/
│   └── ПОЛНЫЙ_АНАЛИЗ_ПРОВАЛА_11.04.2026.md
└── ПОЛЬЗОВАТЕЛИ/
```

---

## КЛЮЧЕВЫЕ ФАКТЫ (выучить наизусть)

```yaml
Сервер:     85.137.166.209 (Чехия, SmartApe)
SSH-ключ:   C:\lab\vpn_matryoshka_key
SSH-alias:  vpn-serger

Протокол:   AmneziaWG (НЕ VLESS! НЕ Docker!)
Порт:       41234/UDP
Интерфейс: awg0 (нативный, НЕ Docker)

Бот:        v12 (текущий, генерирует .conf)
            /root/datalink_pro_bot_v12.py
Токен:      8349948703:AAFybtShN5Q6LlVM8nzUbEzTvQK1VrgAc5I

Сервер PubKey: r1H9WNYCogOjf/x+3eoo2OGhN6Qnt8LlhQc721OlsHM=
VPN подсеть:   10.9.9.0/24
Бот IP диапазон: 10.9.9.100–250

ЮKassa:     Shop 1313515 (БОЕВОЙ)
Тарифы:     500₽ / 1000₽ / 2000₽
```

---

## СТАТУС ПОЛЬЗОВАТЕЛЕЙ (13.04.2026)

| Пользователь | WiFi | Мобильный | Конфиг | Проблема |
|---|---|---|---|---|
| Наталья | ✅ | ✅ | NatalyaChut.conf | — |
| Олег | ✅ | ❌→⚙️ | oleg.conf / oleg_phone.conf | CGNAT Билайн |
| Сергей | ❌ | ❌ | sergey_clean.conf (новый) | Неверный порт/приложение |
| Тася | ✅ | — | tasya.conf | — |

---

## ДИАГНОСТИКА — СТАНДАРТНЫЕ КОМАНДЫ

```bash
# Все пиры
ssh vpn-serger "awg show awg0"

# Конкретный пир по имени
ssh vpn-serger "awg show awg0 | grep -A5 'ib5Iq'"  # Сергей
ssh vpn-serger "awg show awg0 | grep -A5 'm8qzI'"  # Олег мобильный
ssh vpn-serger "awg show awg0 | grep -A5 'MqZIe'"  # Олег WiFi

# Лог бота
ssh vpn-serger "tail -50 /tmp/datalink_v12.log"

# Файлы конфигов
ssh vpn-serger "ls -la /root/awg/*.conf"
```

---

## ЗАПРЕЩЕНО

- ❌ Использовать Docker для VPN (wireguard-go не поддерживает BLEICH)
- ❌ Генерировать VLESS .vpnuri (не работает через Nginx stream)
- ❌ Порт 443 для AmneziaWG (там Nginx TCP, не UDP)
- ❌ PersistentKeepalive > 15 для пользователей с CGNAT
- ❌ Менять BLEICH параметры на сервере без бэкапа

---

## ОБНОВЛЕНИЕ ДОКУМЕНТА

После каждой диагностической сессии обновлять:
`C:\matryoshka\DATALINK_PRO_АНАЛИЗ\МАСТЕР_АНАЛИЗ_13.04.2026.md`

Создавать новый файл с датой когда изменения значительные.
