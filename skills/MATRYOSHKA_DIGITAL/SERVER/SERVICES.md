# SERVER — Сервисы и контейнеры

## Systemd сервисы
```bash
# VPN
systemctl status amneziawg   # AmneziaWG
systemctl status xray        # VLESS/REALITY

# Веб
systemctl status nginx       # Nginx (SNI routing)
systemctl status flask       # Если есть

# Защита
systemctl status fail2ban    # SSH защита
```

## Docker контейнеры
```bash
ssh vpn-serger "docker ps"
```
⚠️ Docker wireguard-go НЕ поддерживает AmneziaWG BLEICH!

## Управление
```bash
# Рестарт сервиса
ssh vpn-serger "systemctl restart <service>"

# Логи journalctl
ssh vpn-serger "journalctl -u <service> -n 50 --no-pager"

# Автозагрузка
ssh vpn-serger "systemctl enable <service>"
```

## Логи
```bash
# VPN
ssh vpn-serger "awg show awg0"                    # пиры
ssh vpn-serger "tail -50 /tmp/datalink_v12.log"  # бот

# Nginx
ssh vpn-serger "tail -30 /var/log/nginx/error.log"

# Xray
ssh vpn-serger "journalctl -u xray -n 50"
```

## Ресурсы
```bash
ssh vpn-serger "htop"
ssh vpn-serger "df -h"
ssh vpn-serger "free -h"
```
