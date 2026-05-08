# AMNEZIA VPN — ГЛУБОКИЙ АНАЛИЗ
## Дата: 08.05.2026 | Для: DATALINK PRO

---

## 1. ЧТО ТАКОЕ AMNEZIA VPN

**AmneziaVPN** — это open-source VPN решение, которое позволяет развернуть собственный VPN сервер на VPS за 20 минут.

**Ключевое отличие от Xray/VLESS Reality:** AmneziaWG — форк WireGuard с обфускацией трафика для обхода DPI (Deep Packet Inspection).

---

## 2. PROTOKOL AMNEZIAWG

### WireGuard — проблема

Обычный WireGuard легко детектируется DPI системами из-за:
- Фиксированных заголовков пакетов
- Предсказуемых размеров пакетов
- Характерных "подписей" в трафике

### AmneziaWG — решение

AmneziaWG 2.0 изменяет заголовки ВСЕХ пакетов:
- DPI видит хаотичную последовательность UDP-пакетов
- Заголовки непредсказуемы
- Размеры пакетов рандомизированы
- handshake размыт
- Уникальные сигнатуры на каждого пользователя

---

## 3. ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ AMNEZIAWG 2.0

### Динамические заголовки (H1-H4)

| Header | Применяется к | Описание |
|--------|---------------|----------|
| H1 | Init packet | Значение из настроенного диапазона |
| H2 | Response packet | Значение из настроенного диапазона |
| H3 | Cookie packet | "Magic" header вместо 32-bit message type |
| H4 | Data packet | Значение из настроенного диапазона |

**Важно:** Диапазоны H1-H4 НЕ должны пересекаться между собой.

### Рандомизация размеров пакетов (S1-S4)

| Тип пакета | Оригинальный размер | Формула |
|------------|---------------------|---------|
| Init | 148 bytes | 148 + S1 |
| Response | 92 bytes | 92 + S2 |
| Cookie | 64 bytes | 64 + S3 |
| Data | Variable | payload + S4 |

### Маскировка пакетов (CPS — Custom Protocol Signature)

Перед каждым handshake (каждые 120 секунд) клиент может отправлять до 5 разных UDP пакетов, описанных в формате CPS.

**Формат CPS:**
```
i{n} = <tag1><tag2><tag3>...<tagN>
```

**Типы тегов:**

| Тег | Формат | Описание | Пример |
|-----|--------|----------|--------|
| b | `<b hex_data>` | Статичные байты | `<b 0xf6ab3267fa>` |
| t | `<t>` | Unix timestamp | Unix время |
| r | `<r length>` | Случайные байты (криптостойкие) | `<r 20>` |
| rc | `<rc N>` | Случайные ASCII буквы | `<rc 10>` → "aBcDeFgHiJ" |
| rd | `<rd N>` | Случайные цифры | `<rd 5>` → "13654" |

### Junk-train (Jc)

После цепочки I-пакетов отправляются псевдо-случайные пакеты размером от Jmin до Jmax байт. Это размывает начало сессии.

---

## 4. ПАРАМЕТРЫ КОНФИГУРАЦИИ

### Все параметры AWG 2.0

| Параметр | Диапазон | Описание |
|----------|----------|----------|
| Jc | 3-6 | Количество junk-пакетов |
| Jmin | 40-89 bytes | Минимальный размер junk |
| Jmax | Jmin+50..Jmin+250 | Максимальный размер junk |
| S1 | 15-150 bytes | Padding Init-сообщения |
| S2 | 15-150 bytes | Padding Response-сообщения |
| S3 | 8-55 bytes | Padding Cookie-сообщения |
| S4 | 4-27 bytes | Padding Data-сообщения |
| H1-H4 | uint32 range | Идентификаторы сообщений |
| I1-I5 | CPS format | Пакеты маскировки |

**Важно:** S1 + 56 ≠ S2 (критическое ограничение)

---

## 5. PRESETS (ГОТОВЫЕ НАБОРЫ)

### preset=default
- Jc: 3-6 (случайно)
- Jmin: 40-89
- Jmax: Jmin+50..250
- **Использование:** Домашний WiFi, стандартный VPS

### preset=mobile
- Jc: 3 (фиксировано)
- Jmin: 30-50
- Jmax: Jmin+20..80
- **Использование:** Мобильные операторы (Tele2, Yota, Megafon, Beeline)

**Если VPN работает на WiFi но нестабилен на мобильном — переустановить с --preset=mobile**

---

## 6. УСТАНОВКА НА СЕРВЕР (85.137.166.209)

### Скрипт: bivlked/amneziawg-installer

**One-command установка:**
```bash
sudo bash <(curl -s https://raw.githubusercontent.com/bivlked/amneziawg-installer/main/install_amneziawg.sh) --preset=mobile
```

**Полный список опций:**
```bash
--port=PORT         # UDP порт (1024-65535)
--preset=TYPE       # default или mobile
--jc=N              # 1-128 junk packets
--jmin=N            # 0-1280 bytes
--jmax=N            # 0-1280 bytes
--route-all         # Весь трафик через VPN
--route-amnezia     # Только Amnezia + DNS (по умолчанию)
--endpoint=IP       # Внешний IP (для NAT серверов)
--yes               # Неинтерактивный режим
--no-tweaks         # Пропустить hardening
```

### Управление

```bash
# Добавить клиента
sudo bash /root/awg/manage_amneziawg.sh add client_name

# Удалить клиента
sudo bash /root/awg/manage_amneziawg.sh remove client_name

# Список клиентов
sudo bash /root/awg/manage_amneziawg.sh list

# Бэкап
sudo bash /root/awg/manage_amneziawg.sh backup

# Проверка статуса
sudo bash /root/awg/manage_amneziawg.sh check
```

---

## 7. КЛИЕНТЫ AMNEZIA VPN

### Доступные платформы
- **Windows** — AmneziaWG client
- **macOS** — AmneziaVPN app
- **Linux** — AmneziaVPN app
- **Android** — AmneziaVPN (Google Play / APK)
- **iOS** — AmneziaVPN (App Store)

### Как подключиться
1. Установить приложение AmneziaVPN
2. Отсканировать QR код или ввести конфиг вручную
3. Подключиться

---

## 8. ПРЕИМУЩЕСТВА AMNEZIAWG ПЕРЕД VLESS REALITY

| Критерий | VLESS Reality | AmneziaWG |
|----------|---------------|-----------|
| Обход DPI | Частично (SNI mismatch) | Полностью (TRAFFIC не детектируется) |
| Мобильные сети | Проблемы с ТСПУ | Работает с preset=mobile |
| Настройка | Сложная (ключи, конфиги) | Простая (скрипт一键安装) |
| Клиент | v2rayNG (сложно) | AmneziaVPN (удобно) |
| Скорость | Высокая | Высокая |
| Стабильность | Зависит от ТСПУ | Более стабильная |

---

## 9. PLAN РАЗВЕРТЫВАНИЯ

### Шаг 1: Установить AmneziaWG
```bash
sudo bash <(curl -s https://raw.githubusercontent.com/bivlked/amneziawg-installer/main/install_amneziawg.sh) --preset=mobile --port=51820 --route-all
```

### Шаг 2: Создать клиента
```bash
sudo bash /root/awg/manage_amneziawg.sh add oleg_mobile
```

### Шаг 3: Получить конфиг
Конфиг сохраняется в `/root/awg/clients/`

### Шаг 4: Передать конфиг клиенту
QR код или файл конфига

---

## 10. ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После установки AmneziaWG:
- ✅ Полный обход DPI на мобильных сетях
- ✅ Работает на Beeline, Tele2, Yota, Megafon
- ✅ Простая настройка через скрипт
- ✅ Удобный клиент для пользователей
- ✅ Нет проблем с "server name mismatch"

---

## 11. ФАЙЛЫ И ДОКУМЕНТАЦИЯ

- GitHub: https://github.com/bivlked/amneziawg-installer
- Docs: https://docs.amnezia.org/ru/documentation/amnezia-wg
- AmneziaVPN: https://amnezia.org

---

**Следующий шаг:** Запустить установку AmneziaWG на сервере?