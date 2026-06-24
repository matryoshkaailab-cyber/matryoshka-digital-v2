# ПОДКЛЮЧЕНИЕ NOTEBOOK LM ЧЕРЕЗ VPS HERMES

**Дата создания:** 2026-06-01
**Статус:** ПЛАНИРУЕТСЯ
**Приоритет:** ВЫСОКИЙ

---

## ЦЕЛЬ

Подключить Notebook LM через VPS в Чехии для обхода российских блокировок Google. VPS имеет IP в ЕС — Google не блокирует доступ.

---

## АРХИТЕКТУРА

```
Олег (Россия)                    VPS HERMES (Чехия, 85.137.166.209)
     │                                    │
     │                              Chromium Browser
     │                                    │
     │                            Notebook LM (Google)
     │                                    │
     │◄──── Управление через Telegram ◄───┘
```

---

## ЭТАПЫ ПОДКЛЮЧЕНИЯ

### ЭТАП 1: Проверка и установка browser

**Проверить:**
```bash
which google-chrome chromium-browser chromium 2>/dev/null
```

**Если нет — установить:**
```bash
apt-get update && apt-get install -y chromium-browser xvfb
```

**Вариант с Playwright (рекомендуется):**
```bash
pip install playwright && playwright install chromium
```

---

### ЭТАП 2: Запуск browser в режиме remote debugging

**Вариант A: Playwright (рекомендуется)**
```bash
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])"
```

**Вариант B: Xvfb + Chromium**
```bash
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &
chromium-browser --headless --disable-gpu --remote-debugging-port=9222 --no-sandbox &
```

---

### ЭТАП 3: Подключение browser к Hermes

В терминале VPS:
```bash
# Запустить Chrome
google-chrome --headless --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-profile &
```

В Hermes CLI:
```
/browser connect
```

Если нужен CDP endpoint:
```
ws://localhost:9222
```

---

### ЭТАП 4: Login в Google Account

**Шаги:**
1. Navigate: `https://notebooklm.google.com`
2. Click "Sign in"
3. Type email (browser_type)
4. Type password
5. Если 2FA → ввести код
6. Разрешить "Remember this device"

**Важно:** Перед началом убедиться что 2FA отключена ИЛИ есть резервные коды.

---

### ЭТАП 5: Использование Notebook LM

После успешного login через browser можно:

| Функция | Как сделать |
|---------|-------------|
| Создать notebook | browser_click + browser_type |
| Загрузить источник (PDF/URL) | Upload через file input или paste URL |
| Сгенерировать контент | Клик на нужный тип (Podcast, Video, etc.) |
| Скачать результат | browser_click на кнопку Download |
| Управлять несколькими notebooks | Tab management |

---

### ЭТАП 6: Сохранение сессии (Cookies)

**Для persistent session:**
```python
# Сохранить cookies после login
context = browser.contexts[0]
cookies = context.cookies()
with open('/tmp/notebook_lm_cookies.json', 'w') as f:
    json.dump(cookies, f)

# Восстановить в следующей сессии
with open('/tmp/notebook_lm_cookies.json') as f:
    cookies = json.load(f)
context.add_cookies(cookies)
```

**Это позволяет НЕ вводить логин/пароль каждый раз.**

---

## КРИТИЧЕСКИЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема: Google detected as bot
**Решение:**
```python
# При запуске browser
browser = p.chromium.launch(
    headless=True,
    args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    ]
)
```

### Проблема: 2FA не позволяет автоматизировать
**Решения:**
1. **Отключить 2FA** на время настройки (не рекомендуется для безопасности)
2. **Использовать резервные коды** — 10 кодов из настроек Google
3. **Использовать Authenticator app** — но нужен доступ к телефону

### Проблема: Session expired after some time
**Решение:** Периодически обновлять cookies. Автоматизировать "browser.navigate + check if logged in".

### Проблема: CAPTCHA
**Решение:** Если появится CAPTCHA — остановить автоматизацию, сообщить Олегу через Telegram для ручного ввода.

---

## АВТОМАТИЗАЦИЯ РАБОЧЕГО ПРОЦЕССА

### Workflow: Создать контент из источника

```
1. HERMES получает задачу (например: "сделай подкаст про X")
2. → Navigate to Notebook LM
3. → Open или создать notebook
4. → Загрузить источник (URL или файл)
5. → Дождаться обработки (AI reads source)
6. → Generate Podcast
7. → Скачать результат
8. → Сохранить в /root/matryoshka/notebook_lm/output/
9. → Отправить Олегу через Telegram
```

---

## ФАЙЛЫ И ПАПКИ

```
/root/matryoshka/notebook_lm/
├── cookies.json          # Сохранённые cookies для session persistence
├── sources/              # Загруженные источники (PDF, URLs)
├── output/               # Результаты (podcasts, videos, infographics)
├── logs/                  # Логи работы
└── PLAN.md              # Этот документ
```

---

## CHECKLIST ПЕРЕД СТАРТОМ

- [ ] VPS browser проверен
- [ ] Playwright or Xvfb+Chromium установлен
- [ ] Google account credentials received from Oleg
- [ ] 2FA отключена ИЛИ резервные коды получены
- [ ] Browser подключен к Hermes
- [ ] Login успешен
- [ ] Cookies сохранены

---

## АЛЬТЕРНАТИВНЫЙ ПУТЬ: MCP Server

Исследовать есть ли у Notebook LM MCP endpoint или API:

**Варианты:**
1. Notebook LM имеет неофициальный API
2. Использовать unofficial Python client
3. Использовать browser automation как fallback

**Проверить:**
- `https://notebooklm.google.com/_/api/...`
- Поиск в GitHub: "notebooklm api unofficial"

---

## КОНТАКТ

**Когда план готов к выполнению:**
1. Олег скидывает логин/пароль Google
2. Резервные коды 2FA (если есть)
3. Мы начинаем с ЭТАПА 1

---

**Следующий шаг:** Проверить browser на VPS и начать установку.