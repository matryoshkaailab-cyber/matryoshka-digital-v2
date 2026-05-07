# SERVER — Доступ и порты

## Главный сервер VPN
```
IP:           85.137.166.209
Хостинг:      SmartApe (Host-Telecom, Чехия)
SSH login:    root
SSH password: Jktu22051987
SSH key:     C:\lab\vpn_matryoshka_key
SSH alias:   vpn-serger (в ~/.ssh/config)
```

## SSH подключение
```bash
# Через ключ (рекомендуется)
ssh -i C:/lab/vpn_matryoshka_key root@85.137.166.209

# Через alias (если настроен)
ssh vpn-serger
```

## Порты и сервисы
| Порт | Сервис | Назначение |
|------|--------|------------|
| 22 | SSH | Управление |
| 443 | TCP | Nginx (SNI routing) |
| 41234 | UDP | AmneziaWG VPN |
| 4443 | TCP | Xray REALITY (локально) |
| 8444 | TCP | Flask сайт (локально) |

## Проверка портов
```bash
ssh vpn-serger "ss -tlnp | grep -E '22|443|41234'"
```

## Firewall (UFW)
```bash
ssh vpn-serger "ufw status"
ssh vpn-serger "ufw allow 22/tcp"
ssh vpn-serger "ufw allow 443/tcp"
ssh vpn-serger "ufw allow 41234/udp"
```
