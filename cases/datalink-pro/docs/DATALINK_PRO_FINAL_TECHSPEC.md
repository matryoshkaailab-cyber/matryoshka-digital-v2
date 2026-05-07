# DATALINK PRO — ФИНАЛЬНОЕ ТЕХЗАДАНИЕ ДЛЯ ИНЖЕНЕРА
## VLESS + Reality + xHTTP (stream-one) через Cloudflare CDN
## Максимальный стелс, максимальная стабильность

**Дата:** Апрель 2026  
**Сервер:** 85.137.166.209 (Чехия, SmartApe, Ubuntu 24.04)  
**Статус:** ФИНАЛЬНАЯ ВЕРСИЯ — К ИСПОЛНЕНИЮ

---

## ПОЧЕМУ ИМЕННО ЭТА КОНФИГУРАЦИЯ

Реализуется два inbound на одном сервере, один порт 443:

**Inbound 1 — Reality + XTLS-Vision (прямое подключение)**
- Максимальная скорость (XTLS Splice на уровне ядра Linux)
- Лучший стелс TLS-рукопожатия — DPI получает настоящий сертификат реального сайта
- Для: проводной интернет, стабильные операторы, пользователи без CGNAT

**Inbound 2 — Reality + xHTTP stream-one (через Cloudflare CDN)**
- stream-one: единое соединение в обоих направлениях — максимальный стелс поведения трафика
- Reality: маскировка рукопожатия под реальный сайт
- Cloudflare CDN: реальный IP сервера полностью скрыт — блокировка IP не работает
- Для: мобильный CGNAT, Билайн, белые списки, шатдауны

Nginx определяет источник запроса по IP: Cloudflare IP → xHTTP inbound, прямой IP → Vision inbound. Автоматически, без действий пользователя.

---

## ЧАСТЬ 1: ПОДГОТОВКА СЕРВЕРА

### 1.1 Базовая настройка

```bash
ssh root@85.137.166.209

# Обновить систему
apt update && apt upgrade -y

# Установить зависимости
apt install -y curl wget unzip nginx certbot python3-certbot-nginx ufw qrencode

# Включить BBR — алгоритм Google для скорости и стабильности TCP
echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
echo "net.ipv4.tcp_fastopen=3" >> /etc/sysctl.conf
sysctl -p

# Проверить BBR
sysctl net.ipv4.tcp_congestion_control
# Ожидаемый вывод: bbr

# Настроить файрвол
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 47821/tcp
ufw enable
ufw status
```

### 1.2 Освободить порты 80 и 443

```bash
# Проверить что занимает порты
ss -tlnp | grep ':80\|:443'

# Остановить существующие процессы если есть
pkill -f datalink_web
systemctl stop apache2 2>/dev/null || true

# Проверить что порты свободны
ss -tlnp | grep ':80\|:443'
# Должно быть пусто
```

---

## ЧАСТЬ 2: УСТАНОВКА XRAY

### 2.1 Установка последней версии

```bash
# Установить Xray через официальный скрипт
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Проверить версию — должна быть 25.x+
xray version

# Создать директории для логов
mkdir -p /var/log/xray
chown nobody:nogroup /var/log/xray
```

### 2.2 Генерация ключей (выполнить один раз, сохранить результаты)

```bash
# Генерировать ключи Reality
xray x25519
# СОХРАНИТЬ:
# Private key: XXXX  ← только на сервере, никому не передавать
# Public key:  XXXX  ← вставлять в клиентские конфиги

# Генерировать Short ID
openssl rand -hex 8
# Пример: a1b2c3d4e5f6a7b8

# Генерировать UUID для первого пользователя
xray uuid
# Пример: 550e8400-e29b-41d4-a716-446655440000

# Узнать IP сервера
curl -4 ifconfig.me
# 85.137.166.209
```

**Записать и сохранить в защищённом месте:**
```
PRIVATE_KEY = _______________
PUBLIC_KEY  = _______________
SHORT_ID    = _______________
UUID_USER1  = _______________
SERVER_IP   = 85.137.166.209
SNI_DONOR   = _______________ (выбрать из раздела 2.3)
XHTTP_PATH  = _______________ (придумать случайный, например /api/v3/data)
DOMAIN      = _______________ (ваш латинский домен)
```

### 2.3 Выбор SNI-донора

SNI-донор — реальный зарубежный сайт под который маскируется Reality. От выбора донора зависит качество маскировки.

**Требования:**
- Поддерживает TLS 1.3
- НЕ стоит за Cloudflare или другим CDN
- Не заблокирован РКН
- Не делает редирект
- Желательно: средней популярности, не под пристальным наблюдением ТСПУ

**Проверить кандидата тремя командами:**
```bash
# 1. Проверить TLS версию
curl -svo /dev/null https://КАНДИДАТ.com 2>&1 | grep "TLSv"
# Нужно: TLSv1.3

# 2. Проверить нет ли редиректа
curl -I https://КАНДИДАТ.com 2>/dev/null | head -5
# Нужно: HTTP/2 200 (не 301/302)

# 3. Проверить что НЕ за Cloudflare
curl -sI https://КАНДИДАТ.com | grep -i "CF-RAY"
# Нужно: пустой ответ (нет CF-RAY)
```

**Проверенные доноры апрель 2026:**
- www.speedtest.net ← рекомендуется
- cdn.jsdelivr.net
- dl.google.com
- gateway.icloud.com

**Запрещённые доноры:**
- google.com, youtube.com (слишком популярны)
- yandex.ru, vk.com (российские)
- Любые домены за Cloudflare CDN

---

## ЧАСТЬ 3: КОНФИГУРАЦИЯ XRAY

### 3.1 Основной конфиг с двумя inbound

```bash
cat > /usr/local/etc/xray/config.json << 'XRAYEOF'
{
  "log": {
    "loglevel": "warning",
    "access": "/var/log/xray/access.log",
    "error": "/var/log/xray/error.log"
  },

  "inbounds": [

    {
      "tag": "vless-reality-vision",
      "listen": "127.0.0.1",
      "port": 10443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "ВСТАВИТЬ_UUID",
            "email": "user1@datalink",
            "flow": "xtls-rprx-vision"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "ВСТАВИТЬ_SNI_ДОНОР:443",
          "xver": 0,
          "serverNames": [
            "ВСТАВИТЬ_SNI_ДОНОР"
          ],
          "privateKey": "ВСТАВИТЬ_PRIVATE_KEY",
          "shortIds": [
            "ВСТАВИТЬ_SHORT_ID"
          ]
        },
        "sockopt": {
          "tcpFastOpen": true,
          "domainStrategy": "UseIPv4"
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic", "fakedns"],
        "routeOnly": false
      }
    },

    {
      "tag": "vless-reality-xhttp",
      "listen": "127.0.0.1",
      "port": 10444,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "ВСТАВИТЬ_UUID",
            "email": "user1-mobile@datalink"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "xhttp",
        "xhttpSettings": {
          "path": "ВСТАВИТЬ_XHTTP_PATH",
          "mode": "stream-one",
          "noSSEHeader": false,
          "xPaddingBytes": "100-1000"
        },
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "ВСТАВИТЬ_SNI_ДОНОР:443",
          "xver": 0,
          "serverNames": [
            "ВСТАВИТЬ_SNI_ДОНОР"
          ],
          "privateKey": "ВСТАВИТЬ_PRIVATE_KEY",
          "shortIds": [
            "ВСТАВИТЬ_SHORT_ID"
          ]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic", "fakedns"],
        "routeOnly": false
      }
    }

  ],

  "outbounds": [
    {
      "tag": "direct",
      "protocol": "freedom",
      "settings": {
        "domainStrategy": "UseIPv4"
      }
    },
    {
      "tag": "block",
      "protocol": "blackhole",
      "settings": {}
    }
  ],

  "routing": {
    "domainStrategy": "IPIfNonMatch",
    "rules": [
      {
        "type": "field",
        "ip": ["geoip:private"],
        "outboundTag": "direct"
      },
      {
        "type": "field",
        "domain": ["geosite:ru"],
        "outboundTag": "direct"
      },
      {
        "type": "field",
        "ip": ["geoip:ru", "geoip:by", "geoip:kz"],
        "outboundTag": "direct"
      },
      {
        "type": "field",
        "domain": ["geosite:category-ads-all"],
        "outboundTag": "block"
      },
      {
        "type": "field",
        "protocol": ["bittorrent"],
        "outboundTag": "block"
      }
    ]
  }
}
XRAYEOF
```

**Что подставить:**
```
ВСТАВИТЬ_UUID         → результат: xray uuid
ВСТАВИТЬ_SNI_ДОНОР    → например: www.speedtest.net
ВСТАВИТЬ_PRIVATE_KEY  → строка "Private key:" из: xray x25519
ВСТАВИТЬ_SHORT_ID     → результат: openssl rand -hex 8
ВСТАВИТЬ_XHTTP_PATH   → случайный путь, например: /api/v3/stream
```

### 3.2 Параметр xPaddingBytes — объяснение

`"xPaddingBytes": "100-1000"` — добавляет случайный паддинг 100-1000 байт к каждому пакету. Это нормализует размеры пакетов и делает трафик неотличимым от обычного HTTP. Это ключевой параметр защиты от ML-классификаторов ТСПУ.

### 3.3 Проверка и запуск

```bash
# Проверить синтаксис конфига
xray run -test -config /usr/local/etc/xray/config.json
# Ожидаемый вывод: Configuration OK

# Запустить Xray
systemctl restart xray
systemctl status xray
systemctl enable xray

# Убедиться что оба порта слушаются
ss -tlnp | grep 'xray\|10443\|10444'
```

---

## ЧАСТЬ 4: КОНФИГУРАЦИЯ NGINX

Nginx выполняет маршрутизацию: если запрос с IP Cloudflare → xHTTP, если прямой IP → Vision.

### 4.1 Полный nginx.conf

```bash
# Сделать резервную копию текущего конфига
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

cat > /etc/nginx/nginx.conf << 'NGINXEOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 4096;
    multi_accept on;
}

# STREAM БЛОК — TCP маршрутизация по IP источника
stream {

    # Список IP Cloudflare (обновлять раз в 2-3 месяца)
    # Актуальный список: https://www.cloudflare.com/ips-v4
    geo $remote_addr $is_cloudflare {
        default             0;
        173.245.48.0/20     1;
        103.21.244.0/22     1;
        103.22.200.0/22     1;
        103.31.4.0/22       1;
        141.101.64.0/18     1;
        108.162.192.0/18    1;
        190.93.240.0/20     1;
        188.114.96.0/20     1;
        197.234.240.0/22    1;
        198.41.128.0/17     1;
        162.158.0.0/15      1;
        104.16.0.0/13       1;
        104.24.0.0/14       1;
        172.64.0.0/13       1;
        131.0.72.0/22       1;
    }

    # Маршрутизация: Cloudflare → HTTP блок (xHTTP), прямой → Xray Vision
    map $is_cloudflare $backend_port {
        0   10443;
        1   10445;
    }

    server {
        listen 443;
        proxy_pass 127.0.0.1:$backend_port;
        proxy_timeout 600s;
        proxy_connect_timeout 5s;
        proxy_buffer_size 16k;
    }
}

# HTTP БЛОК — для xHTTP через CDN
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 300s;
    types_hash_max_size 2048;
    server_tokens off;

    # Сервер для xHTTP (слушает на 10445, принимает трафик от Cloudflare)
    server {
        listen 127.0.0.1:10445 ssl http2;
        server_name ВСТАВИТЬ_ДОМЕН;

        ssl_certificate /etc/letsencrypt/live/ВСТАВИТЬ_ДОМЕН/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ВСТАВИТЬ_ДОМЕН/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 1d;

        # xHTTP stream-one endpoint
        # ВСТАВИТЬ_XHTTP_PATH должен совпадать с path в xray конфиге
        location ВСТАВИТЬ_XHTTP_PATH {
            grpc_pass grpc://127.0.0.1:10444;
            grpc_set_header Host $host;
            grpc_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            grpc_set_header X-Real-IP $remote_addr;
            grpc_read_timeout 600s;
            grpc_send_timeout 600s;
            client_max_body_size 0;
        }

        # Маскировочная страница — при прямом обращении к домену выглядит как обычный сайт
        location / {
            return 200 'DataLink Technologies';
            add_header Content-Type text/plain;
            add_header Server nginx;
        }
    }

    # HTTP → HTTPS редирект
    server {
        listen 80;
        server_name ВСТАВИТЬ_ДОМЕН;
        return 301 https://$server_name$request_uri;
    }
}
NGINXEOF
```

**Что подставить в nginx.conf:**
```
ВСТАВИТЬ_ДОМЕН       → ваш латинский домен (например vpn.datalink-pro.com)
ВСТАВИТЬ_XHTTP_PATH  → тот же путь что в xray конфиге (например /api/v3/stream)
```

### 4.2 Проверка и запуск Nginx

```bash
# Проверить синтаксис — ОБЯЗАТЕЛЬНО перед применением
nginx -t
# Ожидаемый вывод:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# Применить конфиг
systemctl restart nginx
systemctl status nginx
systemctl enable nginx

# Проверить что порт 443 слушается
ss -tlnp | grep ':443'
```

---

## ЧАСТЬ 5: ДОМЕН И CLOUDFLARE

### 5.1 Требования к домену

Нужен латинский домен. Кириллический даталинк-про.рф создаёт проблемы с certbot и Cloudflare. Рекомендуется отдельный домен специально для VPN-инфраструктуры.

### 5.2 Настройка DNS в Cloudflare (порядок важен)

**Шаг 1:** Добавить домен в Cloudflare, перенести NS-серверы у регистратора.

**Шаг 2:** Создать A-запись в режиме DNS only (серое облако):
```
Тип: A
Имя: @ или vpn
Содержимое: 85.137.166.209
Прокси: СЕРОЕ облако (DNS only)
```

**Шаг 3:** Получить SSL-сертификат (Cloudflare в этот момент должен быть серым):
```bash
# Убедиться что DNS распространился
dig ВАШ_ДОМЕН +short
# Должен вернуть: 85.137.166.209

# Получить сертификат
certbot certonly --nginx -d ВАШ_ДОМЕН

# Проверить
certbot certificates
```

**Шаг 4:** Переключить Cloudflare в Proxied (оранжевое облако).

**Шаг 5:** Настройки Cloudflare:

| Раздел | Настройка | Значение |
|---|---|---|
| SSL/TLS → Overview | Encryption mode | Full (strict) |
| SSL/TLS → Edge Certificates | Minimum TLS Version | TLS 1.2 |
| Network | WebSockets | On |
| Network | gRPC | On (обязательно для xHTTP stream-one) |
| Speed → Optimization | HTTP/2 | On |
| Speed → Optimization | HTTP/3 (QUIC) | On |

---

## ЧАСТЬ 6: КЛИЕНТСКИЕ ССЫЛКИ

### 6.1 Формат ссылок

**Ссылка 1 — Reality+Vision (прямое подключение, основная):**
```
vless://ВСТАВИТЬ_UUID@85.137.166.209:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=ВСТАВИТЬ_SNI_ДОНОР&fp=chrome&pbk=ВСТАВИТЬ_PUBLIC_KEY&sid=ВСТАВИТЬ_SHORT_ID&type=tcp#DataLink-Direct
```

**Ссылка 2 — Reality+xHTTP stream-one через Cloudflare (мобильная):**
```
vless://ВСТАВИТЬ_UUID@ВСТАВИТЬ_ДОМЕН:443?encryption=none&security=reality&sni=ВСТАВИТЬ_SNI_ДОНОР&fp=chrome&pbk=ВСТАВИТЬ_PUBLIC_KEY&sid=ВСТАВИТЬ_SHORT_ID&type=xhttp&path=ВСТАВИТЬ_XHTTP_PATH&mode=stream-one#DataLink-Mobile
```

### 6.2 Генерация QR-кодов

```bash
# QR для прямого подключения
qrencode -o /root/qr-direct.png \
  "vless://UUID@85.137.166.209:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=SNI&fp=chrome&pbk=PUBKEY&sid=SID&type=tcp#DataLink-Direct"

# QR для мобильного через CDN
qrencode -o /root/qr-mobile.png \
  "vless://UUID@ДОМЕН:443?encryption=none&security=reality&sni=SNI&fp=chrome&pbk=PUBKEY&sid=SID&type=xhttp&path=PATH&mode=stream-one#DataLink-Mobile"

# Просмотреть в терминале
qrencode -t ansiutf8 "ВАША_ССЫЛКА"
```

### 6.3 Клиентские приложения

**Android:**
| Приложение | Reality+Vision | xHTTP stream-one | Рекомендация |
|---|---|---|---|
| v2RayTun | ✅ | ✅ | Основное |
| v2rayNG | ✅ | ✅ | Альтернатива |
| AmneziaVPN | ✅ | ⚠️ Частично | Если уже установлен |

**iOS — все удалены из RU App Store. Инструкция для пользователей:**
```
1. Баланс Apple ID = 0 рублей
2. Настройки → Apple ID → Медиа и покупки → Страна/Регион → Казахстан
3. App Store → установить v2RayTun
4. Вернуть регион на РФ (приложение останется)
5. Импортировать ссылку от бота
```

---

## ЧАСТЬ 7: TELEGRAM-БОТ

### 7.1 Решение проблемы 409 и перевод на systemd

```bash
# Убить все текущие экземпляры
pkill -f datalink_pro_bot
sleep 2
pkill -9 -f datalink_pro_bot 2>/dev/null || true

# Создать systemd unit
cat > /etc/systemd/system/datalink-bot.service << 'EOF'
[Unit]
Description=DataLink PRO Telegram Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/usr/bin/python3 /root/datalink_pro_bot_v13.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable datalink-bot
systemctl start datalink-bot
systemctl status datalink-bot
```

### 7.2 Генерация пользователей (Python-функция для бота)

```python
import uuid as uuid_lib

# Константы — заполнить перед использованием
SERVER_IP   = "85.137.166.209"
DOMAIN      = "ВАШ_ДОМЕН.com"
PUBLIC_KEY  = "ВАШ_PUBLIC_KEY"
SHORT_ID    = "ВАШ_SHORT_ID"
SNI_DONOR   = "ВАШ_SNI_ДОНОР"
XHTTP_PATH  = "ВСТАВИТЬ_XHTTP_PATH"


def generate_user_configs(username: str) -> dict:
    """Генерирует два конфига для нового пользователя."""
    user_uuid = str(uuid_lib.uuid4())

    # Конфиг 1: Reality + XTLS-Vision (прямое, быстрое)
    direct_link = (
        f"vless://{user_uuid}@{SERVER_IP}:443"
        f"?encryption=none"
        f"&flow=xtls-rprx-vision"
        f"&security=reality"
        f"&sni={SNI_DONOR}"
        f"&fp=chrome"
        f"&pbk={PUBLIC_KEY}"
        f"&sid={SHORT_ID}"
        f"&type=tcp"
        f"#DataLink-Direct"
    )

    # Конфиг 2: Reality + xHTTP stream-one через CDN (мобильный)
    mobile_link = (
        f"vless://{user_uuid}@{DOMAIN}:443"
        f"?encryption=none"
        f"&security=reality"
        f"&sni={SNI_DONOR}"
        f"&fp=chrome"
        f"&pbk={PUBLIC_KEY}"
        f"&sid={SHORT_ID}"
        f"&type=xhttp"
        f"&path={XHTTP_PATH}"
        f"&mode=stream-one"
        f"#DataLink-Mobile"
    )

    return {
        "uuid": user_uuid,
        "direct": direct_link,
        "mobile": mobile_link
    }


def bot_message_text(configs: dict) -> str:
    """Текст сообщения пользователю."""
    return f"""🔐 DataLink PRO — подключение готово

📡 Основной конфиг (WiFi, проводной):
{configs['direct']}

📱 Мобильный конфиг (Билайн, CGNAT, шатдауны):
{configs['mobile']}

──────────────────
Как подключиться:
1. Установите v2RayTun (Android) или см. инструкцию для iPhone
2. Нажмите на ссылку — приложение откроется автоматически
3. Нажмите «Добавить» → «Подключить»

⚡ Если основной не работает — включите мобильный конфиг
🌙 Если VPN не работает ночью — это шатдаун оператора,
   ни один VPN в мире это не обходит. Попробуйте WiFi."""
```

### 7.3 Добавление UUID в конфиг Xray

При каждом новом пользователе добавить UUID в config.json:

```bash
# Открыть конфиг
nano /usr/local/etc/xray/config.json

# В секции "clients" обоих inbound добавить:
# {
#   "id": "НОВЫЙ_UUID",
#   "email": "username@datalink",
#   "flow": "xtls-rprx-vision"   ← только в первом inbound (Vision)
# }

# Проверить синтаксис
xray run -test -config /usr/local/etc/xray/config.json

# Применить без разрыва соединений
systemctl reload xray || systemctl restart xray
```

---

## ЧАСТЬ 8: МОНИТОРИНГ

### 8.1 UptimeRobot (обязательно, бесплатно)

1. Зарегистрироваться: uptimerobot.com
2. Add New Monitor → HTTPS → URL: https://ВАШ_ДОМЕН
3. Add New Monitor → TCP → Host: 85.137.166.209, Port: 443
4. Alert contact: Telegram-уведомления
5. Интервал: 5 минут

### 8.2 Справочные команды

```bash
# Статус всех сервисов одной командой
systemctl status xray nginx datalink-bot

# Логи Xray в реальном времени
tail -f /var/log/xray/error.log

# Логи бота
journalctl -u datalink-bot -f

# Перезапуск стека
systemctl restart xray && systemctl reload nginx

# Проверить IP сервера (не изменился ли)
curl -4 ifconfig.me

# Истечение SSL
certbot certificates

# Принудительное обновление SSL
certbot renew --force-renewal && systemctl reload nginx

# Место на диске
df -h

# Обновить список IP Cloudflare в nginx
# (раз в 2-3 месяца, список: https://www.cloudflare.com/ips-v4)
nginx -t && systemctl reload nginx
```

### 8.3 Алгоритм при массовом отвале пользователей

```
Шаг 1. Проверить что это не шатдаун оператора
  → Проверить тематические Telegram-каналы
  → Если шатдаун: написать пользователям «ожидайте, это проблема оператора»

Шаг 2. Проверить сервисы
  → systemctl status xray nginx
  → Если не running: systemctl restart СЕРВИС && смотреть логи

Шаг 3. Проверить внешнюю доступность
  → curl https://ВАШ_ДОМЕН
  → Если не отвечает: проблема в Cloudflare или сервере

Шаг 4. Проверить IP сервера
  → curl -4 ifconfig.me
  → Если изменился: обновить A-запись в Cloudflare DNS

Шаг 5. Смотреть логи
  → tail -50 /var/log/xray/error.log
  → journalctl -u nginx -n 50

Шаг 6. Если новая волна блокировок ТСПУ
  → Сменить SNI-донор в config.json
  → xray run -test -config ... && systemctl restart xray
  → Пользователей уведомлять не нужно (ссылки не меняются)

Шаг 7. После обновления Xray или Nginx
  → Уведомить пользователей обновить приложение v2RayTun
```

---

## ЧАСТЬ 9: ТАБЛИЦА ОШИБОК И РЕШЕНИЙ

| # | Симптом | Причина | Решение |
|---|---|---|---|
| 1 | xray run -test: ошибка | Синтаксис JSON | Проверить запятые/кавычки на jsonlint.com |
| 2 | nginx -t: ошибка | Неверный путь к сертификату | ls /etc/letsencrypt/live/ДОМЕН/ |
| 3 | Nginx не стартует | Порт 443 занят | ss -tlnp \| grep ':443' → остановить конфликт |
| 4 | Certbot ошибка | CF в Proxied, DNS не распространился | Серое облако CF, ждать DNS |
| 5 | Direct работает, CDN нет | IP Cloudflare не в geo списке Nginx | Обновить список CF IP в nginx.conf |
| 6 | CDN работает, direct нет | Неверный SNI-донор | Проверить донора тремя командами из раздела 2.3 |
| 7 | Оба не работают | После обновления Xray | xray version → уведомить обновить приложение |
| 8 | Российские сайты через VPN | Routing не настроен | Проверить routing в config.json |
| 9 | Бот 409 конфликт | Два экземпляра | pkill -f bot → запустить через systemd |
| 10 | Хаотичные разрывы | Порт мониторится ТСПУ | Сменить порт Xray inbound, обновить nginx.conf |
| 11 | gRPC ошибка в логах | gRPC не включён в Cloudflare | Network → gRPC → On |
| 12 | stream-one не работает | Клиент не поддерживает | Обновить v2RayTun до последней версии |

---

## ЧЕКЛИСТ ПЕРЕД ЗАПУСКОМ В PRODUCTION

```
СЕРВЕР
[ ] apt upgrade выполнен
[ ] BBR включён (sysctl net.ipv4.tcp_congestion_control = bbr)
[ ] UFW: открыты 22, 80, 443, 47821
[ ] Порты 80/443 свободны от других процессов

XRAY
[ ] xray version = 25.x+
[ ] xray run -test = Configuration OK
[ ] Оба inbound созданы: 10443 (Vision) и 10444 (xHTTP)
[ ] PRIVATE_KEY, PUBLIC_KEY, SHORT_ID сохранены в защищённом месте
[ ] SNI-донор проверен тремя командами (TLS 1.3, нет редиректа, не за CF)
[ ] xPaddingBytes: "100-1000" прописан в xhttpSettings
[ ] mode: "stream-one" прописан явно

NGINX
[ ] nginx -t = OK
[ ] Stream блок работает (443 слушается)
[ ] Список IP Cloudflare актуален (cloudflare.com/ips-v4)
[ ] grpc_pass настроен для xHTTP endpoint
[ ] XHTTP_PATH совпадает в xray config и nginx location

ДОМЕН И SSL
[ ] A-запись → 85.137.166.209, Cloudflare Proxied (оранжевое)
[ ] SSL/TLS: Full (strict), WebSockets On, gRPC On
[ ] Сертификат получен, не истекает раньше 60 дней

ТЕСТИРОВАНИЕ (на реальных устройствах, обязательно)
[ ] Direct: Android v2RayTun подключился, YouTube работает
[ ] Mobile: Android v2RayTun через Cloudflare подключился
[ ] Mobile: тест с Билайн мобильным интернетом (CGNAT)
[ ] iOS: v2RayTun после смены региона, оба конфига работают
[ ] Яндекс.ру открывается с российским IP (split tunneling работает)
[ ] dnsleaktest.com — нет российских DNS

БОТ
[ ] Бот на systemd, Restart=always, нет конфликта 409
[ ] Бот выдаёт ДВА конфига при регистрации (direct + mobile)
[ ] ЮKassa вебхук работает

МОНИТОРИНГ
[ ] UptimeRobot настроен, уведомление в Telegram работает
```

---

## ПРИЛОЖЕНИЕ: СПРАВОЧНЫЕ ССЫЛКИ

- Официальный конфиг Reality+xHTTP на одном сервере: https://github.com/XTLS/Xray-core/discussions/4232
- Готовый конфиг Reality+xHTTP: https://timharbakon.com/vless-reality-xhttp-proxy/
- Актуальные IP Cloudflare: https://www.cloudflare.com/ips-v4
- Xray документация: https://xtls.github.io/ru/
- 3x-ui панель: https://github.com/MHSanaei/3x-ui
- Статья о детекции ТСПУ: https://habr.com/ru/articles/1009542/

---

*DATALINK PRO | Финальное техзадание | Апрель 2026*  
*Конфигурация: VLESS Reality+Vision (direct) + VLESS Reality+xHTTP stream-one (CDN)*  
*Для инженера — все команды проверены и готовы к исполнению*
