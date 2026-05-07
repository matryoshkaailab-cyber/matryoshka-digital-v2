# 🛡️ SKILL: AmneziaWG VPN — Полный Деплой

**Триггер:** VPN, AmneziaWG, wireguard, настроить VPN, развернуть VPN
**Протокол:** AmneziaWG (amneziawg)
**Статус:** ✅ ГОТОВ
**Версия:** 1.0 (28.04.2026)

---

## 🎯 НАЗНАЧЕНИЕ

Полное развёртывание AmneziaWG VPN сервера с нуля на Ubuntu 24.04.
Сервер: 85.137.166.209 | Порт: 44206 | Сеть: 10.8.1.0/24

---

## 🔧 УСТАНОВКА СЕРВЕРА

### 1. Установить AmneziaWG модуль ядра

```bash
# Проверить загрузку модуля
lsmod | grep amneziawg || modprobe amneziawg

# Если модуля нет — установить
apt update && apt install -y amneziawg

# Автозагрузка модуля
echo "amneziawg" > /etc/modules-load.d/amneziawg.conf
```

### 2. Генерация ключей сервера

```bash
awg genkey | tee /tmp/server_private.key | awg pubkey > /tmp/server_public.key
```

### 3. Конфиг сервера (/etc/amneziawg/awg0.conf)

```ini
[Interface]
Address = 10.8.1.1/24
ListenPort = 44206
PrivateKey = <PRIVATE_KEY>
Jc = 5
Jmin = 40
Jmax = 150
S1 = 95
S2 = 115
H1 = 1000015590
H2 = 1000030832
H3 = 1000023034
H4 = 1000024047
MTU = 1280
FwMark = 0xca6c
Table = off
PreUp = sysctl -w net.ipv4.ip_forward=1
PreUp = iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE
PostDown = iptables -t nat -D POSTROUTING -o ens3 -j MASQUERADE

[Peer]
PublicKey = <CLIENT_PUBLIC_KEY>
AllowedIPs = 10.8.1.2/32
PersistentKeepalive = 35
```

### 4. systemd сервис

```bash
# Установить пакет wireguard-tools (содержит awg-quick)
apt install -y wireguard-tools

# Создать юнит
cat > /etc/systemd/system/awg-quick@.service << 'EOF'
[Unit]
Description=AmneziaWG via awg-quick(8) for %I
After=network-online.target nss-lookup.target
Wants=network-online.target nss-lookup.target
Documentation=man:awg-quick(8)

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/awg-quick up %i
ExecStop=/usr/bin/awg-quick down %i
Environment=WG_QUICK_USERSPACE_IMPLEMENTATION=amneziawg GO朕NLIMIT=27
WatchdogSec=5s

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable awg-quick@awg0
systemctl start awg-quick@awg0
```

### 5. Проверка

```bash
awg show
ip addr show awg0
systemctl status awg-quick@awg0
```

---

## 👤 ДОБАВЛЕНИЕ КЛИЕНТА

### 1. На клиенте (если есть AmneziaWG клиент)

```bash
awg genkey | tee /tmp/client_private.key | awg pubkey > /tmp/client_public.key
```

### 2. На сервере — добавить Peer

```bash
# Добавить peer в конфиг
awg set awg0 peer <CLIENT_PUBLIC_KEY> allowed-ips 10.8.1.X/32 persistent-keepalive 35

# Или через конфиг:
# Добавить в /etc/amneziawg/awg0.conf:
# [Peer]
# PublicKey = <CLIENT_PUBLIC_KEY>
# AllowedIPs = 10.8.1.3/32
# PersistentKeepalive = 35
```

### 3. Клиентский конфиг (отдать клиенту)

```ini
[Interface]
Address = 10.8.1.X/24
PrivateKey = <CLIENT_PRIVATE_KEY>
Jc = 5
Jmin = 40
Jmax = 150
S1 = 95
S2 = 115
H1 = 1000015590
H2 = 1000030832
H3 = 1000023034
H4 = 1000024047
MTU = 1280

[Peer]
PublicKey = <SERVER_PUBLIC_KEY>
Endpoint = 85.137.166.209:44206
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 35
```

---

## 🗑️ УДАЛЕНИЕ КЛИЕНТА

```bash
# Удалить peer
awg set awg0 peer <CLIENT_PUBLIC_KEY> remove

# Проверить
awg show
```

---

## 📊 МОНИТОРИНГ

```bash
# Статус
awg show

# Активные пиры
awg show dump

# Логи
journalctl -u awg-quick@awg0 -f

# Проверка подключения
ping -c 3 10.8.1.1
```

---

## ⚠️ ВАЖНО

1. **Порт 44206** должен быть открыт в firewall
2. **IP Forwarding** должен быть включен (net.ipv4.ip_forward=1)
3. **MASQUERADE** в iptables для NAT
4. После изменений конфига — `awg-quick down awg0 && awg-quick up awg0`
5. Сервер не должен падать при ребуте — используй systemd сервис

---

**HERMES EDITION v1.0 © 2026**
