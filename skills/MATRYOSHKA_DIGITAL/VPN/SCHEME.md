# VPN — Архитектура DATALINK PRO

## Сервер
```
IP:        85.137.166.209
ОС:        Ubuntu 24.04.4 LTS
Хостинг:   SmartApe (Чехия)
SSH:       root / Jktu22051987
```

## Два протокола одновременно

### Протокол 1: AmneziaWG (основной, работает)
```
Интерфейс:  awg0 (нативный, НЕ Docker!)
Порт:       41234/UDP
Подсеть:    10.9.9.0/24
Gateway:    10.9.9.1
MTU:        1280
DNS:        1.1.1.1
```
⚠️ Docker wireguard-go НЕ поддерживает BLEICH — только натив!

### Протокол 2: VLESS+REALITY (частично работает)
```
Порт внешний:  443/TCP (через Nginx Stream)
Порт локальный: 4443/TCP (127.0.0.1)
SNI:           github.com
Dest:          github.com:443
Flow:          xtls-rprx-vision
```
⚠️ Работает только на WiFi. На мобильных — connection reset.

## Nginx Stream маршрутизация
```
СЕРВЕР: 85.137.166.209:443
    │
    ├── SNI = github.com  →  127.0.0.1:4443 (Xray REALITY)
    └── SNI = default     →  127.0.0.1:8444 (Flask сайт)
```

## Порты на сервере
| Порт | Протокол | Сервис | Статус |
|------|----------|--------|--------|
| 443 | TCP | Nginx Stream | ✅ |
| 41234 | UDP | AmneziaWG awg0 | ✅ |
| 4443 | TCP | Xray REALITY | ✅ |
| 8444 | TCP | Flask сайт | ✅ |
| 22 | TCP | SSH | ✅ |

## Команда и пиры
```
awg show awg0  — посмотреть все пиры
```

| IP | Имя | Статус |
|----|-----|--------|
| 10.9.9.2 | oleg | ✅ WiFi |
| 10.9.9.3 | sergey | ❌ не подключался |
| 10.9.9.4 | sergeiborodi | ⚪ неактивен |
| 10.9.9.5 | NatalyaChut | ✅ |
| 10.9.9.10+ | trial_* | ⚪ триал |
| 10.9.9.18 | tasya | ✅ активен |
