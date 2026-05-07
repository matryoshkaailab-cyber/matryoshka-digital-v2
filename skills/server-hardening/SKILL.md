# 🔒 SKILL: Server Hardening — Безопасность Сервера

**Триггер:** security, harden, ssh, firewall, fail2ban, защита
**ОС:** Ubuntu 24.04
**Статус:** ✅ ГОТОВ
**Версия:** 1.0 (28.04.2026)

---

## 🎯 НАЗНАЧЕНИЕ

Быстрая настройка базовой безопасности сервера: SSH, firewall, обновления.

---

## 1. SSH Hardening

### /etc/ssh/sshd_config

```bash
# Обязательные настройки:
Port 22                                 # сменить на нестандартный
PermitRootLogin no                      # запрет root логина
PasswordAuthentication no               # только ключи
PubkeyAuthentication yes                # ключи обязательно
MaxAuthTries 3                          # макс 3 попытки
ClientAliveInterval 300                  # alive каждые 5 мин
ClientAliveCountMax 2                   # 2 проверки перед disconnect
X11Forwarding no                        # отключить X11
AllowUsers root                         # только root

# Дополнительно:
LoginGraceTime 60
StrictModes yes
MaxSessions 10
```

### Перезагрузка SSH

```bash
systemctl restart sshd
```

⚠️ **ВНИМАНИЕ:** Менять порт SSH опасно если нет альтернативного доступа!

---

## 2. Firewall (UFW)

```bash
# Установить
apt install -y ufw

# Правила по умолчанию
ufw default deny incoming
ufw default allow outgoing

# Открыть нужные порты
ufw allow 22/tcp          # SSH (если стандартный порт)
ufw allow 443/tcp         # WireGuard/AmneziaWG
ufw allow 80/tcp          # HTTP (для certbot)

# Включить
ufw enable

# Проверить
ufw status verbose
```

---

## 3. Fail2Ban

```bash
# Установить
apt install -y fail2ban

# Включить защиту SSH
cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
findtime = 600
action = iptables-allports
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Проверить статус
fail2ban-client status
fail2ban-client status sshd
```

---

## 4. Автообновления

```bash
# Установить unattended-upgrades
apt install -y unattended-upgrades

# Включить автообновления безопасности
dpkg-reconfigure -plow unattended-upgrades

# Проверить
cat /etc/apt/apt.conf.d/50unattended-upgrades
```

---

## 5. Защита от DDoS (базовая)

```bash
# SYN flood protection
echo 1 > /proc/sys/net/ipv4/tcp_syncookies

# Добавить в /etc/sysctl.conf:
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Применить
sysctl -p
```

---

## 6. Проверка

```bash
# Открытые порты
ss -tlnp

# Активные соединения
ss -s

# Логи SSH
tail -50 /var/log/auth.log | grep sshd

# Логи fail2ban
tail -50 /var/log/fail2ban.log
```

---

## ⚠️ ВАЖНО

1. **Менять порт SSH** — только если есть console/IPMI доступ
2. **Отключать password auth** — только после проверки что ключ работает
3. **Fail2Ban** — проверить что не заблокирует тебя сам
4. ** Firewall** — всегда держать SSH порт открытым

---

**HERMES EDITION v1.0 © 2026**
