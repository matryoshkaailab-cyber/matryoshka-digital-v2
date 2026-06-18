# 🔧 ТЗ для ALEX: REFRESH NOTEBOOKLM COOKIES

**Дата:** 2026-06-19
**Заказчик:** ALF (стратег/аналитик)
**Исполнитель:** ALEX (тех инженер, Windows ПК Олега)
**Срочность:** 🟡 средняя (cookies протухают каждые 3-5 дней)

---

## Зачем

ALF использует NotebookLM как страховку от галлюцинаций (стратег Олега сказал: "Ты наш аналитик, тебе нельзя допускать ошибки"). Cookies Google протухают агрессивно при использовании через прокси FoxyProxy (HTTP `45.83.11.211:8000`).

**Симптом:** `notebooklm ask` падает с `Error: Authentication expired or invalid. Redirected to: https://accounts.google.com/v3/signin/identifier...`

**Что происходит:** cookies в `/root/.notebooklm/profiles/default/storage_state.json` устаревают, нужно обновить из живого Chrome на ПК.

---

## Что нужно сделать

### Шаг 1: Экспортировать cookies из Chrome (на ПК Олега)

1. Открыть Chrome
2. Перейти на https://notebooklm.google.com (должен быть залогинен как `matryoshka.ai.lab@gmail.com`)
3. Установить расширение **Cookie-Editor** (если нет) — https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm
4. Открыть Cookie-Editor → кнопка **Export** → формат **JSON** → "Tab" (только для текущего сайта)
5. Сохранить в файл `C:\Users\User\Desktop\notebooklm_cookies_YYYYMMDD.json`

### Шаг 2: Загрузить cookies на VPS

Через WebDAV (https://85.137.166.209:8181, auth: hermes / hermes2026):
```
C:\Users\User\Desktop\notebooklm_cookies_YYYYMMDD.json
  → https://85.137.166.209:8181/inbox/notebooklm_cookies_YYYYMMDD.json
```

Или через PowerShell + scp:
```powershell
scp C:\Users\User\Desktop\notebooklm_cookies_YYYYMMDD.json root@85.137.166.209:/tmp/
```

### Шаг 3: ALF конвертирует cookies в storage_state.json

ALF (на VPS) выполнит:
```bash
# 1. Использовать скрипт от ALEX (уже есть)
/root/.hermes/skills/notebooklm/import_browser_cookies.py /tmp/notebooklm_cookies_*.json

# 2. Результат автоматически в /root/.notebooklm/profiles/default/storage_state.json
```

### Шаг 4: Verify
ALF проверит:
```bash
/root/.notebooklm/nb.sh ask "Test" -n 38d2a04f-9f73-49c7-baf7-0a289eecfa8a 2>&1 | head -3
# Должен ответить без "Authentication expired"
```

### Шаг 5: Cleanup
ALF удалит /tmp/notebooklm_cookies_*.json после успешного импорта.

---

## Когда делать

| Триггер | Действие |
|---------|----------|
| Cookies протухли (ALF получил Authentication expired) | Сделать Шаги 1-5 |
| Cron `cookie_expiry_check.sh` (25 числа каждого месяца в 10:00) уведомил | Сделать Шаги 1-5 |
| Олег попросил | Сделать Шаги 1-5 |

**Не нужно:** Делать каждую неделю или автоматизировать через ALEX (Chrome на ПК не всегда в сети).

---

## Что НЕ нужно делать

- ❌ Не использовать Playwright headless login — credentials не передаются через прокси
- ❌ Не патчить auth.json — это для Hermes API, не Google
- ❌ Не использовать VPN AmneziaWG для обхода geo-блока — geo-блок уже обходится через FoxyProxy
- ❌ Не делать через Chrome на VPS — Chrome на ПК уже залогинен

---

## Что ALEX должен вернуть после выполнения

После Шагов 1-2, ALEX должен сообщить ALF:
- Количество cookies в файле (`24 cookies expected`)
- Дата экспорта
- Любые warnings (если cookies содержат `httpOnly` или `secure` флаги — это OK)

---

## Файлы

- **Источник cookies:** Chrome на ПК Олега, расширение Cookie-Editor
- **Промежуточный:** `/tmp/notebooklm_cookies_YYYYMMDD.json`
- **Финальный:** `/root/.notebooklm/profiles/default/storage_state.json` (обновляется скриптом)
- **Скрипт конвертации:** `/root/.hermes/skills/notebooklm/import_browser_cookies.py`
- **Wrapper:** `/root/.notebooklm/nb.sh` (использует HTTP прокси)

---

## Связанные ресурсы

- **NotebookLM notebook ID:** `38d2a04f-9f73-49c7-baf7-0a289eecfa8a` (ALF, 33 источника)
- **Google account:** `matryoshka.ai.lab@gmail.com`
- **FoxyProxy HTTP:** `45.83.11.211:8000`, user=`gusQy8`, password=[REDACTED]
- **VPS WebDAV:** `https://85.137.166.209:8181`, auth=`hermes:hermes2026`
- **Cron reminder:** `/etc/cron.d/notebooklm_cookies` (или существующий `/root/.notebooklm/cookie_expiry_check.sh`)

---

## Итог

ALEX делает Шаги 1-2 (10 минут), ALF делает Шаги 3-5 (2 минуты). Итого 12 минут на полный refresh.

---

*ALF, 2026-06-19. Это ТЗ для ALEX — не требует немедленного выполнения, делать когда cookies протухнут.*