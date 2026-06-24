# ⚠️ DEPRECATED 2026-06-16 — ФЕЙКИ
# Этот файл содержит УСТАРЕВШИЕ данные: агенты ILON/ECLER/OpenClaw (не существуют),
# VPN UUID 4ea33e69 / SNI microsoft (ВЫДУМАННЫЕ — реально SNI=www.google.com),
# Hermes v0.15.1 / MiniMax-M2.7 (НЕ СУЩЕСТВУЕТ — v0.16.0 / MiniMax-M3).
# НЕ ИСПОЛЬЗОВАТЬ как источник истины.
# Источник правды: /root/matryoshka/AGENTS.md + /root/matryoshka/SOUL.md
# Holographic memory: fact #28 (warnings о фейках)
# Skill автопроверки: soul-fake-detection
# Если нужна актуальная инфа — перегенерируй документ или спроси Hermes.
# ────────────────────────────────────────────────────────────────────────

# MATRYOSHKA DIGITAL — Ключевые факты

## Проект
**Matryoshka Digital** — система VPN + Telegram боты + автоматизация.
Создатель: **Олег Чут** (Генерал).
Рабочая папка: `C:\matryoshka\`

## Главный VPN-сервис: DATALINK PRO

### Сервер
- **IP:** 85.137.166.209
- **ОС:** Ubuntu 24.04.4 LTS
- **Хостинг:** SmartApe (Host-Telecom, Чехия)
- **SSH:** root / Jktu22051987
- **SSH ключ:** `C:\lab\vpn_matryoshka_key` (alias: vpn-serger в ~/.ssh/config)

### Архитектура VPN
```
AmneziaWG (awg0)     → порт 41234/UDP  ✅ РАБОТАЕТ
VLESS+REALITY (Xray) → порт 443/TCP    ⚠️ частично (WiFi)
Nginx Stream         → порт 443/TCP    → маршрутизация SNI
Сайт (Flask)         → порт 8444/TCP  ✅ РАБОТАЕТ
```

### Команда VPN
| Имя | Статус | Примечание |
|-----|--------|-----------|
| **Наталья** | ✅ работает | WiFi + мобильный |
| **Олег** | ⚠️ частично | WiFi ✅, мобильный ❌ (CGNAT) |
| **Сергей** | ❌ не работает | Использовал порт 443 |
| **Тася** | ✅ активна | 229 MiB in / 2.56 GiB out |

### Проблемы (известные)
1. Олег на мобильном — CGNAT Билайн убивает UDP сессии
2. VLESS через Nginx не работает на мобильных (connection reset)
3. Бот v11 генерировал VLESS — заменён на v12 (AmneziaWG)

## BLEICH параметры AmneziaWG
```
Jc=4, Jmin=84, Jmax=243, S1=35, S2=99, S3=24, S4=8
H1=100000-800000, H2=1000000-8000000
H3=10000000-80000000, H4=100000000-800000000
I1=<r 256>, MTU=1280, DNS=1.1.1.1
```
⚠️ Клиент должен использовать ТОЧНО эти параметры!

## Ключевые файлы
| Файл | Назначение |
|------|------------|
| `datalink_pro_bot_v13.py` | Telegram бот (бот v12 на сервере) |
| `datalink_web_v2.py` | Сайт Flask |
| `DATALINK_PRO_АНАЛИЗ/` | Вся документация по VPN |
| `sergey-vpn-czech/` | VPN проект (15 файлов) |
| `vpn_business/` | VPN бизнес-логика (боты, x-ui) |
| `vPn/` | VPN скрипты и конфиги (35 файлов) |

## Бизнес
### Тарифы DATALINK PRO (через ЮKassa)
- Shop ID: **1313515** (боевой)
- Тарифы: 500₽ / 1000₽ / 2000₽

### Приложение для клиентов
⚠️ **AmneziaWG** (НЕ AmneziaVPN!)
- Android: `org.amnezia.awg`
- iPhone: AmneziaWG (App Store)

## Другие проекты в Matryoshka
| Проект | Назначение |
|--------|-----------|
| `vpn_business/` | VPN с x-ui панелью |
| `vpn_simple/` | Простой WireGuard |
| `n8n/` | n8n автоматизация |
| `scripts/` | Скрипты проверки ботов |

## Установленные скиллы OpenClaw
- `mmxagent-guardian` — защита
- `skill-scanner` — сканер скиллов
- `skill-guard` — гвард скиллов
- `prompt-injection-guard` — защита от инъекций

## OpenClaw
- **Версия:** 2026.4.14
- **Модель:** minimax-portal/MiniMax-M2.7 (OAuth)
- **Gateway:** 127.0.0.1:18789
- **Документация:** docs.openclaw.ai

## Связь с проектом
- OpenClaw TUI: `openclaw-tui`
- Telegram бот проекта: `@datalink_pro_bot`
- Токен бота: `8349948703:AAFybtShN5Q6LlVM8nzUbEzTvQK1VrgAc5I`
