# 🔍 SKILL: VPN Quick Status — Быстрая Проверка VPN

**Триггер:** vpn status, vpn check, vpn работает, статус VPN
**ОС:** Ubuntu 24.04 / AmneziaWG
**Статус:** ✅ ГОТОВ
**Версия:** 1.0 (28.04.2026)

---

## 🎯 НАЗНАЧЕНИЕ

Мгновенная проверка статуса VPN на сервере.

---

## ⚡ БЫСТРЫЙ CHECK

```bash
# Все в одном:
echo "=== VPN STATUS ===" && awg show 2>/dev/null && echo "" && echo "=== DUMP ===" && awg show dump 2>/dev/null && echo "" && echo "=== PING ===" && ping -c 2 -W 2 10.8.1.1 && echo "✓ VPN UP" || echo "✗ VPN DOWN"
```

---

## 📊 РЕЗУЛЬТАТЫ

### VPN UP (пример):
```
=== VPN STATUS ===
interface: awg0
  public key: zZJpQrQForeHQ+jV7OwdClrVybI7INGk1iiv7AzLwiw=
  private key: (hidden)
  listening port: 44206

peer: (unknown endpoint)
  allowed ips: 10.8.1.2/32
  persistent keepalive: every 35 seconds
✓ VPN UP
```

### VPN DOWN:
```
awg: show: Transport endpoint is not connected
✗ VPN DOWN
```

---

## 🔧 ЕСЛИ VPN DOWN

```bash
# Попробовать поднять
systemctl start awg-quick@awg0

# Проверить статус
systemctl status awg-quick@awg0

# Смотреть логи
journalctl -u awg-quick@awg0 -n 20 --no-pager

# Если не помогло — перезапустить
systemctl restart awg-quick@awg0
```

---

## 📱 ПРОВЕРКА С КЛИЕНТА

```bash
# ping до сервера VPN
ping -c 3 10.8.1.1

# Проверить туннель
curl --interface awg0 https://ipinfo.io/ip

# ДНС через VPN
nslookup google.com 10.8.1.1
```

---

## 📋 QUICK COMMANDS

| Команда | Что делает |
|---------|-----------|
| `awg show` | Статус интерфейса |
| `awg show dump` | Все пиры и их IP |
| `systemctl status awg-quick@awg0` | systemd статус |
| `ip addr show awg0` | IP адрес интерфейса |
| `ping -c 3 10.8.1.1` | Проверка связи |

---

**HERMES EDITION v1.0 © 2026**
