# DATALINK PRO — ПОЛНЫЙ АНАЛИЗ
## Сервер: 85.137.166.209 | Дата: 08.05.2026 11:50

---

## 1. КОНФИГУРАЦИЯ СЕРВЕРА

### Xray (v26.4.25)
- Файл: `/usr/local/x-ui/bin/config.json`
- Порты: 443, 2053
- Протокол: VLESS Reality
- SNI: www.speedtest.net

### Ключи Reality (действующие)
```
PrivateKey: UKgNujpwM7vC_jONfuV-hn4YL_6dziNUTz6_Ey7QzVo
PublicKey/PBK: KD3vWGJ-3ikGgncM405UpfGOLMVofZPiaAUU7ZHD6S8
UUID: 28625ddc-ce9b-4086-b4b8-9a77b9a448ec
ShortID: 53f80cad0ac6a04b
```

### Конфиг inbounds
- Порт 443: flow=xtls-rprx-vision (для ПК)
- Порт 2053: flow=empty (для мобильных)

---

## 2. ИСТОРИЯ РАБОТОСПОСОБНОСТИ

### ПОРТ 443
| Дата | Время | Статус | Примечания |
|------|-------|--------|-----------|
| 07.05 | 19:44-19:48 | ✅ РАБОТАЛ |accepted трафик YouTube, Google |
| 08.05 | 00:00-01:19 | ❌ ПОЛНЫЙ ОТКАЗ | connection reset by peer |
| 08.05 | 10-11 | ❌ НЕТ ЗАПИСЕЙ | Не работает вообще |

### ПОРТ 2053
| Дата | Время | Статус | Примечания |
|------|-------|--------|-----------|
| 08.05 | 11:34-11:34 | ✅ РАБОТАЛ | accepted google, youtube, dns |
| 08.05 | 11:13-11:13 | ❌ failed to read client hello | Мобильный |

---

## 3. ЛОГИ — ПОРТ 443 (ИСТОРИЯ)

### 07.05.2026 19:44-19:48 — РАБОТАЛ ✅
```
from 95.25.135.49:26683 accepted tcp:relay-67a9a5c4.net.anydesk.com:443 [reality-443 >> direct]
from 95.25.135.49:25449 accepted tcp:relay-b7f36689.net.anydesk.com:443 [reality-443 >> direct]
from 95.25.135.49:25420 accepted tcp:www.youtube.com:443 [reality-443 >> direct]
from 95.25.135.49:26181 accepted tcp:i.ytimg.com:443 [reality-443 >> direct]
from 95.25.135.49:26484 accepted tcp:149.154.167.41:443 [reality-443 >> direct] (Telegram)
from 95.25.135.49:26602 accepted tcp:accounts.google.com:443 [reality-443 >> direct]
from 95.25.135.49:25296 accepted tcp:www.google.com:443 [reality-443 >> direct]
```
**Вывод: Порт 443 РАБОТАЛ 07.05 с того же IP 95.25.135.49**

### 08.05.2026 00:00-01:19 — ПОЛНЫЙ ОТКАЗ ❌
```
[Info] app/proxyman/outbound: failed to process outbound traffic
> proxy/freedom: connection ends
> read tcp 85.137.166.209:443->95.25.135.49:26386: read: connection reset by peer
> write tcp 85.137.166.209:443->95.25.135.49:25250: write: broken pipe
> splice: connection reset by peer
```
**Сотни ошибок connection reset by peer**

### 08.05.2026 10-11 — НЕТ ЗАПИСЕЙ ВООБЩЕ
Нет попыток подключения на порт 443 с IP 95.25.135.49

---

## 4. ЛОГИ — ПОРТ 2053

### 08.05.2026 11:34 — РАБОТАЕТ ✅ (WiFi)
```
from 95.25.135.49:26326 accepted tcp:redirector.googlevideo.com:443 [inbound-2053-mobile -> direct]
from 95.25.135.49:25806 accepted tcp:s.youtube.com:443 [inbound-2053-mobile -> direct]
from 95.25.135.49:26620 accepted udp:8.8.8.8:53 [inbound-2053-mobile -> direct]
```

### 08.05.2026 11:13 — ОШИБКА ❌ (мобильный)
```
failed to read client hello
```

---

## 5. КЛЮЧЕВЫЕ ВЫВОДЫ

### Проблема 1: Порт 443 перестал работать
- 07.05 — работал ✅
- 08.05 00:00 — начались массовые connection reset
- 08.05 10-11 — вообще нет записей

**Возможные причины:**
1. ТСПУ начал блокировать порт 443
2. Изменились ключи/конфиг — старые клиенты не могут подключиться
3. Файл конфигурации был изменён

### Проблема 2: Порт 2053 работает только на WiFi
- WiFi: accepted ✅
- Мобильный: failed to read client hello ❌

**Причина: ТСПУ блокирует Reality на мобильном**

---

## 6. ХРОНОЛОГИЯ ДЕЙСТВИЙ

| Время | Действие | Результат |
|-------|----------|-----------|
| 07.05 19:44 | Порт 443 работал | ✅ VPN функционировал |
| 08.05 00:00 | Начались ошибки connection reset | ❌ |
| 08.05 02:00 | Создан breakpoint, SNI→speedtest.net | - |
| 08.05 10:26 | Обнаружен "server name mismatch" | Старые ссылки |
| 08.05 10:56 | Пересозданы ключи | Новые ключи |
| 08.05 11:08 | Синхронизирован бот | Ключи совпали |
| 08.05 11:13 | Порт 2053 — failed to read client hello | ❌ |
| 08.05 11:34 | Порт 2053 WiFi — accepted | ✅ |

---

## 7. ЧТО ТРЕБУЕТСЯ ДЛЯ РЕШЕНИЯ

### Вариант 1: Понять почему порт 443 не работает
- Проверить текущий конфиг xray
- Возможно вернуть старые работавшие ключи

### Вариант 2: xHTTP для мобильных
- Reality не работает через ТСПУ на мобильном
- Нужен xHTTP + Cloudflare

---

## 8. ФАЙЛЫ

- Xray config: `/usr/local/x-ui/bin/config.json`
- Bot: `/opt/vpn_bot/bot.py`
- Логи: `/var/log/xray/access.log`, `/var/log/xray/error.log`
- Breakpoint: `/root/matryoshka/VPN_BREAKPOINT_08_05_2026/`
- Отчёты: `/root/matryoshka/cases/datalink-pro/docs/`