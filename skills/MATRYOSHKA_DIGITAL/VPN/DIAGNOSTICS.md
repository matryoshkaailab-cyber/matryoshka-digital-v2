# VPN — Диагностика и решения

## Быстрая диагностика

### 1. Проверить все пиры
```bash
ssh vpn-serger "awg show awg0"
```

### 2. Проверить бота
```bash
ssh vpn-serger "ps aux | grep datalink | grep -v grep"
```

### 3. Логи бота
```bash
ssh vpn-serger "tail -50 /tmp/datalink_v12.log"
```

### 4. Статус Xray
```bash
ssh vpn-serger "systemctl status xray"
```

---

## Известные проблемы и решения

### ❌ Олег на мобильном — CGNAT
**Симптом:** Handshake есть, но данные не идут (только keepalive)
**Причина:** Билайн использует CGNAT через Cloudflare — UDP сессии убиваются
**Решение:**
1. PersistentKeepalive=10 (уменьшить с 33)
2. Попробовать другой порт
3. Предложить сменить оператора (Теле2, Мегафон)

### ❌ Сергей не подключается
**Симптом:** endpoint: (none), handshake нет
**Причина:** Использовал конфиг с портом 443 вместо 41234
**Решение:**
1. Выдать новый конфиг с портом 41234
2. Убедиться что приложение = AmneziaWG (НЕ AmneziaVPN!)

### ❌ VLESS не работает на мобильных
**Симптом:** Connection reset by peer
**Причина:** Nginx ssl_preread ломает mux соединения
**Решение:** VLESS через Nginx нестабилен. Использовать AmneziaWG.

### ❌ Docker amnezia-awg не работает
**Симптом:** BLEICH параметры не применяются
**Причина:** wireguard-go в Docker не поддерживает AmneziaWG ядро
**Решение:** Только нативный awg0!

---

## Проверка клиента
```bash
# На сервере
ssh vpn-serger "awg show awg0 | grep <PubKey>"

# Если endpoint = (none) — клиент не подключался
# Если handshake "вечен" — клиент подключен но спит
# Если трафик растёт — всё работает
```

## Добавить нового клиента
1. Через бота @datalink_pro_bot (автоматически)
2. Вручную:
```bash
ssh vpn-serger
awg genkey
awg pubkey
# Добавить в awg0.conf:
awg set awg0 peer <PubKey> allowed-ips 10.9.9.X/32
```
