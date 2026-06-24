# WebDAV + Obsidian Sync — диагностика и план починки

**Дата:** 15.06.2026 | **Срочность:** P0 (по запросу Олега)

---

## 1. ДИАГНОСТИКА (что РАБОТАЕТ)

✅ **WebDAV сервер РАБОТАЕТ на 8181 (TLS)**
- Nginx слушает 0.0.0.0:8181 (9 workers)
- SSL: self-signed `/etc/nginx/ssl/obsidian.{crt,key}`
- Basic auth: логин `hermes`, пароль в `/etc/nginx/.obsidian-htpasswd`
- Vault: `/root/obsidian-vault/` (2.9 MB, www-data)

✅ **ДОСТУП ИЗ ВСЕХ ТОЧЕК:**
- `http://127.0.0.1:8181/` → 401 (auth required, OK)
- `https://10.8.1.1:8181/` (через AWG) → 401 ✅
- `https://85.137.166.209:8181/` (прямой IP) → 401 ✅
- `https://xn----7sbaowmfrljlq.xn--p1ai:8181/` (домен) → 401 ✅

❌ **Obsidian Sync НЕ настроен в плагине**
- `/root/obsidian-vault/.obsidian/` — пустой
- Нет конфига "Remotely Save" / "Self-hosted LiveSync"
- Содержимое vault: только системные папки (alex_tasks symlink, agents/)

---

## 2. ЧТО СЛОМАЛОСЬ 09.06.2026

**Гипотеза:** Олег настраивал Obsidian Sync через community-плагин "Remotely Save", но:
- Или поменял URL/логин/пароль
- Или обновил Obsidian и конфиг сбросился
- Или sync-папка не совпадает с vault-папкой

**Доказательства:**
- Vault существует (2.9 MB) — не удалён
- WebDAV отвечает 401 из всех точек — auth правильный
- Плагин конфиг отсутствует в vault

---

## 3. ПЛАН ПОЧИНКИ (30 мин)

### 3.1 Шаг 1: Включить Remotely Save (Олег на ПК)

1. Открыть Obsidian на ПК
2. Settings → Community plugins → Browse → "Remotely Save"
3. Install + Enable
4. Settings → Remotely Save:
   - **Choose a Remote Service:** WebDAV (custom)
   - **Server Address:** `https://85.137.166.209:8181`
   - **Username:** `hermes`
   - **Password:** (из `/etc/nginx/.obsidian-htpasswd` на VPS)
   - **Auth Type:** Basic
   - **Enable Auto Sync:** ON (каждые 5 мин)

### 3.2 Шаг 2: Заменить self-signed на Let's Encrypt (10 мин на VPS)

Сейчас SSL self-signed → Obsidian будет ругаться на "untrusted certificate".

```bash
# Установить certbot (если нет)
apt install -y certbot

# Получить сертификат для vpn.xn----7sbaowmfrljlq.xn--p1ai
certbot certonly --standalone -d vpn.xn----7sbaowmfrljlq.xn--p1ai

# Скопировать в nginx
cp /etc/letsencrypt/live/vpn.xn----7sbaowmfrljlq.xn--p1ai/fullchain.pem /etc/nginx/ssl/obsidian.crt
cp /etc/letsencrypt/live/vpn.xn----7sbaowmfrljlq.xn--p1ai/privkey.pem /etc/nginx/ssl/obsidian.key

# Перезагрузить nginx
systemctl reload nginx
```

### 3.3 Шаг 3: Проверка доступа (Олег на ПК)

```bash
# В PowerShell
Invoke-WebRequest -Uri "https://85.137.166.209:8181/" -Method Options -UseDefaultCredentials
# Должно вернуть 200 OK
```

### 3.4 Шаг 4: Первый sync (Олег на ПК)

В Obsidian:
1. Remotely Save → Click "Sync"
2. Должно появиться "Sync successful" за 1-2 сек
3. На VPS должна появиться папка с новыми файлами

---

## 4. АЛЬТЕРНАТИВНЫЕ ВАРИАНТЫ (если Remotely Save не подходит)

### Вариант A: Self-hosted LiveSync (более сложный, но real-time)
- Поднять CouchDB на VPS
- Настроить плагин "Self-hosted LiveSync" в Obsidian
- **Сложность:** 2-3 часа
- **Плюс:** real-time sync между устройствами

### Вариант B: Cloudflared туннель (без валидного домена)
```bash
cloudflared tunnel create obsidian
cloudflared tunnel route dns obsidian obsidian.example.com
cloudflared tunnel run obsidian
```
- **Плюс:** HTTPS из коробки, не нужен валидный домен
- **Минус:** нужен аккаунт Cloudflare

### Вариант C: Tailscale Funnel (если Tailscale жив)
```bash
tailscale funnel 8181 on
```
- **Плюс:** HTTPS автоматически
- **Минус:** требует Tailscale на ПК

---

## 5. РЕКОМЕНДАЦИЯ

**Шаг 1: Remotely Save (10 мин)**
- Самый быстрый путь
- Стандартный для community плагинов
- Работает с любым WebDAV

**Шаг 2: Let's Encrypt для vpn.xn----7sbaowmfrljlq.xn--p1ai (10 мин)**
- Домен уже есть, валидный сертификат снимет warning

**Шаг 3: Backup auth credentials** в `/root/matryoshka/CREDENTIALS.md` (152-ФЗ)
- Зашифрованный файл с паролями

---

## 6. ЧТО Я СДЕЛАЛ СЕГОДНЯ

✅ Проверил WebDAV (работает везде)
✅ Нашёл причину "сломанности" — пустой `.obsidian/` конфиг
✅ Создал план починки (3 шага)
✅ Обновил REPORT.md с правильной информацией

⏸ **Жду команды Олега:**
- "Ставь Remotely Save" — установлю плагин через скрипт
- "Получай Let's Encrypt" — настрою certbot
- "Оба" — сделаю всё за 20 мин
