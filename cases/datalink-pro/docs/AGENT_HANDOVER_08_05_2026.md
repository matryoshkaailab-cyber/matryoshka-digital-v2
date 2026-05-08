# DATALINK PRO — ПОЛНЫЙ КОМПЛЕКТ ДАННЫХ ДЛЯ АГЕНТА
## Сервер: 85.137.166.209 | Дата: 08.05.2026 12:55

---

## 1. СЕРВЕР

**Хост:** s1562355.smartape-vps.com
**IP:** 85.137.166.209
**OS:** Ubuntu 24.04 LTS
**Kernel:** 6.8.0-107-generic
**Uptime:** 9 дней 22 часа
**RAM:** 7.8 GB (2.3 GB used, 5.5 GB available)
**Disk:** 50 GB (29 GB used, 18 GB available, 62%)
**CPU:** x86_64

**SSH доступ:**
```
ssh root@85.137.166.209
Пароль: R5t6y7u8i9o0
```

---

## 2. XRAY VLESS REALITY VPN

### Конфиг: /usr/local/x-ui/bin/config.json

```json
{
  "log": {
    "access": "/var/log/xray/access.log",
    "error": "/var/log/xray/error.log",
    "loglevel": "info"
  },
  "inbounds": [
    {
      "tag": "inbound-443-pc",
      "listen": "0.0.0.0",
      "port": 443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "28625ddc-ce9b-4086-b4b8-9a77b9a448ec",
            "flow": "xtls-rprx-vision",
            "email": "datalink-pc@vpn"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "www.speedtest.net:443",
          "xver": 0,
          "serverNames": ["www.speedtest.net", "speedtest.net"],
          "privateKey": "UKgNujpwM7vC_jONfuV-hn4YL_6dziNUTz6_Ey7QzVo",
          "shortIds": ["53f80cad0ac6a04b", ""]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    },
    {
      "tag": "inbound-2053-mobile",
      "listen": "0.0.0.0",
      "port": 2053,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "28625ddc-ce9b-4086-b4b8-9a77b9a448ec",
            "flow": "",
            "email": "datalink-mobile@vpn"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "dest": "www.speedtest.net:443",
          "xver": 0,
          "serverNames": ["www.speedtest.net", "speedtest.net"],
          "privateKey": "UKgNujpwM7vC_jONfuV-hn4YL_6dziNUTz6_Ey7QzVo",
          "shortIds": ["53f80cad0ac6a04b", ""]
        }
      },
      "sniffing": {
        "enabled": true,
        "destOverride": ["http", "tls", "quic"]
      }
    }
  ],
  "outbounds": [
    {"tag": "direct", "protocol": "freedom", "settings": {}},
    {"tag": "blocked", "protocol": "blackhole"}
  ],
  "routing": {
    "domainStrategy": "AsIs",
    "rules": [
      {"type": "field", "ip": ["geoip:private"], "outboundTag": "blocked"},
      {"type": "field", "protocol": ["bittorrent"], "outboundTag": "blocked"},
      {"type": "field", "network": "tcp,udp", "outboundTag": "direct"}
    ]
  }
}
```

### Ключи Reality
```
UUID: 28625ddc-ce9b-4086-b4b8-9a77b9a448ec
PrivateKey: UKgNujpwM7vC_jONfuV-hn4YL_6dziNUTz6_Ey7QzVo
PublicKey/PBK: KD3vWGJ-3ikGgncM405UpfGOLMVofZPiaAUU7ZHD6S8
ShortID: 53f80cad0ac6a04b
SNI: www.speedtest.net
```

### Порты
- 443 — ПК (flow: xtls-rprx-vision)
- 2053 — мобильный (flow: empty)

### Логи
- Access: /var/log/xray/access.log
- Error: /var/log/xray/error.log

### Xray Binary
/usr/local/x-ui/bin/xray-linux-amd64

### Генерация ключей
```bash
/usr/local/x-ui/bin/xray-linux-amd64 x25519
```

---

## 3. VPN BOT (Telegram)

**Bot:** @datalink_pro_bot
**Token:** 8349948703:AAFybtShN5Q6LlVM8nzUbEzTvQK1VrgAc5I
**Файл:** /opt/vpn_bot/bot.py
**База:** /opt/vpn_bot/users.db

### YooKassa
- Shop ID: 1313515
- Webhook: https://vpn.xn----7sbaowmfrljlq.xn--p1ai:8443/webhook/yookassa

### Тарифы
- 300₽/мес
- 800₽/3мес
- 1500₽/6мес

---

## 4. NGINX

**Папка:** /etc/nginx/sites-enabled/
**Сайты:**
- datalink — VPN сайт
- xray-fallback
- xray-xhttp
- cyber-kub
- hermes-dashboard

**SSL сертификаты:** /etc/letsencrypt/live/vpn.matryoshka-digital.ru/

---

## 5. MATRYOSHKA DIGITAL

**Папка:** /root/matryoshka/

**Структура:**
```
/root/matryoshka/
├── cases/
│   └── datalink-pro/
│       └── docs/
│           ├── FULL_ANALYSIS_08_05_2026.md
│           ├── DEADLOCK_ANALYSIS_08_05_2026.md
│           └── AMNEZIA_ANALYSIS_08_05_2026.md
├── matryoshka/
├── ecler/
├── legion/
└── VPN_BREAKPOINT_08_05_2026/
```

---

## 6. HERMES AGENT

**Конфиг:** /root/.hermes/config.yaml
**Секреты:** /root/.hermes/.env
**Профиль Эклер:** /root/.hermes/profiles/ecler/

**Подключение:**
- Telegram бот для Олега: @oleg_industry_bot
- Telegram ID Олега: 7453044462

---

## 7. ПРОБЛЕМА (ТЕКУЩАЯ)

**Статус VPN на 08.05.2026:**
- Порт 443 — НЕ РАБОТАЕТ (с 08.05 00:00)
- Порт 2053 — РАБОТАЕТ на WiFi, НЕ РАБОТАЕТ на мобильном
- Причина: ТСПУ блокирует Reality на мобильных сетях

**Логи показывают accepted подключения до 11:34, потом тишина.**

**Решение:** Переход на AmneziaWG

---

## 8. AMNEZIA WG (ПЛАН)

**GitHub:** https://github.com/bivlked/amneziawg-installer
**Docs:** https://docs.amnezia.org/ru/documentation/amnezia-wg

**Установка:**
```bash
sudo bash <(curl -s https://raw.githubusercontent.com/bivlked/amneziawg-installer/main/install_amneziawg.sh) --preset=mobile --port=51820 --route-all
```

**Управление:**
```bash
sudo bash /root/awg/manage_amneziawg.sh add client_name
sudo bash /root/awg/manage_amneziawg.sh list
sudo bash /root/awg/manage_amneziawg.sh backup
```

---

## 9. ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ

**Windows VPS (для SSH туннеля):**
- Host: WIN-OHDOM31GC8P
- User: user
- Password: Gfhjkm
- SSH туннель: `ssh -R 2222:localhost:22 user@85.137.166.209`

---

## ЗАДАЧИ ДЛЯ АГЕНТА

1. Изучить текущую конфигурацию Xray
2. Понять почему порт 443 не работает
3. Решить проблему с мобильным интернетом
4. Рассмотреть установку AmneziaWG как альтернативу
5. Подготовить рекомендации по улучшению VPN сервиса