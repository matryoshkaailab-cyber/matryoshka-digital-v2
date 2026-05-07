# DATALINK PRO — ТЕХНИЧЕСКИЙ ПЛАН РАЗВЁРТЫВАНИЯ
## ЕДИНСТВЕННЫЙ ПРОТОКОЛ: VLESS + xHTTP

**Дата:** Апрель 2026
**Сервер:** 85.137.166.209 (Чехия, SmartApe, Ubuntu 24.04)
**Решение принято:** Только VLESS+xHTTP через Cloudflare CDN. AWG не используется для новых пользователей.

---

> ⚠️ КРИТИЧЕСКИ ВАЖНО ДЛЯ ВСЕЙ КОМАНДЫ
>
> Версии Xray-core на СЕРВЕРЕ и КЛИЕНТЕ обязаны совпадать.
> Несовпадение = полная неработоспособность без понятных ошибок в логах.
> После любого обновления 3x-ui — сразу проверять версию Xray командой: x-ui version
> Уведомлять пользователей обновить приложение перед раздачей новых конфигов.

---

## ПОЧЕМУ ТОЛЬКО VLESS+xHTTP — ОБОСНОВАНИЕ РЕШЕНИЯ

Все остальные протоколы отброшены по следующим причинам:

- **AWG Legacy (текущий)** — детектируется ТСПУ на мобильных сетях, причина всех проблем с Билайн CGNAT
- **AWG 2.0** — нестабилен на мобильном интернете с апреля 2026, управляется только через десктопное приложение (нет нормального API для автоматизации бота), не решает проблему CGNAT
- **OpenVPN, WireGuard чистый** — заблокированы полностью
- **Shadowsocks/Outline** — заблокирован на большинстве провайдеров
- **VLESS+Reality без xHTTP** — нестабилен с февраля 2026, ТСПУ научился анализировать поведение трафика после рукопожатия

**VLESS+xHTTP через Cloudflare CDN** закрывает:
- Мобильный интернет Билайн CGNAT ✅
- Мобильный МТС, Мегафон, Tele2 ✅
- Белые списки (шатдауны) ✅
- Блокировку IP-адреса сервера (IP скрыт за Cloudflare) ✅
- Проводной домашний интернет ✅

---

## СОДЕРЖАНИЕ

1. Архитектура
2. Требования
3. Установка сервера
4. Настройка 3x-ui и Xray
5. Настройка Nginx
6. Настройка Cloudflare
7. Интеграция с Telegram-ботом
8. Клиентские приложения
9. Мониторинг и аварийные процедуры
10. Перенос существующих пользователей
11. Сводная таблица ошибок
12. Чеклист перед запуском

---

## 1. АРХИТЕКТУРА

### Схема трафика

```
Пользователь (телефон/ПК)
        |
        | HTTPS порт 443
        ↓
Cloudflare CDN (бесплатно, скрывает реальный IP сервера)
        |
        | HTTPS → Nginx
        ↓
Nginx на VPS (85.137.166.209)
        |
        | HTTP → localhost:12345
        ↓
Xray-core (VLESS+xHTTP inbound)
        |
        ↓
Интернет
```

### Компоненты стека

| Компонент | Роль | Версия |
|---|---|---|
| Ubuntu 24.04 | ОС сервера | уже есть |
| Xray-core | Движок VLESS+xHTTP | 25.x (последняя) |
| 3x-ui | Веб-панель + REST API для управления пользователями | последняя из MHSanaei/3x-ui |
| Nginx | Reverse proxy, SSL-терминация | системный |
| Certbot | SSL-сертификат Let's Encrypt | системный |
| Cloudflare | CDN, скрывает IP, бесплатный Free план | — |
| Python-бот | Выдача конфигов через 3x-ui API + ЮKassa | доработка существующего |

### Почему Cloudflare обязателен

Без Cloudflare реальный IP сервера (85.137.166.209) виден всем. ТСПУ ведёт базу IP-адресов VPN-серверов и блокирует их. С Cloudflare пользователь подключается к IP-адресу Cloudflare (который нельзя заблокировать без отключения половины интернета), а реальный IP сервера скрыт.

---

## 2. ТРЕБОВАНИЯ

### Сервер (текущий подходит)

| Параметр | Текущий сервер | Требование |
|---|---|---|
| ОЗУ | 7.8 GiB | минимум 1 GB ✅ |
| Диск | 50 GiB | минимум 10 GB ✅ |
| ОС | Ubuntu 24.04 | Ubuntu 20.04+ ✅ |
| SSH | работает | ✅ |

### Что нужно получить до начала работ

**1. Доменное имя (латинское)**

Кириллический домен даталинк-про.рф технически можно использовать в punycode-форме (xn----7sbaowmfrljlq.xn--p1ai), но это усложняет настройку certbot и Nginx. Рекомендуется зарегистрировать отдельный латинский домен вида datalink-pro.com или datalink-vpn.ru и управлять им через Cloudflare.

**2. Аккаунт Cloudflare (бесплатный)**

Зарегистрироваться на cloudflare.com, добавить домен, перенести управление DNS на серверы Cloudflare.

**3. Свободный порт для 3x-ui панели**

Выбрать любой нестандартный порт, например 47821. Проверить что он свободен:
```bash
ss -tlnp | grep 47821
# Если пусто — порт свободен
```

---

## 3. УСТАНОВКА СЕРВЕРА

### Шаг 3.1 — Подготовка

```bash
ssh root@85.137.166.209

# Обновить систему
apt update && apt upgrade -y

# Установить зависимости
apt install -y curl wget git nginx certbot python3-certbot-nginx ufw

# Настроить файрвол
ufw allow 22/tcp      # SSH — не трогать, иначе потеряете доступ
ufw allow 80/tcp      # HTTP (нужен certbot для получения сертификата)
ufw allow 443/tcp     # HTTPS (порт для клиентов)
ufw allow 47821/tcp   # Порт панели 3x-ui (ваш нестандартный порт)
ufw enable

# Проверить что применилось
ufw status
```

> ОШИБКА #1: "Address already in use" при запуске Nginx
>
> ДИАГНОСТИКА:
> ```bash
> ss -tlnp | grep ':80\|:443'
> ```
> Найти процесс на порту. Скорее всего это datalink_web.py (существующий веб-бэкенд).
>
> РЕШЕНИЕ: Остановить существующий веб-процесс или перевести его на другой порт
> перед установкой Nginx. Nginx должен занять 80 и 443.
>
> ВАЖНО: Если datalink_web.py используется в production — сначала договориться
> о maintenance window, только потом останавливать.

### Шаг 3.2 — Установка 3x-ui

```bash
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
```

В процессе установки скрипт задаст вопросы:
- Порт панели → ввести 47821 (или другой нестандартный)
- Имя пользователя → придумать, не использовать "admin"
- Пароль → минимум 16 символов, сохранить в защищённое место

```bash
# После установки проверить
x-ui status
# Должно быть: running

# Если не запустился
x-ui start
x-ui logs    # посмотреть ошибки
```

Панель доступна по адресу: http://85.137.166.209:47821

> ОШИБКА #2: Панель недоступна из браузера
>
> ПРОВЕРИТЬ ПО ПОРЯДКУ:
>
> 1. Запущен ли сервис:
>    ```bash
>    x-ui status
>    ```
>
> 2. Открыт ли порт:
>    ```bash
>    ufw status | grep 47821
>    ```
>    Если нет — ufw allow 47821/tcp
>
> 3. Слушает ли порт:
>    ```bash
>    ss -tlnp | grep 47821
>    ```
>
> 4. Блокирует ли хостер SmartApe нестандартные порты — уточнить в поддержке.
>    Если блокирует — изменить порт панели через x-ui → пункт 14 в меню.

### Шаг 3.3 — SSL-сертификат

```bash
# СНАЧАЛА убедиться что DNS A-запись уже указывает на сервер
# (настройка Cloudflare в разделе 6 должна быть выполнена ДО этого шага)
# Проверить:
dig vpn.ваш-домен.com +short
# Ожидаемый результат: 85.137.166.209

# Получить сертификат
# ВАЖНО: Cloudflare в этот момент должен быть в режиме DNS only (серое облако),
# не Proxied (оранжевое облако) — иначе certbot не сможет верифицировать домен
certbot --nginx -d vpn.ваш-домен.com

# Проверить сертификат
certbot certificates
# Показывает дату истечения и путь к файлам
```

> ОШИБКА #3: Certbot — "Challenge failed" или "Connection refused"
>
> ПРИЧИНА 1: DNS ещё не распространился.
> Проверить: dig vpn.ваш-домен.com +short
> Если не возвращает IP — ждать от 5 минут до 1 часа.
>
> ПРИЧИНА 2: Cloudflare стоит в режиме Proxied (оранжевое облако).
> Временно переключить в DNS only (серое облако), получить сертификат, вернуть оранжевое.
>
> ПРИЧИНА 3: Порт 80 занят или закрыт.
> Альтернативный способ получения сертификата:
> ```bash
> systemctl stop nginx
> certbot certonly --standalone -d vpn.ваш-домен.com
> systemctl start nginx
> ```
>
> ПРИЧИНА 4: На сервере уже есть сертификат для этого домена.
> Принудительное обновление: certbot renew --force-renewal

---

## 4. НАСТРОЙКА 3x-ui И XRAY

### Шаг 4.1 — Обновить версию Xray в панели

Войти в панель: http://85.137.166.209:47821

Перейти: Settings (Настройки) → Xray Version
Выбрать последнюю версию 25.x и нажать Restart.

Проверить версию через SSH:
```bash
x-ui version
# Должно показать 25.x.x
```

> ОШИБКА #4: В списке нет версий 25.x, только старые
>
> Обновить саму панель 3x-ui:
> ```bash
> x-ui update
> ```
> После обновления снова открыть Settings → Xray Version.

### Шаг 4.2 — Создать VLESS+xHTTP inbound

В панели: Inbounds → Add Inbound

Заполнить поля точно по таблице:

| Поле | Значение | Пояснение |
|---|---|---|
| Remark | datalink-vless | Название для себя |
| Protocol | vless | |
| Port | 12345 | Внутренний порт Xray, клиенты его не видят |
| Total Flow (GB) | 0 | 0 = безлимит |
| Expire Date | пусто | Не ограничивать inbound |
| Security | tls | Обязательно TLS |
| Certificate File | /etc/letsencrypt/live/vpn.ваш-домен.com/fullchain.pem | |
| Key File | /etc/letsencrypt/live/vpn.ваш-домен.com/privkey.pem | |
| Transport | xhttp | Выбрать из выпадающего |
| Mode | packet-up | Единственный вариант совместимый с Cloudflare |
| Path | /dl-vpn | Любой путь, запомнить — нужен для Nginx |
| Host | vpn.ваш-домен.com | |
| Sniffing | ВКЛ | ОБЯЗАТЕЛЬНО |
| Sniffing Domain | tls,http,quic,fakedns | |
| Flow | ПУСТО | Не выбирать — только для Reality+TCP |

Нажать Save (Сохранить).

> ОШИБКА #5: xHTTP нет в выпадающем списке транспортов
>
> Панель 3x-ui устарела. Выполнить:
> ```bash
> x-ui update
> ```
> Затем повторно открыть Add Inbound.

> ОШИБКА #6: Клиент подключается (статус Connected) но сайты не открываются
>
> ДИАГНОСТИКА:
> ```bash
> x-ui logs -f
> # Смотреть на ошибки в реальном времени пока пытаетесь открыть сайт
> ```
>
> ПРИЧИНА 1: Sniffing выключен → включить в настройках inbound.
>
> ПРИЧИНА 2: Path в клиенте не совпадает с Path в inbound.
> Проверить что в клиентской ссылке path=/dl-vpn совпадает с настройкой.
>
> ПРИЧИНА 3: Routing не настроен (см. шаг 4.3).
>
> ПРИЧИНА 4: DNS утечка — проверить dnsleaktest.com.

### Шаг 4.3 — Настройка маршрутизации (Split Tunneling)

Это критически важно. Без этого пользователи не смогут открывать российские сайты (Wildberries, Сбербанк, Госуслуги и т.д.) — они блокируют VPN-IP.

В панели: Xray Settings → Routing (или Route)

Добавить правила в следующем порядке (порядок важен):

```
Правило 1:
  Type: field
  Domain: geosite:ru
  Outbound: direct

Правило 2:
  Type: field
  IP: geoip:ru
  Outbound: direct

Правило 3:
  Type: field
  IP: geoip:private
  Outbound: direct

Правило 4 (опционально — блокировка рекламы):
  Type: field
  Domain: geosite:category-ads-all
  Outbound: block

Правило 5 (финальное):
  Type: field
  Network: tcp,udp
  Outbound: proxy
```

Нажать Save → Restart Xray.

---

## 5. НАСТРОЙКА NGINX

### Шаг 5.1 — Конфигурационный файл

Создать файл:
```bash
nano /etc/nginx/sites-available/datalink-vless
```

Вставить содержимое:

```nginx
# HTTPS сервер — основной
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name vpn.ваш-домен.com;

    # SSL сертификаты от certbot
    ssl_certificate /etc/letsencrypt/live/vpn.ваш-домен.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vpn.ваш-домен.com/privkey.pem;

    # Безопасные настройки TLS
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Маршрут для VLESS+xHTTP трафика
    # /dl-vpn должен совпадать с Path в настройке inbound (шаг 4.2)
    location /dl-vpn {
        proxy_pass http://127.0.0.1:12345;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 315s;
        proxy_send_timeout 315s;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Заглушка — при прямом обращении к домену выглядит как обычный сайт
    location / {
        return 200 'OK';
        add_header Content-Type text/plain;
        add_header Server "nginx";
    }
}

# HTTP → HTTPS редирект
server {
    listen 80;
    listen [::]:80;
    server_name vpn.ваш-домен.com;
    return 301 https://$server_name$request_uri;
}
```

```bash
# Активировать конфиг
ln -s /etc/nginx/sites-available/datalink-vless /etc/nginx/sites-enabled/

# ОБЯЗАТЕЛЬНО проверить синтаксис перед перезапуском
nginx -t
# Ожидаемый вывод: nginx: configuration file /etc/nginx/nginx.conf test is successful

# Применить конфиг
systemctl reload nginx
```

> ОШИБКА #7: nginx -t выдаёт ошибку
>
> ОШИБКА "could not build server_names_hash":
> В файле /etc/nginx/nginx.conf внутри блока http{} добавить строку:
> server_names_hash_bucket_size 128;
>
> ОШИБКА "No such file or directory" для сертификатов:
> ```bash
> ls -la /etc/letsencrypt/live/vpn.ваш-домен.com/
> ```
> Если папки нет — certbot не выпустил сертификат. Вернуться к шагу 3.3.
>
> ОШИБКА синтаксическая (missing ; или }):
> Внимательно проверить конфиг — каждая директива заканчивается точкой с запятой,
> каждый блок {} закрыт.

---

## 6. НАСТРОЙКА CLOUDFLARE

### Шаг 6.1 — Добавить домен

1. Зайти на cloudflare.com → Add a Site
2. Ввести домен → выбрать Free план
3. Следовать инструкциям по смене NS-серверов у регистратора домена
4. Ждать активации (от 5 минут до 24 часов)

### Шаг 6.2 — DNS-запись

DNS → Add Record:

| Тип | Имя | Содержимое | Прокси |
|---|---|---|---|
| A | vpn | 85.137.166.209 | Оранжевое облако (Proxied) |

Оранжевое облако — ОБЯЗАТЕЛЬНО. Именно оно скрывает реальный IP сервера.

### Шаг 6.3 — Настройки Cloudflare

Пройти по всем разделам и выставить:

| Раздел | Настройка | Значение |
|---|---|---|
| SSL/TLS → Overview | Encryption mode | Full (strict) |
| SSL/TLS → Edge Certificates | Minimum TLS | TLS 1.2 |
| SSL/TLS → Edge Certificates | TLS 1.3 | Enabled |
| Network | WebSockets | On |
| Network | gRPC | On |
| Speed → Optimization | HTTP/2 | On |
| Speed → Optimization | HTTP/3 (QUIC) | On |

### Шаг 6.4 — Проверка

```bash
# С любого внешнего устройства (не с сервера):
curl -I https://vpn.ваш-домен.com
# Ожидаемый ответ: HTTP/2 200 (через Cloudflare)
# В заголовках должен быть: CF-RAY: ... (признак Cloudflare)
```

> ОШИБКА #8: Cloudflare возвращает 502 Bad Gateway
>
> ПРОВЕРИТЬ ПО ПОРЯДКУ:
>
> 1. Nginx запущен: systemctl status nginx
> 2. Xray запущен: x-ui status
> 3. Nginx слушает 443: ss -tlnp | grep ':443'
> 4. SSL mode в Cloudflare: должен быть Full (strict), не Flexible
>    При Flexible CF пытается подключиться по HTTP к серверу — получает ошибку.
>
> Временный тест — отключить Cloudflare прокси (серое облако) и проверить
> прямое подключение: curl -I https://85.137.166.209 --resolve vpn.домен.com:443:85.137.166.209
> Если работает напрямую но не через CF — проблема в настройках Cloudflare.

> ОШИБКА #9: Работает без Cloudflare, не работает через Cloudflare
>
> ПРИЧИНА 1: Cloudflare не поддерживает данный порт на Free плане.
> РЕШЕНИЕ: Убедиться что клиент подключается именно на порт 443.
>
> ПРИЧИНА 2: Режим xHTTP не packet-up.
> Режим stream-up и stream-one не проходят через Cloudflare без специальной настройки.
> РЕШЕНИЕ: В настройках inbound (шаг 4.2) Mode обязательно packet-up.
>
> ПРИЧИНА 3: WebSockets или gRPC не включены в Cloudflare.
> РЕШЕНИЕ: Network → WebSockets On, Network → gRPC On.

---

## 7. ИНТЕГРАЦИЯ С TELEGRAM-БОТОМ

### Шаг 7.1 — Выбор подхода

**Вариант A — Использовать готовый бот (рекомендуется)**

Репозиторий evansvl/3x-ui-shop — Python, Docker, ЮKassa уже интегрирована, мультисервер:

```bash
git clone https://github.com/evansvl/3x-ui-shop.git
cd 3x-ui-shop
cp .env.example .env
nano .env
```

Обязательные переменные в .env:
```
BOT_TOKEN=8349948703:AAFybtShN5Q6LlVM8nzUbEzTvQK1VrgAc5I
YOOKASSA_SHOP_ID=1313515
YOOKASSA_SECRET_KEY=live_ВАША_СЕКРЕТНАЯ_КЛЮЧ
XUI_URL=http://127.0.0.1:47821
XUI_USERNAME=ваш_логин_панели
XUI_PASSWORD=ваш_пароль_панели
XUI_INBOUND_ID=1
DOMAIN=vpn.ваш-домен.com
VLESS_PATH=/dl-vpn
```

```bash
bash install.sh
```

**Вариант B — Доработать существующий бот datalink_pro_bot_v13.py**

Добавить в существующий бот функции работы с 3x-ui API (см. шаг 7.2).

### Шаг 7.2 — API 3x-ui (для варианта B или кастомной интеграции)

Все запросы идут на http://127.0.0.1:47821. Аутентификация через сессионные cookie.

**Авторизация:**
```python
import requests

session = requests.Session()

def login():
    resp = session.post(
        "http://127.0.0.1:47821/login",
        json={"username": XUI_USERNAME, "password": XUI_PASSWORD}
    )
    if resp.status_code != 200:
        raise Exception(f"Login failed: {resp.text}")
    return True

# Вызывать при старте и при получении 401
login()
```

**Создание пользователя:**
```python
import uuid, json, time

def create_vless_user(username: str, expire_days: int = 30, traffic_gb: int = 0):
    user_uuid = str(uuid.uuid4())
    expire_ms = int((time.time() + expire_days * 86400) * 1000) if expire_days > 0 else 0

    client = {
        "id": user_uuid,
        "email": f"{username}@datalink",
        "enable": True,
        "expiryTime": expire_ms,
        "totalGB": traffic_gb * 1024 * 1024 * 1024,  # bytes, 0 = безлимит
        "limitIp": 3,  # максимум устройств
        "subId": user_uuid[:8],
        "tgId": "",
        "comment": username
    }

    resp = session.post(
        "http://127.0.0.1:47821/xui/inbound/addClient",
        json={
            "id": INBOUND_ID,  # ID inbound из панели (обычно 1)
            "settings": json.dumps({"clients": [client]})
        }
    )

    if resp.status_code == 401:
        login()  # Переавторизация при истечении сессии
        return create_vless_user(username, expire_days, traffic_gb)

    if not resp.json().get("success"):
        raise Exception(f"Create user failed: {resp.text}")

    # Формируем ссылку для пользователя
    vless_link = (
        f"vless://{user_uuid}@vpn.ваш-домен.com:443"
        f"?type=xhttp&security=tls&path=%2Fdl-vpn"
        f"&host=vpn.ваш-домен.com"
        f"#DataLink-PRO"
    )

    return {"uuid": user_uuid, "link": vless_link}
```

**Удаление пользователя (при отмене подписки):**
```python
def delete_vless_user(inbound_id: int, user_uuid: str):
    resp = session.post(
        f"http://127.0.0.1:47821/xui/inbound/{inbound_id}/delClient/{user_uuid}"
    )
    if resp.status_code == 401:
        login()
        return delete_vless_user(inbound_id, user_uuid)
    return resp.json().get("success", False)
```

**Получение трафика пользователя:**
```python
def get_user_traffic(email: str):
    resp = session.get(
        f"http://127.0.0.1:47821/xui/inbound/getClientTraffics/{email}@datalink"
    )
    if resp.status_code == 401:
        login()
        return get_user_traffic(email)
    data = resp.json()
    if data.get("success"):
        obj = data.get("obj", {})
        return {
            "up": obj.get("up", 0),
            "down": obj.get("down", 0),
            "total": obj.get("total", 0),
            "enable": obj.get("enable", True)
        }
    return None
```

### Шаг 7.3 — Перевод бота на systemd (обязательно)

Текущий бот запускается через nohup — нет автозапуска при падении. Это критическая проблема для бизнеса.

```bash
# Создать unit-файл
nano /etc/systemd/system/datalink-bot.service
```

```ini
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
PIDFile=/run/datalink-bot.pid

[Install]
WantedBy=multi-user.target
```

```bash
# Убить текущие экземпляры бота (решение проблемы 409)
pkill -f datalink_pro_bot

# Активировать и запустить
systemctl daemon-reload
systemctl enable datalink-bot
systemctl start datalink-bot

# Проверить статус
systemctl status datalink-bot

# Смотреть логи
journalctl -u datalink-bot -f
```

> ОШИБКА #10: Бот не авторизуется в 3x-ui API (401 Unauthorized)
>
> ПРИЧИНА 1: Неверные XUI_USERNAME или XUI_PASSWORD.
> Проверить что они совпадают с теми что вводились при установке 3x-ui.
>
> ПРИЧИНА 2: Сессионная cookie истекла.
> Решение: реализовать автоматическую переавторизацию при получении 401 (код выше).
>
> ПРИЧИНА 3: Бот обращается по внешнему IP вместо localhost.
> Правильно: http://127.0.0.1:47821
> Неправильно: http://85.137.166.209:47821
>
> ПРИЧИНА 4: Панель 3x-ui упала.
> Проверить: x-ui status && x-ui start

### Шаг 7.4 — Текст сообщения бота для пользователя

```
🔐 DataLink PRO — ваш VPN готов

Нажмите на ссылку ниже — приложение откроется автоматически:

[VLESS-ссылка]

📱 Если ссылка не открывается автоматически:
Android: v2RayTun (скачать в Google Play)
iPhone: инструкция → [кнопка]

▶ Нажмите "Добавить" → "Подключиться"

❓ Если не работает на мобильном интернете ночью —
это отключение связи оператором во время тревоги.
Ни один VPN не обходит полный шатдаун.
Попробуйте подключиться к WiFi.
```

---

## 8. КЛИЕНТСКИЕ ПРИЛОЖЕНИЯ

### Android

| Приложение | Google Play РФ | Поддержка xHTTP | Рекомендация |
|---|---|---|---|
| v2RayTun | ✅ Есть | ✅ Да | ОСНОВНОЕ |
| v2rayNG | ✅ Есть | ✅ Да | Альтернатива |
| AmneziaVPN | ✅ Есть | ✅ Понимает VLESS-конфиги | Если уже установлен |
| Hiddify | ❌ Заброшен, не обновляется | ❌ | НЕ ИСПОЛЬЗОВАТЬ |

Пользователь получает vless:// ссылку → нажимает на неё → приложение открывается и предлагает добавить подключение → нажать "Добавить" → "Подключить".

### iOS

Все основные VLESS-клиенты удалены из российского App Store (v2RayTun, Happ — март 2026, AmneziaVPN — октябрь 2024).

Единственное решение — смена региона Apple ID. Инструкция которая должна быть в боте кнопкой:

```
Инструкция для iPhone:

1. Проверьте баланс Apple ID — должен быть 0 рублей
   (Настройки → [ваше имя] → Медиа и покупки → просмотреть баланс)

2. Откройте: Настройки → [ваше имя] → Медиа и покупки → Просмотреть

3. Нажмите "Страна или регион" → выберите Казахстан

4. Согласитесь с условиями, укажите любой адрес в Казахстане

5. Откройте App Store → найдите "v2RayTun" → установите

6. После установки можно вернуть регион обратно на Россию
   Приложение останется на телефоне навсегда

7. Откройте ссылку которую прислал бот — v2RayTun откроется автоматически
```

> ОШИБКА #11: Пользователь говорит "у меня не работает Hiddify"
>
> Hiddify не обновлялся с марта 2026 и фактически брошен разработчиками.
> Решение для пользователя: удалить Hiddify, установить v2RayTun.
> Конфиг (vless:// ссылка) одинаково работает в обоих приложениях.

---

## 9. МОНИТОРИНГ И АВАРИЙНЫЕ ПРОЦЕДУРЫ

### Обязательный мониторинг

Настроить UptimeRobot (бесплатно, uptimerobot.com):
- Создать monitor типа HTTPS
- URL: https://vpn.ваш-домен.com
- Интервал: 5 минут
- Уведомление: Telegram (есть встроенная интеграция)

При падении сервиса получите уведомление в Telegram раньше чем пользователи начнут жаловаться.

### Ежедневные команды

```bash
# Полный статус системы
x-ui status && systemctl status nginx && systemctl status datalink-bot

# Количество активных пользователей в Xray
x-ui logs | grep "accepted" | wc -l

# Проверить место на диске (логи растут)
df -h

# Проверить когда истекает SSL-сертификат
certbot certificates | grep "Expiry Date"
```

### Алгоритм при массовом отвале (пошагово)

```
ШАГ 1: Проверить что это не шатдаун оператора
  → Зайти в Telegram-канал с новостями о шатдаунах
  → Если шатдаун — сообщить пользователям, ждать окончания
  → Это не ваша проблема, ни один VPN не поможет

ШАГ 2: Проверить сервисы
  → x-ui status
  → systemctl status nginx
  → systemctl status datalink-bot
  Если что-то не running — запустить и смотреть логи

ШАГ 3: Проверить доступность извне
  → curl https://vpn.ваш-домен.com
  → Если не отвечает — проблема в Cloudflare или сервере

ШАГ 4: Проверить Cloudflare
  → cloudflarestatus.com (глобальный статус)
  → Если CF в порядке — проблема на стороне сервера

ШАГ 5: Проверить не изменился ли IP сервера
  → curl ifconfig.me
  → Если не совпадает с 85.137.166.209 — обновить A-запись в Cloudflare DNS

ШАГ 6: Проверить логи на конкретную ошибку
  → x-ui logs -f
  → journalctl -u nginx -n 50
  → Найти причину и устранить

ШАГ 7: Если новая волна блокировок от ТСПУ
  → Сменить Path в inbound (/dl-vpn → /любой-другой-путь)
  → Обновить Nginx конфиг (location block)
  → Перевыпустить конфиги пользователям через бота
```

> ОШИБКА #12: После обновления 3x-ui или Xray пользователи отвалились
>
> ПРИЧИНА: Изменилась версия Xray-core — клиентские приложения стали несовместимы.
>
> НЕМЕДЛЕННЫЕ ДЕЙСТВИЯ:
> 1. Проверить версию: x-ui version
> 2. Разослать пользователям: "Пожалуйста обновите приложение v2RayTun до последней версии"
> 3. Если обновление клиента не помогает — откатить Xray:
>    В панели Settings → Xray Version → выбрать предыдущую версию → Restart
>
> ПРОФИЛАКТИКА:
> Перед обновлением 3x-ui — проверить на тестовом устройстве.
> Обновлять в нерабочее время (ночью по МСК).

---

## 10. ПЕРЕНОС СУЩЕСТВУЮЩИХ ПОЛЬЗОВАТЕЛЕЙ

### Наталья (native awg0)

НЕ ТРОГАТЬ. Наталья на отдельном интерфейсе (awg0, порт 41234), он никак не связан с новым стеком. Пусть работает как работает.

### Олег и другие пользователи на AWG Legacy

Они на Docker amnezia-awg2. Этот контейнер можно оставить работать — он никак не мешает новому стеку. Пользователей переводить постепенно:

1. Выдать им новый VLESS-конфиг через бота
2. Попросить проверить что работает
3. Если доволен — старый AWG-конфиг сам по себе устареет
4. Через месяц можно остановить Docker-контейнер amnezia-awg2

```bash
# Остановить AWG-контейнер когда все переведены
docker stop amnezia-awg2
# Не удалять сразу — пусть постоит как резерв
```

### Сергей (никогда не подключался)

Выдать VLESS-конфиг вместо AWG. Убедиться что у него установлен v2RayTun.

---

## 11. СВОДНАЯ ТАБЛИЦА ОШИБОК

| # | Симптом | Первопричина | Решение |
|---|---|---|---|
| #1 | "Address already in use" при Nginx | Конфликт на порту 80/443 | ss -tlnp → найти и остановить процесс |
| #2 | Панель 3x-ui не открывается | Порт закрыт, сервис не запущен | ufw allow PORT → x-ui start |
| #3 | Certbot "Challenge failed" | DNS не распространился, CF в Proxied | Ждать DNS, серое облако CF на время получения |
| #4 | xHTTP нет в списке транспортов | Устаревшая 3x-ui | x-ui update |
| #5 | Подключён, сайты не открываются | Sniffing выключен, нет routing | Включить Sniffing, настроить routing (шаг 4.3) |
| #6 | Логи Xray: routing errors | Path в клиенте ≠ Path в inbound | Проверить совпадение /dl-vpn везде |
| #7 | nginx -t ошибка | Неверные пути сертификатов, синтаксис | ls /etc/letsencrypt/live/ДОМЕН/ → исправить пути |
| #8 | Cloudflare 502 Bad Gateway | Nginx/Xray не работают, SSL mode | Проверить сервисы, установить Full (strict) в CF |
| #9 | Работает без CF, не через CF | Не packet-up, WebSockets выключен | Mode = packet-up, включить WebSockets в CF |
| #10 | Бот 401 от 3x-ui API | Неверные credentials, истекла сессия | Проверить .env, реализовать автоперереавторизацию |
| #11 | Hiddify не работает | Приложение заброшено разработчиком | Установить v2RayTun |
| #12 | Пользователи отвалились после обновления | Версия Xray изменилась | Уведомить обновить приложение, откатить Xray если нужно |

---

## 12. ЧЕКЛИСТ ПЕРЕД ЗАПУСКОМ

Пройти все пункты перед тем как запустить бота в production:

**СЕРВЕР**
```
[ ] apt upgrade выполнен
[ ] UFW: открыты 22, 80, 443, порт панели (47821)
[ ] 3x-ui установлен и работает (x-ui status = running)
[ ] Версия Xray в панели: 25.x+ (x-ui version)
[ ] Пароль панели сложный и сохранён в защищённом месте
```

**ДОМЕН И SSL**
```
[ ] Домен зарегистрирован, NS переведены на Cloudflare
[ ] A-запись: vpn.домен.com → 85.137.166.209, Proxied (оранжевое)
[ ] SSL/TLS Cloudflare: Full (strict)
[ ] WebSockets: On, gRPC: On, HTTP/2: On
[ ] Сертификат certbot получен, не истекает раньше 60 дней
```

**NGINX И XRAY**
```
[ ] nginx -t показывает "test is successful"
[ ] Nginx перезапущен после изменений (systemctl reload nginx)
[ ] VLESS+xHTTP inbound создан в панели
[ ] Mode: packet-up (не stream-up, не stream-one)
[ ] Path: /dl-vpn совпадает в inbound И в nginx location block
[ ] Sniffing: включён
[ ] Routing настроен: geoip:ru и geosite:ru → direct
```

**ТЕСТИРОВАНИЕ — ОБЯЗАТЕЛЬНО ДО ЗАПУСКА**
```
[ ] curl -I https://vpn.домен.com возвращает 200 и заголовок CF-RAY
[ ] Тестовый аккаунт создан через 3x-ui API (не вручную в панели)
[ ] Vless-ссылка открылась в v2RayTun на Android → Connected
[ ] YouTube 1080p работает без буферизации
[ ] Яндекс.ру открывается с российским IP (split tunneling работает)
[ ] dnsleaktest.com показывает не российские DNS-серверы
[ ] Тест с мобильного Билайн (самый важный кейс)
[ ] Тест с iOS через v2RayTun
```

**БОТ И АВТОМАТИЗАЦИЯ**
```
[ ] Конфликт 409 устранён: pkill -f datalink_pro_bot
[ ] Бот переведён на systemd (systemctl status datalink-bot = active)
[ ] Бот создаёт пользователя через 3x-ui API и выдаёт vless:// ссылку
[ ] ЮKassa вебхуки работают (тестовый платёж)
[ ] Пробный период (3 дня) выдаётся автоматически при /start
[ ] Инструкция для iPhone добавлена кнопкой в боте
```

**МОНИТОРИНГ**
```
[ ] UptimeRobot настроен на https://vpn.домен.com, уведомление в Telegram
[ ] Проверить через день что UptimeRobot реально шлёт уведомления (тест)
```

---

## ПРИЛОЖЕНИЕ: СПРАВОЧНЫЕ КОМАНДЫ

```bash
# Полный статус
x-ui status && systemctl status nginx && systemctl status datalink-bot

# Перезапуск Xray (если завис)
x-ui restart

# Перезапуск бота
systemctl restart datalink-bot

# Обновление 3x-ui (делать осторожно, в нерабочее время)
x-ui update

# Логи Xray (live)
x-ui logs -f

# Логи бота (live)
journalctl -u datalink-bot -f

# Логи Nginx (ошибки)
tail -50 /var/log/nginx/error.log

# Истечение SSL
certbot certificates

# Принудительное обновление SSL
certbot renew --force-renewal && systemctl reload nginx

# Проверить IP сервера
curl ifconfig.me

# Посмотреть занятые порты
ss -tlnp

# Место на диске
df -h

# Очистить логи Xray если разрослись
x-ui setting -logLevel error
# Перезапустить: x-ui restart
```

---

*DATALINK PRO | Технический документ v2.0 | Апрель 2026*
*Протокол: VLESS+xHTTP через Cloudflare CDN*
*Статус: Финальная версия для передачи инженерам*
