# ЗАДАЧА №001 — AmneziaWG Setup
## Дата: 08.05.2026
## Статус: Ожидает выполнения

---

## ТИТУЛ
Установить AmneziaWG на сервер 85.137.166.209

---

## ПРИОРИТЕТ: HIGH
Дедлайн: 08.05.2026

---

## КОНТЕКСТ

VPN (VLESS Reality) работает только на WiFi. На мобильном — блокирует ТСПУ ( DPI). AmneziaWG — решение которое обходит DPI.

---

## ДАННЫЕ СЕРВЕРА

```
IP: 85.137.166.209
SSH Port: 22
User: root
Password: R5t6y7u8i9o0
```

---

## ЗАДАЧИ

1. Подключиться к серверу
2. Установить AmneziaWG (one-command install)
3. Настроить preset=mobile (для российских операторов)
4. Порт: UDP 51820
5. Проверить работу с мобильного интернета

---

## КОМАНДА УСТАНОВКИ

```bash
sudo bash <(curl -s https://raw.githubusercontent.com/amnezia-vpn/amnezia-wg-install/master/install.sh) --preset=mobile --port=51820 --route-all
```

---

## ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

1. AmneziaWG установлен и работает
2. VPN подключается с мобильного интернета (не только WiFi)
3. Создан конфиг для клиента
4. Результат записан в `/root/matryoshka/results/result_001.md`

---

## ПРОВЕРКА

После установки проверить:
```bash
wg show
ss -ulnp | grep 51820
```

---

## КОНТАКТЫ

Еси вопросы — @oleg_industry_bot (Hermes)