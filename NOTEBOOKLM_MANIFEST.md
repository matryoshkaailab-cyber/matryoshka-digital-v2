# 📚 NotebookLM Manifest — MATRYOSHKA DIGITAL

**Ноутбук:** "MATRYOSHKA DIGITAL — Полная база знаний"
**Дата:** 2026-06-16
**Загружено источников:** 15

## Источники (для загрузки в UI NotebookLM):

| # | Файл | Описание | Категория |
|---|------|----------|-----------|
| 1 | `notebooklm_sources/identity/USER.md` | Профиль Олега (CLIENT_001, CLIENT_002) | IDENTITY |
| 2 | `notebooklm_sources/identity/AGENTS.md` | Архитектура агентов (HERMES/ALEX/ALISA/ALINA/ALF) | IDENTITY |
| 3 | `notebooklm_sources/identity/HERMES_IDENTITY_FULL.md` | Полная идентичность Hermes | IDENTITY |
| 4 | `notebooklm_sources/identity/ALF_FULL.md` | Полная идентичность ALF | IDENTITY |
| 5 | `notebooklm_sources/infrastructure/INFRA.md` | VPS 85.137.166.209, инфраструктура | INFRA |
| 6 | `notebooklm_sources/alex/REPORT.md` | Отчёт по ALEX | AGENTS |
| 7 | `notebooklm_sources/projects/legion/REPORT.md` | VR Клуб (LEGION) | PROJECTS |
| 8 | `notebooklm_sources/projects/webdav/REPORT.md` | WebDAV setup | PROJECTS |
| 9 | `notebooklm_sources/projects/PLAN.md` | Общий план MATRYOSHKA | PROJECTS |
| 10 | `notebooklm_sources/projects/nikolay/PLAN.md` | Кейс NIKOLAY (CLIENT_001) | PROJECTS |
| 11 | `notebooklm_sources/projects/nikolay/PLAN_v5_FINAL.md` | Финальный план NIKOLAY | PROJECTS |
| 12 | `notebooklm_sources/projects/nikolay/alina_plan_draft.md` | Черновик плана ALINA | PROJECTS |
| 13 | `notebooklm_sources/projects/nikolay/ALINA_HANDS.md` | "Руки" ALINA | PROJECTS |
| 14 | `notebooklm_sources/projects/nikolay/PROPOSAL.md` | Предложение для NIKOLAY | PROJECTS |
| 15 | `notebooklm_sources/projects/datalink/REPORT.md` | VPN-сервис DATALINK PRO | PROJECTS |

## Команда для подготовки архива (для загрузки):

```bash
# Создать zip всех 15 источников
cd /root/matryoshka
zip -j notebooklm_sources.zip notebooklm_sources/identity/*.md \
                        notebooklm_sources/infrastructure/*.md \
                        notebooklm_sources/alex/*.md \
                        notebooklm_sources/projects/*/*.md \
                        notebooklm_sources/projects/*.md

# Или отдельными файлами
cp notebooklm_sources/identity/USER.md /tmp/notebooklm/01-user.md
# ... и т.д.
```

## Инструкция для Олега (загрузка в UI):

1. Зайти в https://notebooklm.google.com/
2. Создать новый ноутбук "MATRYOSHKA DIGITAL — Полная база знаний"
3. Загрузить все 15 файлов через "Add source → Upload"
4. Подождать индексации (~2-5 мин)
5. Можно задавать вопросы по базе знаний

## Anonymization (152-ФЗ):

**ВАЖНО:** Перед загрузкой в NotebookLM (внешний сервис), применить anonymizer:

```bash
python3 /root/matryoshka/notebooklm_sources/anonymize.py
```

Заменяет:
- Николай → CLIENT_001
- Наталья → CLIENT_002
- Олег → OLEG_ID
- Краснодар → CITY_001
- Telegram IDs → TG_ID
