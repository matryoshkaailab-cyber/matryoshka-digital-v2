# 🫡 SKILL: DATALINK PRO VPN — СЕРГЕЙ (АКТУАЛЬНО 13.04.2026)

**Версия:** 3.0
**Дата:** 13 апреля 2026 г.
**Статус:** ✅ БОТ v12 ГОТОВ ЛОКАЛЬНО (AmneziaWG .conf)

---

## 🔥 КРИТИЧЕСКИЕ ДАННЫЕ (13.04.2026)

### Сервер (ЕДИНСТВЕННЫЙ ИСТОЧНИК)
```
IP: 85.137.166.209 (Чехия, SmartApe)
SSH: root / Jktu22051987
```

### AmneziaWG (РАБОТАЕТ ✅)
```
Порт: 41234/UDP (НЕ 443!)
Интерфейс: awg0 (нативный, НЕ Docker!)
ServerPublicKey: r1H9WNYCogOjf/x+3eoo2OGhN6Qnt8LlhQc721OlsHM=
BLEICH: Jc=4, Jmin=84, Jmax=243, S1=35, S2=99, S3=24, S4=8
H1=100000-800000, H2=1000000-8000000, H3=10000000-80000000, H4=100000000-800000000
I1 = <r 256>
MTU: 1280, DNS: 1.1.1.1, Keepalive: 25
IP диапазон: 10.9.9.100-250 (бот), 10.9.9.2-99 (ручные)
```

### Бот v12 (АКТУАЛЬНЫЙ)
```
Локально: c:\matryoshka\sergey-vpn-czech\bot\datalink_pro_bot_v12.py
На сервере: НУЖНО ЗАГРУЗИТЬ /root/datalink_pro_bot_v12.py
Токен: 8349948703:AAFybtShN5Q6LlVM8nzUbEzTvQK1VrgAc5I
Бот: @datalink_pro_bot
База: /root/datalink_bot.db
Лог: /tmp/datalink_v12.log

Генерирует: AmneziaWG .conf (НЕ .vpnuri!)
Кнопки: 📱 Android, 🍏 iPhone, 💳 Тарифы, 🎁 Подарок 24ч, ℹ️ Помощь
```

### ЮKassa (БОЕВОЙ)
```
Shop ID: 1313515
Secret: live_SFDL2RtchjadJJPGKsjVtOuFWE0V9ho_8uPDzqz8zsM
Тарифы: 500₽/1000₽/2000₽
```

---

## 🎯 ГЛАВНАЯ ПРОБЛЕМА (РЕШЕНА)

**КОРЕНЬ:** Бот v11 генерировал VLESS .vpnuri → НЕ РАБОТАЕТ через Nginx stream
**РЕШЕНИЕ:** Бот v12 генерирует AmneziaWG .conf → РАБОТАЕТ (доказано Натальей)

### Доказательство работы (ПРЯМО С СЕРВЕРА, 13.04.2026):
| Пользователь | WiFi | Мобильный | Порт | Трафик |
|---|---|---|---|---|
| **Наталья** | ✅ | ✅ | 41234 | 229 MiB in / 2.56 GiB out |
| **Олег** | ✅ | ⚠️ тест keepalive=10 | 41234 | 57 MiB in / 613 MiB out |
| **Сергей** | ❌ | ❌ | (none) | 0, НИ РАЗУ НЕ ПОДКЛЮЧИЛСЯ |

---

## 🔧 ИНФРАСТРУКТУРА

### Docker контейнеры:
```bash
docker ps
# amnezia-awg (порт 49295/udp)
# mtproxy (порт 8443/tcp)
```

### Бот:
```bash
# Путь
/opt/vpn_bot/bot.py

# База данных
/opt/vpn_bot/users.db

# Логи
tail -f /tmp/bot.log

# Перезапуск
killall -9 python3
cd /opt/vpn_bot && nohup python3 bot.py > /tmp/bot.log 2>&1 &
```

### Проверка пиров:
```bash
docker exec amnezia-awg wg show
```

---

## 📝 ИСТОРИЯ ПОПЫТОК (ЧТОБЫ НЕ ПОВТОРЯТЬ)

### ❌ НЕ РАБОТАЛИ:
1. .conf файл — Amnezia не доверяет self-hosted
2. .json файл — Неправильная структура
3. vpn:// текст — Нет подписи
4. .vpn файл (indent=2) — Size header неверный
5. .vpn файл (size header) — port = int вместо str
6. .vpn файл (port=str) — Бот генерировал новые ключи

### ✅ РАБОТАЕТ:
**.vpn файл с правильной структурой + бот проверяет существующих пользователей**

---

## 🔑 КРИТИЧЕСКИЕ ФАЙЛЫ

### /opt/vpn_bot/bot.py

**Функция generate_keys:**
```python
def generate_keys():
    private_key = subprocess.check_output(["docker", "exec", CONTAINER, "wg", "genkey"]).decode().strip()
    public_key = subprocess.run(["docker", "exec", "-i", CONTAINER, "wg", "pubkey"], input=private_key.encode(), capture_output=True).stdout.decode().strip()
    return private_key, public_key
```

**Функция add_peer:**
```python
def add_peer(public_key, client_ip):
    subprocess.run(["docker", "exec", CONTAINER, "wg", "set", "awg0", "peer", public_key, "allowed-ips", client_ip + "/32"], capture_output=True)
    subprocess.run(["docker", "exec", CONTAINER, "wg-quick", "save", "awg0"], capture_output=True)
    return True
```

**Функция create_vpn_config (ИСПРАВЛЕНА!):**
```python
def create_vpn_config(user_id, username):
    # ПРОВЕРЯЕМ есть ли уже пользователь в БД
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT client_ip, public_key, private_key, expires_at FROM users WHERE user_id = ?", (user_id,))
    existing = cursor.fetchone()
    
    if existing:
        # Пользователь уже есть — возвращаем СТАРЫЕ ключи
        client_ip, public_key, private_key, expires_at = existing
        conn.close()
        return CONFIG_TEMPLATE.format(private_key=private_key, client_ip=client_ip), private_key, public_key, client_ip
    
    # Пользователя нет — генерируем НОВЫЕ ключи
    private_key, public_key = generate_keys()
    client_ip = get_next_ip()
    if not client_ip:
        conn.close()
        raise RuntimeError("IP exhausted")
    
    add_peer(public_key, client_ip)
    expires = (datetime.now() + timedelta(hours=24)).strftime("%d.%m.%Y %H:%M")
    cursor.execute("INSERT INTO users (user_id, username, client_ip, public_key, private_key, expires_at) VALUES (?, ?, ?, ?, ?, ?)", (user_id, username, client_ip, public_key, private_key, expires))
    conn.commit()
    conn.close()
    return CONFIG_TEMPLATE.format(private_key=private_key, client_ip=client_ip), private_key, public_key, client_ip
```

**Функция create_vpn_file:**
```python
def create_vpn_file(private_key, public_key, client_ip, preshared_key, server_ip, port):
    # Генерирует .vpn файл в формате AmneziaVPN
    # Структура: vpn://<Base64>(<4 байта size>+zlib(<JSON>))
    # size = len(json_bytes) (не compressed!)
    # indent=4 для JSON
    # port = str(port) (не int!)
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Проверка бота:
```bash
# 1. Запустить
cd /opt/vpn_bot && python3 bot.py &

# 2. Проверить процесс
pgrep -f 'python3 bot.py'

# 3. Проверить лог
tail -f /tmp/bot.log

# 4. Проверить БД
python3 -c "import sqlite3; conn=sqlite3.connect('/opt/vpn_bot/users.db'); print(conn.execute('SELECT * FROM users').fetchall())"
```

### Проверка сервера:
```bash
# 1. Проверить пиры
docker exec amnezia-awg wg show

# 2. Должны видеть:
# peer: <PUBLIC_KEY>
#   allowed ips: 10.8.1.X/32
#   latest handshake: X seconds ago
```

### Проверка подключения:
1. Открыть @datalink_pro_bot
2. Нажать `/start`
3. Нажать `🎁 Тест 24ч`
4. Должен прийти .vpn файл
5. Открыть в AmneziaVPN
6. Должно подключиться!

---

## 🚨 ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема 1: Бот не запускается
```bash
# Проверить синтаксис
python3 -m py_compile /opt/vpn_bot/bot.py

# Проверить логи
tail -f /tmp/bot.log

# Перезапустить
killall -9 python3
cd /opt/vpn_bot && nohup python3 bot.py > /tmp/bot.log 2>&1 &
```

### Проблема 2: Пир не добавляется
```bash
# Проверить wg show
docker exec amnezia-awg wg show

# Добавить вручную
docker exec amnezia-awg wg set awg0 peer <PUBLIC_KEY> allowed-ips 10.8.1.X/32 preshared-key <PSK>
docker exec amnezia-awg wg-quick save awg0
```

### Проблема 3: БД пустая
```bash
# Проверить через Python
python3 -c "import sqlite3; conn=sqlite3.connect('/opt/vpn_bot/users.db'); print(conn.execute('SELECT * FROM users').fetchall())"

# Если пустая — бот работает неправильно!
```

### Проблема 4: AmneziaVPN не подключается
1. Проверить что public_key из файла совпадает с peer на сервере
2. Проверить что пир добавлен (wg show)
3. Проверить что handshake был (latest handshake: X seconds ago)

---

## 📞 КОНТАКТЫ

**Клиент (Сергей):**
- Telegram Chat ID: 1951845052
- Username: @oleglab22

**Другие пользователи в БД:**
- 7453044462 (sergeiborodi) — 10.8.1.3
- 1951845052 (oleglab22) — 10.8.1.4

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

### Если всё работает:
1. ✅ Протестировать подключение с разных устройств
2. ✅ Проверить что трафик идёт
3. ✅ Добавить тарифы (1 мес, 3 мес, 6 мес, 12 мес)
4. ✅ Настроить автоматическое продление

### Если не работает:
1. ❌ Проверить совпадение ключей (БД vs wg show)
2. ❌ Проверить что пир активен (handshake)
3. ❌ Попробовать WireGuard Official вместо AmneziaVPN

---

## 💡 ЗАПОМНИТЬ НАВСЕГДА

1. **Бот должен проверять БД** перед генерацией ключей
2. **Size header = len(json_bytes)** (не compressed!)
3. **port = str(port)** (не int!)
4. **indent=4** для JSON
5. **client_pub_key = clientId**
6. **AmneziaVPN требует .vpn файл** (не .conf, не текст)

---

**🫡 ГОТОВ К РАБОТЕ!**

**При следующем запуске:**
1. Вспомнить этот контекст
2. Начать с того места где остановились
3. Не повторять ошибки
4. Использовать правильные команды
