# 💾 SKILL: Server Backup — Бэкап Конфигов

**Триггер:** backup, бэкап, архив, сохранить конфиги
**ОС:** Ubuntu 24.04
**Статус:** ✅ ГОТОВ
**Версия:** 1.0 (28.04.2026)

---

## 🎯 НАЗНАЧЕНИЕ

Быстрый бэкап критичных конфигов сервера в архив.

---

## 📦 ЧТО БЭКАПИМ

```bash
# Основные конфиги
/etc/amneziawg/           # AmneziaWG конфиги
/etc/ssh/sshd_config     # SSH
/etc/fail2ban/            # Fail2Ban
/etc/iptables/            # Firewall правила
/etc/systemd/system/     # SystemD сервисы
/root/.env               # Переменные окружения
/root/matryoshka/        # Проекты
/root/.hermes/           # Hermes конфиг и память
/etc/letsencrypt/        # SSL сертификаты
```

---

## 🚀 БЫСТРЫЙ БЭКАП

```bash
# Создать бэкап
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

tar czf $BACKUP_DIR/backup_$DATE.tar.gz \
  /etc/amneziawg/ \
  /etc/ssh/sshd_config \
  /etc/systemd/system/vpnbot.service \
  /root/.env \
  /root/matryoshka/ \
  /root/.hermes/config.yaml \
  /root/.hermes/SOUL.md \
  /etc/letsencrypt/ 2>/dev/null

echo "✓ Бэкап: $BACKUP_DIR/backup_$DATE.tar.gz"
ls -lh $BACKUP_DIR/
```

---

## 📤 ВЫГРУЗКА НА ЯНДЕКС.ДИСК

```bash
# Уже настроен WebDAV
WEBDAV_URL="https://webdav.yandex.ru"
YANDEX_EMAIL="matryoshka.lab@yandex.com"
YANDEX_PASS="cotlqepqqgoxfhdc"
BACKUP_FILE="/root/backups/backup_$(date +%Y%m%d).tar.gz"

# Загрузить
curl -u "$YANDEX_EMAIL:$YANDEX_PASS" \
  -T $BACKUP_FILE \
  "$WEBDAV_URL/Backups/"

echo "✓ Выгружено на Яндекс.Диск"
```

---

## 📥 ВОССТАНОВЛЕНИЕ

```bash
# Извлечь архив
tar xzf /root/backups/backup_YYYYMMDD_HHMMSS.tar.gz -C /

# Или конкретный файл
tar xzf /root/backups/backup_20260428.tar.gz etc/amneziawg/awg0.conf
```

---

## 🔄 АВТОБЭКАП (cron)

```bash
# Добавить в crontab: бэкап каждую ночь в 3:00
0 3 * * * tar czf /root/backups/backup_$(date +\%Y\%m\%d).tar.gz /etc/amneziawg/ /root/.env /root/matryoshka/ /root/.hermes/config.yaml 2>/dev/null
```

---

## ⚠️ ВАЖНО

1. **Храни бэкапы локально** — минимум 3 последних
2. **Выгружай на облако** — Яндекс.Диск, S3 и т.д.
3. **Не бэкапь всё подряд** — только критичное
4. **Проверяй архивы** — убедись что распаковывается

---

**HERMES EDITION v1.0 © 2026**
