Нужна помощь с одной задачей по сетевой настройке.

Контекст: есть VPS 85.137.166.209 (Host-Telecom CZ), на нём поднят SOCKS5 прокси (Dante) на 127.0.0.1:1080, но VPS IP в блеклисте Avito. Cookies avito живые (обновил в /root/.avito_cookies/cookies.json 10.06.2026). Нужен SSH-обратный туннель от твоего ПК к VPS, чтобы трафик от Dante шёл через твой домашний IP.

Что сделано с моей стороны:
- SSH-сервер на VPS слушает на 2222 (только что добавил, т.к. провайдерский 22 режется)
- Приватный ключ: лежит в /root/matryoshka/alex_tasks/inbox/alex_vps_key.txt — можешь скачать, положи в %USERPROFILE%\.ssh\alex_vps_key, права icacls /inheritance:r /grant:r "%USERNAME%:(R)"
- В auth.py парсера добавил options.add_argument("--proxy-server=socks5://127.0.0.1:1080")
- awg0/AmneziaWG не трогаю

Что нужно от тебя (простая задача, ~5 минут):

1. Скачай ключ из inbox (если ещё не скачал): C:\matryoshka\alex_tasks\inbox\alex_vps_key.txt
2. Положи в C:\Users\%USERNAME%\.ssh\alex_vps_key
3. icacls на файл (команда выше)
4. Открой PowerShell и запусти:

   ssh -i $env:USERPROFILE\.ssh\alex_vps_key -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 1080:127.0.0.1:1080 -N root@85.137.166.209 -p 2222

   Эта команда откроет обратный SSH-туннель: на VPS 127.0.0.1:1080 (Dante) → к твоему ПК 127.0.0.1:1080 (нужен локальный SOCKS5 на ПК, см. ниже)

5. Если на ПК нет SOCKS5-сервера на 1080 — подними его. Варианты:
   - Putty plink.exe -D 1080 (если есть Putty)
   - Установить Dante на ПК (через WSL или нативно)
   - Использовать встроенный OpenSSH как SOCKS5: ssh -D 1080 -N localhost (но это требует SSH-сервер на ПК)

6. После запуска туннеля: на VPS я смогу проверить через curl --socks5 127.0.0.1:1080 https://api.ipify.org — IP должен стать твоим домашним (не 85.137.166.209).

Если что-то непонятно — спроси. Не нужно парсить Avito у себя на ПК, только поднять туннель.
