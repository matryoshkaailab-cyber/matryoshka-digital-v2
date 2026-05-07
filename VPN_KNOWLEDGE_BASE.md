# DATALINK PRO — БАЗА ЗНАНИЙ VPN
## Борьба с блокировками ВПН в РФ

**Начало ведения:** 30.04.2026  
**Сервер:** 85.137.166.209 (SmartApe, Чехия, Ubuntu 24.04)  
**Протокол:** VLESS + Reality + XTLS (оптимизированный)

---

## СОДЕРЖАНИЕ

1. [Текущий конфиг](#1-текущий-конфиг)
2. [История изменений](#2-история-изменений)
3. [Диагностика и проблемы](#3-диагностика-и-проблемы)
4. [Что работает / не работает](#4-что-работает--не-работает)
5. [Уроки и выводы](#5-уроки-и-выводы)
6. [Планы на будущее](#6-планы-на-будущее)

---

## 1. ТЕКУЩИЙ КОНФИГ

### Сервер
```
IP:           85.137.166.209
Ports:        443 (Reality), 2053 (Reality), 12345 (xHTTP)
Protocol:     VLESS + Reality (без XTLS Vision!)
UUID:         4ea33e69-8a88-4811-b1f7-e433b46b8f5a
SNI:          www.microsoft.com (временно)
Fingerprint:  chrome
Private Key:  iBv1cGLOFYy91WMVnGQVzLVoqXfQ0k_x3JwKdkkzUnU
Public Key:   eiA5hKeJIfikI7zPw4HxZBqyWg3IPzveATsokrK3UCo
Short ID:     42ba5a090b2bdeaa
```

### VLESS Links
```
Порты: 443, 2053
UUID: 4ea33e69-8a88-4811-b1f7-e433b46b8f5a
SNI: www.microsoft.com
Fingerprint: chrome

vless://4ea33e69-8a88-4811-b1f7-e433b46b8f5a@85.137.166.209:443?encryption=none&flow=&type=tcp&security=reality&sni=www.microsoft.com&fp=chrome&pbk=eiA5hKeJIfikI7zPw4HxZBqyWg3IPzveATsokrK3UCo&sid=42ba5a090b2bdeaa&allowlnsecure=false#DATALINK_PRO_443
```

### Routing (последнее обновление 30.04.2026)
```json
{
  "domainStrategy": "IPIfNonMatch",
  "rules": [
    // YouTube → proxy (ВСЕГДА через VPN!)
    { "domain": ["youtube.com","googlevideo.com","ytimg.com","gvt1.com","gvt2.com"], "outboundTag": "proxy" },
    // Instagram, TikTok, Twitter → proxy
    { "domain": ["instagram.com","tiktok.com","twitter.com","x.com"], "outboundTag": "proxy" },
    // Private IP → direct
    { "ip": ["geoip:private"], "outboundTag": "direct" },
    // RU сайты → direct (split tunneling)
    { "domain": ["geosite:ru"], "outboundTag": "direct" },
    // RU/BY/KZ IP → direct
    { "ip": ["geoip:ru","geoip:by","geoip:kz"], "outboundTag": "direct" },
    // Ads → blocked
    { "domain": ["geosite:category-ads-all"], "outboundTag": "blocked" },
    // Torrents → blocked
    { "protocol": ["bittorrent"], "outboundTag": "blocked" }
  ]
}
```

### Outbounds
```json
"outbounds": [
  { "tag": "proxy", "protocol": "freedom", "settings": {"domainStrategy": "UseIPv4"} },
  { "tag": "direct", "protocol": "freedom", "settings": {"domainStrategy": "UseIPv4"} },
  { "tag": "blocked", "protocol": "blackhole", "settings": {} }
]
```

---

## 2. ИСТОРИЯ ИЗМЕНЕНИЙЙ

### 30.04.2026 14:50 — ИСПРАВЛЕНА АРХИТЕКТУРА!

**Вернулся к правильной схеме:**
- nginx на 443 (frontend)
- Xray на 127.0.0.1:10443 (backend)
- Cloudflare CDN работает!

**Новая проблема:** x-ui panel перезаписывала конфиг! Пришлось остановить x-ui.

**Финальный конфиг:**
- Xray PID: 210672
- Routing: YouTube, Instagram, TikTok → proxy
- geosite:ru → geoip:ru (geosite.dat не содержит RU)

**Архитектура:**
```
Cloudflare/Прямой IP → nginx:443 → Xray:10443 (Reality)
Мобильные → Xray:2053 (напрямую)
```

**Статус:** ✅ Работает (14:50)

**Тест:** Олег подключился в 14:50 — работает.

**Ждём тест после 21:00 — основная проверка на ТСПУ.

---

### 30.04.2026 — XTLS Vision removed

**Проблема:** v2rayNG на Android не подключается.

**Причина:** XTLS Vision flow (`xtls-rprx-vision`) несовместим с v2rayNG mobile.

**Решение:** Убран flow полностью (пустая строка `flow: ""`).

**Изменения:**
- Все inbounds: `"flow": ""` вместо `"flow": "xtls-rprx-vision"`
- UUID оставлен тот же: `4ea33e69-8a88-4811-b1f7-e433b46b8f5a`

**Статус:** ✅ Работает, Telegram подключается.

---

### 29.04.2026 — Xray Reality setup

**Начальная настройка.** Обнаружен конфликт nginx + Xray на порту 443.

**Решение:** Xray запущен напрямую на 443 без nginx.

**Конфиг:** `/usr/local/x-ui/bin/config.json` (x-ui managed)

---

## 3. ДИАГНОСТИКА И ПРОБЛЕМЫ

### Проблема: YouTube не работает

| Аспект | Детали |
|--------|--------|
| **Когда обнаружено** | 29.04.2026 |
| **Симптомы** | Telegram работает, YouTube нет |
| **Причина** | geoip:ru routing перехватывает YouTube CDN |
| **Решение** | Добавлено правило youtube.com → proxy |
| **Статус** | ⚠️ Требует тестирования |

### Проблема: Мобильный падает после 21:00

| Аспект | Детали |
|--------|--------|
| **Когда обнаружено** | 29.04.2026 |
| **Симптомы** | VPN работает днём, падает после 21:00 |
| **Причина** | ТСПУ вечером переключается в агрессивный режим |
| **Провайдеры** | Билайн, МТС — подтверждено на форумах |
| **Решение** | Смена SNI + xHTTP через Cloudflare (план) |
| **Статус** | ⚠️ Требует решения |

### Проблема: SNI www.microsoft.com

| Аспект | Детали |
|--------|--------|
| **Риск** | Microsoft.com — один из самых наблюдаемых доменов ТСПУ |
| **Проверка IP+SNI** | Активно используется на мобильных операторах |
| **Рекомендация** | Сменить на www.speedtest.net или www.cloudflare.com |
| **Статус** | ⏳ Запланировано |

### Проблема: Xray без Nginx

| Аспект | Детали |
|--------|--------|
| **Риск** | Уязвим к активному зондированию ТСПУ |
| **Решение** | Вернуть Nginx как reverse proxy |
| **Статус** | ⏳ Запланировано |

---

## 4. ЧТО РАБОТАЕТ / НЕ РАБОТАЕТ

### ✅ Работает
- Telegram (всегда)
- Подключение к серверу
- VLESS Reality на порту 443
- Split tunneling (RU сайты direct)
- Мобильный интернет днём

### ❌ Не работает / Проблемы
- YouTube (частично — надеемся что routing fix помог)
- Мобильный после 21:00 (ТСПУ)
- SNI microsoft.com (слишком наблюдаемый)

### ❓ Не проверено
- Instagram
- TikTok
- Twitter/X

---

## 5. УРОКИ И ВЫВОДЫ

### Ключевые уроки

1. **XTLS Vision несовместим с v2rayNG mobile**
   - Всегда использовать пустой flow `""` для мобильных клиентов

2. **Routing order matters!**
   - Правила применяются сверху вниз
   - YouTube должен идти через proxy ДО geoip:ru

3. **SNI microsoft.com — плохой выбор**
   - ТСПУ мониторит особо внимательно
   - Лучше speedtest.net, cloudflare.com, akamai.com

4. **geoip:ru в routing — быть осторожным**
   - Может ловить CDN заблокированных сервисов
   - Всегда добавлять exceptions для нужных доменов

5. **Nginx перед Xray — защита от зондирования**
   - Без nginx сервер отвечает как Xray, не как HTTPS
   - ТСПУ активнее детектит такие серверы

### Технические детали для отладки

```
# Проверить конфиг Xray
/usr/local/x-ui/bin/xray-linux-amd64 run -test -config /usr/local/x-ui/bin/config.json

# Посмотреть логи
tail -f /var/log/xray/error.log

# Перезапустить Xray
kill -HUP <pid>

# Проверить порты
ss -tlnp | grep -E "443|2053"
```

---

## 6. ПЛАНЫ НА БУДУЩЕЕ

### Приоритет 1 (сегодня)
- [ ] Тестировать YouTube после routing fix
- [ ] Сменить SNI с microsoft.com на speedtest.net
- [ ] Перегенерировать ключи Reality

### Приоритет 2 (эта неделя)
- [ ] Вернуть Nginx как reverse proxy
- [ ] Закрыть порт 2053 (оставить только 443)
- [ ] Протестировать вечером после 21:00

### Приоритет 3 (следующая неделя)
- [ ] Добавить xHTTP inbound через Cloudflare CDN
- [ ] Подготовить запасной VPS (Hetzner/Contabo)
- [ ] Документировать результаты вечернего тестирования

---

## КОМАНДЫ БЫСТРОГО ДОСТУПА

```bash
# Статус Xray
ps aux | grep xray | grep -v grep

# Порты
ss -tlnp | grep -E "443|2053"

# Логи
tail -20 /var/log/xray/error.log

# Тест конфига
/usr/local/x-ui/bin/xray-linux-amd64 run -test -config /usr/local/x-ui/bin/config.json

# Перезапуск
kill -HUP $(ps aux | grep 'xray-linux-amd64' | grep -v grep | awk '{print $2}')
```

---

## VERSION INFO

| Версия | Дата | Автор | Изменения |
|--------|------|-------|-----------|
| 1.0 | 30.04.2026 | Hermes | Начальная версия |

---

*DATALINK PRO — База знаний VPN*  
*Обновляется после каждого изменения*
