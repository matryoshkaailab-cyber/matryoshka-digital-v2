# 📊 SKILL: Server Health Check — Проверка Состояния

**Триггер:** health, status, check, мониторинг, проверить сервер
**ОС:** Ubuntu 24.04
**Статус:** ✅ ГОТОВ
**Версия:** 1.0 (28.04.2026)

---

## 🎯 НАЗНАЧЕНИЕ

Быстрая проверка состояния сервера: CPU, RAM, диски, сеть, сервисы, VPN.

---

## ▶️ ПОЛНЫЙ CHECK

```bash
# Сохрани как скрипт и запускай: bash health_check.sh

echo "═══════════════════════════════════════"
echo "  HERMES HEALTH CHECK"
echo "  $(date)"
echo "═══════════════════════════════════════"

echo ""
echo "【1/7】 UPTIME & LOAD"
uptime
echo ""

echo "【2/7】 CPU"
grep "model name" /proc/cpuinfo | head -1
echo "Load: $(cat /proc/loadavg)"
echo ""

echo "【3/7】 RAM"
free -h
echo ""

echo "【4/7】 DISKS"
df -h | grep -E "^/dev"
echo ""

echo "【5/7】 NETWORK"
echo "IP: $(hostname -I)"
ss -tlnp | grep LISTEN
echo ""

echo "【6/7】 SERVICES"
systemctl list-units --type=service --state=running --no-legend | grep -v systemd
echo ""

echo "【7/7】 VPN (AmneziaWG)"
awg show 2>/dev/null || echo "VPN не запущен"
echo ""

echo "═══════════════════════════════════════"
echo "  CHECK COMPLETE"
echo "═══════════════════════════════════════"
```

---

## ▶️ БЫСТРАЯ ПРОВЕРКА (2 сек)

```bash
uptime && free -h | grep Mem && df -h / | tail -1
```

---

## ▶️ CHECK СЕРВИСОВ

```bash
# Критические сервисы
for svc in sshd docker containerd systemd-resolved; do
  status=$(systemctl is-active $svc 2>/dev/null)
  echo "$svc: $status"
done

# Упавшие сервисы
systemctl list-units --state=failed --no-legend
```

---

## ▶️ CHECK VPN

```bash
# AmneziaWG
awg show
awg show dump

# Проверка туннеля
ip addr show awg0
ping -c 1 -W 2 10.8.1.1 && echo "VPN OK" || echo "VPN DOWN"
```

---

## ▶️ CHECK ДИСКА

```bash
# Занятость
df -h

# Топ директорий
du -sh /root/* 2>/dev/null | sort -rh | head -10
du -sh /var/* 2>/dev/null | sort -rh | head -10

# Inodes
df -i
```

---

## ▶️ CHECK СЕТИ

```bash
# Открытые порты
ss -tlnp

# Активные соединения
ss -an | grep ESTAB | wc -l

# Firewall
ufw status verbose 2>/dev/null || echo "UFW не установлен"
```

---

## ▶️ CHECK ЛОГОВ

```bash
# Последние ошибки
journalctl -p err -n 20 --no-pager

# SSH логи
tail -20 /var/log/auth.log

# Fail2Ban
fail2ban-client status 2>/dev/null || echo "Fail2Ban не установлен"
```

---

## 📊 ALERT THRESHOLDS

| Метрика | Warning | Critical |
|---------|---------|----------|
| CPU Load | > 5 | > 10 |
| RAM | > 80% | > 95% |
| Disk | > 80% | > 95% |
| Failed Services | > 0 | > 2 |

---

## ⚠️ ВАЖНО

1. **Запускай check** перед любыми изменениями на сервере
2. **Сохраняй результаты** — сравнивай с предыдущими
3. **VPN down?** — сначала `systemctl status awg-quick@awg0`
4. **CPU spike?** — `top` или `htop`

---

**HERMES EDITION v1.0 © 2026**
