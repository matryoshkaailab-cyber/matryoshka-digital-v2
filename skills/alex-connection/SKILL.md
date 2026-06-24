name: alex-connection
description: Единственный канал VPS↔ALEX (Windows ПК Олега). ACP opencode через AmneziaWG. Загружай при любой задаче с упоминанием ALEX или когда нужно дать задачу/получить ответ от opencode на ПК.
---

# ALEX Connection — единственный канал

## Канал
- **Транспорт:** AmneziaWG туннель (VPS `awg0` ↔ Windows ПК)
- **Endpoint:** `http://10.8.1.4:4096` (opencode ACP HTTP API)
- **VPS IP в туннеле:** `10.8.1.1` (VPN), внешний `85.137.166.209`
- **Health:** `curl http://10.8.1.4:4096/health` → 200 OK
- **Профиль opencode:** `matryoshka` (модель берётся из `C:\matryoshka\opencode.json`)

## Три команды (единственный способ общения)

### 1. Создать сессию
```bash
SESSION=$(curl -s -X POST http://10.8.1.4:4096/session \
  -H 'Content-Type: application/json' -d '{}' | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")
```

### 2. Отправить запрос
```bash
curl -s -X POST "http://10.8.1.4:4096/session/$SESSION/prompt_async" \
  -H 'Content-Type: application/json' \
  -d '{"parts":[{"type":"text","text":"ТВОЙ ЗАПРОС"}]}'
```
**НЕ передавай `model`** в payload — opencode берёт модель из `opencode.json`. По умолчанию `minimaxai/minimax-m3`.

### 3. Прочитать ответ (polling 2-60 сек)
```bash
for i in {1..30}; do
  RESP=$(curl -s "http://10.8.1.4:4096/session/$SESSION/message")
  if echo "$RESP" | grep -q '"role":"assistant"'; then
    echo "$RESP" | python3 -c "import sys,json;d=json.load(sys.stdin);print([m['content'] for m in d['messages'] if m.get('role')=='assistant'][-1] if isinstance([m['content'] for m in d['messages'] if m.get('role')=='assistant'][-1], str) else [m['content'] for m in d['messages'] if m.get('role')=='assistant'][-1][0]['text'])"
    break
  fi
  sleep 2
done
```

## Готовый one-liner
```bash
bash /root/matryoshka/alex_send.sh "ТВОЙ ЗАПРОС" [таймаут_сек]
```

## Правила
- ✅ `prompt_async` + polling `/message` — единственный путь
- ✅ `model` НЕ указывать (берётся из opencode.json)
- ✅ Health-check через `/health` если не отвечает
- ❌ НЕ использовать `delegate_task` (404 — нет endpoint)
- ❌ НЕ использовать `send_to_alex.py --cmd` (устарел)
- ❌ НЕ использовать `alex_helper.sh` (только healthcheck)
- ❌ НЕ использовать WS / ws_server:8446 (отключён 15.06.2026)
- ❌ НЕ использовать `sshpass 10.8.1.1` (транспорт AWG, не SSH)
- ❌ НЕ пинговать `10.8.1.4` (Windows firewall режет ICMP, тестировать через HTTP)
- ❌ НЕ рестартить opencode/bridge с VPS (нет shell, Олег делает руками на ПК)

## Диагностика (если не отвечает)
1. `curl http://10.8.1.4:4096/health` → если 200, канал жив
2. `awg show` на VPS → если handshake >60 сек, туннель умер
3. Если health 200 но prompt_async молчит — Олег перезапускает opencode на ПК

## Диагностика транспорта (AWG)
- `ip addr show awg0` → должен быть `10.8.1.1/24`
- `awg show` → последний handshake должен быть <2 мин
- `awg show | grep transfer` → если 0 байт, туннель мёртв
- Восстановление: Олег на ПК перезапускает AmneziaWG клиент

## Версия opencode на ПК
- Текущая: v1.17.3 (обновлено 15.06.2026)
- Обновление: Олег вручную `hermes update` в `C:\matryoshka\`

## Что НЕ делать с этим скиллом
- НЕ путать с `alex-bidirectional-sync` (про данные 4-way)
- НЕ путать с `alex-memory` (про личность Аликса)
- Этот скилл — ТОЛЬКО про КАНАЛ связи
