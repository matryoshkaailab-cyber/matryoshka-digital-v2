# DATALINK PRO — ТЕХНИЧЕСКОЕ ЗАДАНИЕ ДЛЯ ИНЖЕНЕРА
## Оптимальная конфигурация VPN: VLESS Reality+Vision + VLESS Reality+xHTTP

**Дата:** Апрель 2026  
**Версия:** 1.0 ФИНАЛЬНАЯ  
**Статус:** К исполнению  
**Сервер:** 85.137.166.209 (Чехия, SmartApe, Ubuntu 24.04)

---

## АРХИТЕКТУРНОЕ РЕШЕНИЕ — ПОЧЕМУ ИМЕННО ЭТО

Реализуется ДВА inbound на ОДНОМ сервере, ОДИН порт 443, маршрутизация через Nginx:

```
Прямое подключение (не через CDN):
Клиент → IP сервера :443 → Nginx → Xray inbound #1
Протокол: VLESS + Reality + XTLS-Vision (TCP)
Использование: проводной интернет, стабильные операторы

Подключение через Cloudflare CDN:
Клиент → Cloudflare IP :443 → IP сервера :443 → Nginx → Xray inbound #2
Протокол: VLESS + Reality + xHTTP
Использование: мобильный CGNAT, Билайн, белые списки, блокировка IP
```

Nginx определяет источник по IP: если запрос пришёл с IP Cloudflare — отправляет в xHTTP inbound. Если прямое подключение — в Reality+Vision inbound. Один порт 443, два протокола, автоматическое переключение.

**Почему два протокола а не один:**
- Reality+Vision: максимальная скорость (XTLS Splice на уровне ядра), лучший стелс TLS-рукопожатия, но не закрывает детекцию поведения трафика после рукопожатия
- xHTTP+Reality: закрывает детекцию поведения трафика, работает через CDN (IP сервера скрыт), лучший для мобильного CGNAT
- Вместе: закрывают все известные векторы детекции ТСПУ на апрель 2026

---

## ЧАСТЬ 1: ПОДГОТОВКА СЕРВЕРА

### 1.1 Системные требования (текущий сервер соответствует)

```
ОС: Ubuntu 24.04 LTS ✅
RAM: минимум 1 GB (у нас 7.8 GB) ✅
Disk: минимум 10 GB ✅
Открытые порты: 443/TCP, 80/TCP
```

### 1.2 Обновление системы и включение BBR

```bash
ssh root@85.137.166.209

# Обновить пакеты
apt update && apt upgrade -y

# Установить зависимости
apt install -y curl wget unzip nginx certbot python3-certbot-nginx ufw qrencode

# Включить BBR (алгоритм Google для увеличения скорости и стабильности)
echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=bbr" >> /etc/sysctl.conf
sysctl -p

# Проверить BBR
sysctl net.ipv4.tcp_congestion_control
# Ожидаемый вывод: net.ipv4.tcp_congestion_control = bbr

# Настроить файрвол
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 47821/tcp   # Порт панели 3x-ui
ufw enable
ufw status
```

### 1.3 Конфликт с существующими процессами

```bash
# Проверить что занимает порты 80 и 443
ss -tlnp | grep ':80\|:443'

# Если datalink_web.py или другой процесс занимает порты:
pkill -f datalink_web
# Или остановить через systemctl если переведён на systemd

# Проверить что порты освободились
ss -tlnp | grep ':80\|:443'
# Должно быть пусто
```

---

## ЧАСТЬ 2: УСТАНОВКА И НАСТРОЙКА XRAY

### 2.1 Установка Xray-core (последняя версия)

```bash
# Установить Xray через официальный скрипт
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Проверить версию
xray version
# Ожидаемый вывод: Xray 25.x.x или новее

# Проверить статус
systemctl status xray
```

### 2.2 Генерация ключей

```bash
# Генерировать UUID для каждого пользователя отдельно
# Для серверного inbound — один общий набор ключей Reality

# Сгенерировать ключи Reality (x25519)
xray x25519
# Сохранить оба ключа:
# Private key: СОХРАНИТЬ СЕКРЕТНО — только на сервере
# Public key:  ПЕРЕДАВАТЬ клиентам в конфиге

# Сгенерировать Short ID
openssl rand -hex 8
# Пример: a1b2c3d4e5f6a7b8
# Можно сгенерировать несколько для разных клиентов

# Получить IP сервера
curl -4 ifconfig.me
# Должен вернуть: 85.137.166.209
```

**ВАЖНО: сохранить все значения в защищённом месте:**
```
PRIVATE_KEY = (из xray x25519, строка "Private key:")
PUBLIC_KEY  = (из xray x25519, строка "Public key:")
SHORT_ID    = (из openssl rand -hex 8)
SERVER_IP   = 85.137.166.209
```

### 2.3 Выбор SNI-донора

SNI-донор — реальный зарубежный сайт под который маскируется Reality.

**Требования:**
- Поддерживает TLS 1.3
- НЕ стоит за Cloudflare или другим CDN
- Не заблокирован РКН
- Не делает редирект на другой домен

**Проверить кандидата:**
```bash
# Проверить TLS версию
curl -svo /dev/null https://КАНДИДАТ.com 2>&1 | grep "TLSv"
# Должен быть TLSv1.3

# Проверить что нет редиректа
curl -I https://КАНДИДАТ.com
# Должен вернуть 200 OK (не 301/302)

# Проверить что НЕ за Cloudflare
curl -I https://КАНДИДАТ.com | grep "CF-RAY"
# Должно быть ПУСТО
```

**Проверенные доноры на апрель 2026:**
- www.speedtest.net
- cdn.jsdelivr.net  
- dl.google.com
- gateway.icloud.com (осторожно — Apple меняет поведение)

**НЕ использовать:**
- google.com, youtube.com (слишком популярные — под наблюдением)
- yandex.ru, vk.com (российские)
- Любые домены через Cloudflare CDN

### 2.4 Основной конфиг Xray (два inbound)

```bash
# Создать конфиг
cat > /usr/local/etc/xray/config.json << 'EOF'
{
  "log": {
    "loglevel": "warning",
    "access": "/var/log/xray/access.log",
    "error": "/var/log/xray/error.log"
  },

  "inbounds": [

    {
      "tag": "reality-vision-direct",
      "listen": "127.0.0.1",
      "port": 10443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "ВСТАВИТЬ_UUID_ПОЛЬЗОВАТЕЛЯ_1",
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
          "dest": "ВАШ_SNI_ДОНОР:443",
          "xver": 0,
          "serverNames": ["ВАШ_SNI_ДОНОР"],
          "privateKey": "ВАШ_PRIVATE_KEY",
          "shortIds": ["ВАШ_SHORT_ID"]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic", "fakedns"]
      }
    },

    {
      "tag": "reality-xhttp-cdn",
      "listen": "127.0.0.1",
      "port": 10444,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "ВСТАВИТЬ_UUID_ПОЛЬЗОВАТЕЛЯ_1",
            "email": "user1-xhttp@datalink"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "xhttp",
        "xhttpSettings": {
          "path": "/СЕКРЕТНЫЙ_PATH",
          "mode": "auto"
        },
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "ВАШ_SNI_ДОНОР:443",
          "xver": 0,
          "serverNames": ["ВАШ_SNI_ДОНОР"],
          "privateKey": "ВАШ_PRIVATE_KEY",
          "shortIds": ["ВАШ_SHORT_ID"]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic", "fakedns"]
      }
    }

  ],

  "outbounds": [
    {
      "tag": "direct",
      "protocol": "freedom",
      "settings": {}
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
        "ip": ["geoip:ru"],
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
EOF
```

**Что заменить в конфиге:**
```
ВСТАВИТЬ_UUID_ПОЛЬЗОВАТЕЛЯ_1  → результат команды: xray uuid
ВАШ_SNI_ДОНОР                 → выбранный донор, например: www.speedtest.net
ВАШ_PRIVATE_KEY               → Private key из xray x25519
ВАШ_SHORT_ID                  → результат openssl rand -hex 8
СЕКРЕТНЫЙ_PATH                → любой случайный путь, например: /api/v3/stream
```

```bash
# Проверить синтаксис конфига
xray run -test -config /usr/local/etc/xray/config.json
# Ожидаемый вывод: Configuration OK

# Перезапустить Xray
systemctl restart xray
systemctl status xray

# Создать директорию для логов если нет
mkdir -p /var/log/xray
```

---

## ЧАСТЬ 3: НАСТРОЙКА NGINX

Nginx выполняет критическую роль: определяет откуда пришёл запрос и направляет в нужный Xray inbound.

```bash
# Создать конфиг Nginx
cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;

# Критически важно для xHTTP: stream блок для TCP маршрутизации
events {
    worker_connections 1024;
}

# Stream блок для маршрутизации по IP источника
stream {
    # Список IP-адресов Cloudflare (обновлять раз в несколько месяцев)
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

    map $is_cloudflare $backend {
        0   127.0.0.1:10443;  # Прямое подключение → Reality+Vision
        1   127.0.0.1:10445;  # Через Cloudflare → Nginx http блок → xHTTP
    }

    server {
        listen 443;
        proxy_pass $backend;
        proxy_timeout 315s;
        proxy_connect_timeout 5s;
    }
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;

    server {
        listen 127.0.0.1:10445 ssl http2;
        server_name ВАШ_ДОМЕН.com;

        ssl_certificate /etc/letsencrypt/live/ВАШ_ДОМЕН.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ВАШ_ДОМЕН.com/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        # xHTTP endpoint
        location /СЕКРЕТНЫЙ_PATH {
            grpc_pass grpc://127.0.0.1:10444;
            grpc_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            grpc_read_timeout 315s;
            grpc_send_timeout 315s;
        }

        # Маскировочная страница
        location / {
            return 200 'OK';
            add_header Content-Type text/plain;
        }
    }

    # HTTP → HTTPS редирект
    server {
        listen 80;
        server_name ВАШ_ДОМЕН.com;
        return 301 https://$server_name$request_uri;
    }
}
EOF
```

**Что заменить:**
```
ВАШ_ДОМЕН.com     → ваш реальный домен (латинский)
СЕКРЕТНЫЙ_PATH    → тот же путь что в xray конфиге
```

```bash
# Проверить синтаксис
nginx -t
# Ожидаемый вывод: syntax is ok / test is successful

# Перезапустить Nginx
systemctl restart nginx
systemctl status nginx
```

---

## ЧАСТЬ 4: НАСТРОЙКА ДОМЕНА И CLOUDFLARE

### 4.1 Требования к домену

Нужен латинский домен (не кириллица). Кириллический даталинк-про.рф работает через punycode но создаёт сложности. Рекомендуется отдельный домен для VPN-инфраструктуры.

### 4.2 DNS в Cloudflare

```
Тип    Имя    Содержимое         Прокси
A      @      85.137.166.209     Серое облако (DNS only) — для получения сертификата
A      vpn    85.137.166.209     Серое облако (DNS only) — временно для certbot
```

### 4.3 Получение SSL-сертификата

```bash
# Cloudflare должен быть в режиме DNS only (серое облако) на этом этапе
# Проверить что DNS уже смотрит на сервер:
dig ВАШ_ДОМЕН.com +short
# Должен вернуть: 85.137.166.209

# Получить сертификат
certbot --nginx -d ВАШ_ДОМЕН.com

# Проверить:
certbot certificates
# Показывает дату истечения и пути к файлам

# Автообновление сертификата (проверить что настроено)
systemctl status certbot.timer
# Должен быть active
```

### 4.4 Включить Cloudflare прокси

После получения сертификата:

```
DNS → A-запись vpn → переключить на оранжевое облако (Proxied)

SSL/TLS → Overview → Full (strict)
Network → WebSockets → On
Network → gRPC → On
Speed → HTTP/2 → On
```

**КРИТИЧНО:** обновить список IP Cloudflare в Nginx конфиге из https://www.cloudflare.com/ips-v4 — список меняется.

---

## ЧАСТЬ 5: ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ

### 5.1 Через 3x-ui панель (рекомендуется)

```bash
# Установить 3x-ui если не установлен
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
# Выбрать нестандартный порт панели: 47821
# Задать сложный логин и пароль
```

В панели создать два inbound:
- **Inbound 1:** VLESS + TCP + Reality, port 10443, flow: xtls-rprx-vision
- **Inbound 2:** VLESS + xHTTP + Reality, port 10444, mode: auto

Добавлять пользователей через панель → система автоматически генерирует UUID и ссылки.

### 5.2 Вручную через конфиг

```bash
# Генерировать UUID для каждого нового пользователя
xray uuid
# Добавить в config.json в секцию clients обоих inbound
# Перезапустить xray:
systemctl restart xray
```

### 5.3 Формат клиентских ссылок

**Ссылка для Reality+Vision (прямое подключение):**
```
vless://UUID@85.137.166.209:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=ВАШ_SNI_ДОНОР&fp=chrome&pbk=ВАШ_PUBLIC_KEY&sid=ВАШ_SHORT_ID&type=tcp#DataLink-Direct
```

**Ссылка для xHTTP через Cloudflare (мобильный/CGNAT):**
```
vless://UUID@ВАШ_ДОМЕН.com:443?encryption=none&security=reality&sni=ВАШ_SNI_ДОНОР&fp=chrome&pbk=ВАШ_PUBLIC_KEY&sid=ВАШ_SHORT_ID&type=xhttp&path=СЕКРЕТНЫЙ_PATH#DataLink-Mobile
```

**Генерировать QR-код:**
```bash
qrencode -o /tmp/qr-direct.png "vless://UUID@85.137.166.209:443?..."
qrencode -o /tmp/qr-mobile.png "vless://UUID@ВАШ_ДОМЕН.com:443?..."
```

---

## ЧАСТЬ 6: КЛИЕНТСКИЕ ПРИЛОЖЕНИЯ

### Android

| Приложение | Поддержка Reality+Vision | Поддержка xHTTP | Статус |
|---|---|---|---|
| v2RayTun | ✅ | ✅ | Рекомендуется |
| v2rayNG | ✅ | ✅ | Рабочий |
| AmneziaVPN | ✅ VLESS | ⚠️ Частично | Если уже установлен |

### iOS (все VLESS-клиенты удалены из RU App Store)

Обязательна смена региона Apple ID:
```
1. Баланс Apple ID = 0 рублей
2. Настройки → Apple ID → Медиа и покупки → Страна/Регион → Казахстан
3. App Store → установить v2RayTun
4. Можно вернуть регион на РФ после установки
```

### Настройки клиента (v2RayTun, v2rayNG)

```
Для Reality+Vision (прямое подключение):
  Address: 85.137.166.209
  Port: 443
  UUID: (из конфига)
  Flow: xtls-rprx-vision
  Security: reality
  SNI: ВАШ_SNI_ДОНОР
  Fingerprint: chrome
  Public Key: ВАШ_PUBLIC_KEY
  Short ID: ВАШ_SHORT_ID
  Network: tcp

Для xHTTP через CDN (мобильный/CGNAT):
  Address: ВАШ_ДОМЕН.com
  Port: 443
  UUID: (из конфига)
  Flow: (пусто)
  Security: reality
  SNI: ВАШ_SNI_ДОНОР
  Fingerprint: chrome
  Public Key: ВАШ_PUBLIC_KEY
  Short ID: ВАШ_SHORT_ID
  Network: xhttp
  Path: СЕКРЕТНЫЙ_PATH
```

**Пользователь получает в боте ДВА конфига.** Инструкция:
```
📱 У вас два подключения:
• DataLink-Direct — основное, быстрое (WiFi, проводной)
• DataLink-Mobile — для мобильного интернета (Билайн, CGNAT, шатдауны)

Если основное не работает — включите мобильное.
Если не работает ни одно ночью — отключение оператора, не VPN.
```

---

## ЧАСТЬ 7: ИНТЕГРАЦИЯ С TELEGRAM-БОТОМ

### 7.1 Перевод бота на systemd

```bash
# Убить все текущие экземпляры бота (решение проблемы 409)
pkill -f datalink_pro_bot

# Создать systemd unit
cat > /etc/systemd/system/datalink-bot.service << 'EOF'
[Unit]
Description=DataLink PRO Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/usr/bin/python3 /root/datalink_pro_bot_v13.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable datalink-bot
systemctl start datalink-bot
systemctl status datalink-bot
```

### 7.2 Выдача двух конфигов через бота

Бот должен при выдаче конфига создавать пользователя в обоих inbound и отправлять две ссылки:

```python
def create_user_both_inbounds(username: str):
    user_uuid = str(uuid.uuid4())
    
    # Ссылка 1: Reality+Vision прямое подключение
    direct_link = (
        f"vless://{user_uuid}@85.137.166.209:443"
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
    
    # Ссылка 2: xHTTP через CDN
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
        f"#DataLink-Mobile"
    )
    
    return direct_link, mobile_link
```

---

## ЧАСТЬ 8: МОНИТОРИНГ

### 8.1 UptimeRobot (обязательно)

Зарегистрироваться на uptimerobot.com, создать мониторы:
- HTTPS: https://ВАШ_ДОМЕН.com → уведомление в Telegram
- TCP: 85.137.166.209:443 → уведомление в Telegram
- Интервал: 5 минут

### 8.2 Ключевые команды

```bash
# Статус всех сервисов
systemctl status xray nginx datalink-bot

# Логи Xray (live)
tail -f /var/log/xray/error.log

# Логи Nginx
tail -f /var/log/nginx/error.log

# Логи бота
journalctl -u datalink-bot -f

# Перезапуск всего стека
systemctl restart xray && systemctl restart nginx

# Проверить IP сервера
curl -4 ifconfig.me

# Место на диске
df -h

# SSL сертификат
certbot certificates
```

### 8.3 Алгоритм при массовом отвале

```
1. Проверить шатдаун оператора (Telegram-каналы)
   → Если шатдаун: написать пользователям, ждать. Это не ваша проблема.

2. Проверить сервисы:
   systemctl status xray nginx

3. Проверить доступность:
   curl https://ВАШ_ДОМЕН.com

4. Посмотреть логи:
   tail -50 /var/log/xray/error.log

5. Проверить IP сервера:
   curl -4 ifconfig.me
   → Если изменился: обновить A-запись в Cloudflare

6. Если новая волна блокировок:
   → Сменить SNI-донор в конфиге Xray
   → systemctl restart xray
   → Перевыпустить конфиги (не нужно — Reality/xHTTP не зависят от IP донора)

7. Проверить что список IP Cloudflare в Nginx актуален:
   https://www.cloudflare.com/ips-v4
   → Если изменился: обновить nginx.conf → nginx -t → systemctl reload nginx
```

---

## ЧАСТЬ 9: ТИПИЧНЫЕ ОШИБКИ И РЕШЕНИЯ

| # | Симптом | Причина | Решение |
|---|---|---|---|
| 1 | xray run -test выдаёт ошибку | Синтаксическая ошибка в JSON | Проверить запятые, кавычки, скобки. Использовать jsonlint.com |
| 2 | Nginx не стартует (port in use) | Порт 443 занят другим процессом | ss -tlnp \| grep ':443' → остановить конфликт |
| 3 | Certbot не получает сертификат | CF в Proxied режиме, DNS не распространился | Переключить CF в DNS only, ждать DNS |
| 4 | Прямое подключение работает, CDN нет | IP Cloudflare не в списке nginx geo | Обновить список CF IP в nginx.conf |
| 5 | CDN работает, прямое нет | Неверный SNI-донор (за CDN или редирект) | Проверить донора командами из раздела 2.3 |
| 6 | Оба не работают после обновления | Версия Xray изменилась | xray version → уведомить пользователей обновить приложение |
| 7 | Российские сайты через VPN | Routing не настроен | Проверить секцию routing в config.json |
| 8 | Бот 409 конфликт | Два экземпляра бота | pkill -f datalink_pro_bot → запустить через systemd |
| 9 | Пользователь не может подключиться | Неверный UUID или ключи в ссылке | Сверить UUID в config.json с ссылкой клиента |
| 10 | Разрывы соединения хаотично | Порт мониторится ТСПУ | Сменить порт Xray inbound и обновить nginx.conf |

---

## ЧАСТЬ 10: ОБНОВЛЕНИЕ СПИСКА IP CLOUDFLARE В NGINX

Список IP Cloudflare нужно обновлять раз в 2-3 месяца. Актуальный список: https://www.cloudflare.com/ips-v4

```bash
# Скачать актуальный список
curl https://www.cloudflare.com/ips-v4 -o /tmp/cf_ips.txt
cat /tmp/cf_ips.txt

# Обновить geo блок в nginx.conf вручную
# Затем:
nginx -t && systemctl reload nginx
```

---

## ЧЕКЛИСТ ПЕРЕД ЗАПУСКОМ В PRODUCTION

```
СЕРВЕР
[ ] apt upgrade выполнен
[ ] BBR включён: sysctl net.ipv4.tcp_congestion_control = bbr
[ ] UFW: открыты 22, 80, 443, 47821

XRAY
[ ] xray version показывает 25.x+
[ ] xray run -test -config /usr/local/etc/xray/config.json = OK
[ ] Оба inbound созданы (10443 и 10444)
[ ] PRIVATE_KEY, PUBLIC_KEY, SHORT_ID сохранены в защищённом месте
[ ] SNI-донор проверен (TLS 1.3, не за CDN, нет редиректа)

NGINX
[ ] nginx -t = OK
[ ] Stream блок работает (порт 443 слушается)
[ ] Список IP Cloudflare актуален

ДОМЕН И SSL
[ ] A-запись указывает на 85.137.166.209
[ ] Cloudflare: Proxied (оранжевое), Full (strict), WebSocket On, gRPC On
[ ] Certbot сертификат получен, не истекает раньше 60 дней

ТЕСТИРОВАНИЕ (обязательно на реальных устройствах)
[ ] Reality+Vision: Android v2RayTun прямое подключение → Connected
[ ] Reality+Vision: YouTube работает, скорость нормальная
[ ] xHTTP CDN: Android v2RayTun через Cloudflare → Connected
[ ] xHTTP CDN: тест с Билайн мобильным интернетом
[ ] Яндекс.ру открывается с российским IP (split tunneling)
[ ] dnsleaktest.com не показывает российские DNS
[ ] iOS v2RayTun (после смены региона) — оба конфига работают

БОТ
[ ] Конфликт 409 устранён
[ ] Бот на systemd с Restart=always
[ ] Бот выдаёт ДВА конфига при регистрации
[ ] ЮKassa вебхук работает (тестовый платёж)

МОНИТОРИНГ
[ ] UptimeRobot настроен, уведомления в Telegram приходят
```

---

## ПРИЛОЖЕНИЕ: СПРАВОЧНЫЕ ССЫЛКИ

- Xray-core GitHub: https://github.com/XTLS/Xray-core
- Xray документация: https://xtls.github.io/ru/
- Эталонный конфиг двойной настройки: https://github.com/XTLS/Xray-core/discussions/4232
- Актуальные IP Cloudflare: https://www.cloudflare.com/ips-v4
- 3x-ui панель: https://github.com/MHSanaei/3x-ui
- Статья о детекции ТСПУ 2026: https://habr.com/ru/articles/1009542/
- Готовый конфиг Reality+xHTTP: https://timharbakon.com/vless-reality-xhttp-proxy/

---

*DATALINK PRO | Техзадание для инженера | Апрель 2026*
*Конфигурация: VLESS Reality+Vision (прямое) + VLESS Reality+xHTTP (CDN)*
*Статус: Финальная версия*
