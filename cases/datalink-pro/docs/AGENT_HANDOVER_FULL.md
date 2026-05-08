# ПОЛНЫЙ КОМПЛЕКТ ДАННЫХ ДЛЯ АГЕНТА КИМ2,6
## Сервер: 85.137.166.209 | Дата: 08.05.2026

---

## 1. СЕРВЕР VPS

```
IP: 85.137.166.209
Host: s1562355.smartape-vps.com
OS: Ubuntu 24.04 LTS
RAM: 7.8 GB
Disk: 50 GB
SSH Port: 22
Пароль: R5t6y7u8i9o0
```

**Подключение:**
```bash
ssh root@85.137.166.209
# пароль: R5t6y7u8i9o0
```

---

## 2. СТРУКТУРА ПРОЕКТОВ

```
/root/matryoshka/
├── cases/
│   └── datalink-pro/          ← VPN проект
│       ├── bot/               ← Telegram бот
│       └── docs/              ← Документация
├── matryoshka/                ← Основной проект MATRYOSHKA DIGITAL
├── ecler/                     ← Ассистент Эклер (для Натальи)
└── legion/                    ← VR клуб Легион
```

---

## 3. VPN DATALINK PRO

### Текущий конфиг Xray:
```
Ports: 443, 2053
UUID: 28625ddc-ce9b-4086-b4b8-9a77b9a448ec
PrivateKey: UJAUyqjT2CvAmsthrC3y46m0VATjYF8SkXVEBRdvIGE
SNI: www.speedtest.net, speedtest.net
Protocol: VLESS Reality Vision
```

### Файлы:
- Xray config: `/usr/local/x-ui/bin/config.json`
- VPN bot: `/opt/vpn_bot/bot.py`
- VPN bot DB: `/opt/vpn_bot/users.db`
- Xray binary: `/usr/local/x-ui/bin/xray-linux-amd64`

### Бот Telegram:
- Bot: @datalink_pro_bot
- Token: 8349948703:AAFybtShN5Q6LlVM8nzUbEzTvQK1VrgAc5I

### YooKassa:
- Shop ID: 1313515
- Webhook URL: https://vpn.xn----7sbaowmfrljlq.xn--p1ai:8443/webhook/yookassa

### Проблема:
VPN (Reality) работает только на WiFi. На мобильном — блокирует ТСПУ.
Рекомендация: Установить AmneziaWG (port UDP 51820).

---

## 4. HERMES AGENT (мой)

```
Версия: v0.13 "Tenacity"
Конфиг: /root/.hermes/config.yaml
Папка: /usr/local/lib/hermes-agent/
```

**Важно:**
- При изменении конфига — перезапустить gateway
- Tool changes требуют новую сессию

**Kanban:**
```bash
hermes kanban --board default ls     # список задач
hermes kanban --board default create "Задача" --triage
hermes kanban --board default assign TSK_ID profile
hermes kanban --board default complete TSK_ID
```

---

## 5. GITHUB

```
Репозиторий: https://github.com/matryoshkaailab-cyber/matryoshka-digital-v2
Организация: matryoshkaailab-cyber
SSH: git@github.com:matryoshkaailab-cyber/matryoshka-digital-v2.git
```

**SSH ключ агента добавлен:**
```
sk-cp-rgJLDtTJARiNU37fEeAc6go8_vWpkv_onjQjdgMjvaAxT5xdFSCfYktOBLXfPjrh2l8jQEv82ph0IFCqo-ycgnmB9m_A5N3F5bbWBzUPeho6ZbQ6gW_HZgk
```

---

## 6. SSH КЛЮЧИ НА СЕРВЕРЕ

```
/root/.ssh/authorized_keys   ← все авторизованные ключи
/root/.ssh/id_rsa            ← мой приватный ключ
```

---

## 7. КОМАНДЫ АГЕНТА

### Перезапустить Xray:
```bash
pkill xray; sleep 1; /usr/local/x-ui/bin/xray-linux-amd64 run -c /usr/local/x-ui/bin/config.json &
```

### Перезапустить бота:
```bash
pkill -f bot.py; cd /opt/vpn_bot && python3 bot.py &
```

### Проверить статус:
```bash
ps aux | grep xray | grep -v grep
ps aux | grep bot.py | grep -v grep
ss -tlnp | grep -E '443|2053|8443'
```

### Логи:
```bash
tail -50 /var/log/xray/access.log
tail -30 /var/log/xray/error.log
```

---

## 8. ВАЖНЫЕ ПРАВИЛА

1. **x-ui перезаписывает конфиг** — kill x-ui перед изменением config.json
2. **Терминал блокирует redirects** — используй write_file/read_file вместо echo/cat >>
3. **При падении VPN** — чинить немедленно, это критично для клиентов
4. **Персональные данные** — только на сервере РФ, не отправлять во внешние AI

---

## 9. ПЛАН РАБОТ

Текущие задачи в Kanban:
```
t_9c3a012d  triage    Починить VPN на мобильном (ТСПУ)
t_abd23cac  ready     Обновить SOUL.md с новыми правилами v0.13  
t_12ea3930  triage    Установить AmneziaWG на сервер
```

Приоритет: AmneziaWG для решения проблемы с мобильными.

---

## 10. АРХИТЕКТУРА АГЕНТОВ MATRYOSHKA

```
                        ОЛЕГ
                          ↓
                🎼 HERMES (я)
                          ↓
        ┌─────────┬─────────┬─────────┐
        ↓         ↓         ↓         ↓
     Эклер     Ким2,6    Алекс    Алина
   (Наталья)  (новый)   (коорд.) (продажи)
```

---

**Файл для агента:** `/root/matryoshka/cases/datalink-pro/docs/AGENT_HANDOVER_FULL.md`