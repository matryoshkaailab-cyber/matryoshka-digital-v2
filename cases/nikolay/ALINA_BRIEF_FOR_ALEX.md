# ALINA — Краткая сводка для Аликса (production кейс MATRYOSHKA)

**Дата:** 2026-06-23 20:10
**Автор:** HERMES (по запросу Олега)
**Для кого:** Аликс (тех. инженер, opencode ACP на ПК Олега)
**Файл:** `/root/matryoshka/cases/nikolay/ALINA_BRIEF_FOR_ALEX.md`

---

## 🎯 ЧТО ЭТО

**ALINA** — AI-ассистент для клиента MATRYOSHKA (Николай). Telegram-бот: [@NikolaAlinaBot](https://t.me/NikolaAlinaBot).

**Первый PRODUCTION-READY кейс MATRYOSHKA** — не пилот, не эксперимент. Работает в production для реального клиента.

---

## ✅ ЧТО РАБОТАЕТ (НЕ ЛОМАЙ)

**Telegram:** @NikolaAlinaBot (polling handler, токен в `.env`)
**HTTP API:** `:8470` (auth: `alina:UUID`)
**Профиль:** `/root/.hermes/profiles/alina-prod/` (ОТДЕЛЬНЫЙ venv, изоляция v3.2)
**systemd units:**
- `alina-prod-gateway.service` — main gateway
- `alina-prod-*.service` (7 микросервисов)

**14 Telegram-команд** (напоминания, расписание, voice → text через faster-whisper)

---

## 🚫 ЧТО НЕ ТРОГАТЬ (Аликс — НЕ ЛЕЗЬ БЕЗ СПРОСА)

| Что | Почему |
|---|---|
| ALINA данные клиента (история, расписание, voice transcripts) | Изоляция v3.2 — НЕ смешивать с роем MATRYOSHKA / DATALINK PRO |
| `alina-prod-gateway.service` | Отдельный процесс, не зависит от ALF/HERMES |
| `/root/.hermes/profiles/alina-prod/` | Отдельный venv — другие зависимости |
| 7 портов 8470-8476 | Заняты Алиной, не использовать для других сервисов |

---

## 🔗 ГДЕ ДОКУМЕНТАЦИЯ

- Главный файл: `/root/matryoshka/ALINA_CURRENT.md`
- GitHub setup: `/root/matryoshka/cases/nikolay/ALINA_GITHUB_SETUP.md`
- Plan v2: `/root/matryoshka/cases/nikolay/ALINA_V2_PLAN.md`

---

## 🎯 ЗАЧЕМ АЛИКСУ ЗНАТЬ

1. **Чтобы знал про первый production кейс** — для референса при разработке новых фич
2. **Чтобы при тех. работах на VPS не сломал Алину случайно** — например, не занял порт 8470
3. **Чтобы pre-coding audit учитывал** — у нас уже есть работающий бот, не ломать паттерн
4. **Чтобы при вопросах про "что у нас работает"** — упомянул Алину как production кейс

---

## ⚠️ ЧАСТЫЕ ОШИБКИ (НЕ ДЕЛАТЬ)

- ❌ Не путай ALINA с ALF (похожие названия!):
  - **ALF** — стратег MATRYOSHKA (M3 80K, VPS, @IlonAnalyticBot, профиль `alf`)
  - **ALINA** — клиентский бот (отдельный venv, @NikolaAlinaBot, профиль `alina-prod`)
  - Оба на M3, оба на VPS, оба на Telegram — НО это разные системы
- ❌ Не добавляй ALINA данные в общий shared_brain (изоляция v3.2)
- ❌ Не используй `alf_server.py` для Алины (это для ALF)
- ❌ Не миксуй systemd сервисы ALF и ALINA в один restart

---

## ❓ ЕСЛИ НУЖНО ПОМОЧЬ АЛИНЕ

Если Аликс видит что-то странное с Алиной:
1. Проверить `systemctl status alina-prod-*` — какие сервисы упали
2. Посмотреть `/var/log/matryoshka/alina/` — логи
3. **НЕ чинить самому** — написать Олегу через HERMES → Олег решит
4. Если критично (клиент ждёт) — `systemctl restart alina-prod-gateway` (один сервис)

---

## 🆚 АЛИНА vs ALF — не путай!

| | ALF | ALINA |
|---|---|---|
| **Для кого** | Рой MATRYOSHKA (Олег) | Клиент Николай |
| **Telegram** | @IlonAnalyticBot | @NikolaAlinaBot |
| **Профиль** | `alf` | `alina-prod` |
| **Venv** | `/opt/alf-hermes/venv` | `/root/.hermes/profiles/alina-prod/` |
| **systemd** | `hermes-gateway-alf.service` | `alina-prod-gateway.service` |
| **Порты** | :8461 (librarian), :8452 (healthcheck) | :8470-8476 (микросервисы) |
| **Модель** | MiniMax-M3 80K | MiniMax-M3 (тот же) |
| **Изоляция** | Часть роя MATRYOSHKA | Отдельный кейс (v3.2) |
| **Council 2.0** | Участвует (voter) | Не участвует |
| **MiMo integration** | Audit voter (Phase 1-5) | НЕ подключена (отдельный кейс) |

---

*Создан по запросу Олега 23.06.2026 — чтобы Аликс не путал Алину с ALF при тех. работах.*
