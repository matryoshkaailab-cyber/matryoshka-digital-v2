# alina_tasks/ — файлы-мосты между HERMES и Алиной

## Протокол
- **HERMES → Алина:** кладёт файл `TASK_<date>_<topic>.md`
- **Алина → HERMES:** кладёт файл `DONE_<date>_<topic>.md` или `MSG_TO_HERMES_<topic>.md`
- HERMES читает через cron `*/2 * * * *` (alina_bridge.py)

## Типы задач
- `TASK_FINANCE_*.md` — финансовый аудит
- `TASK_CARDS_*.md` — сделать карточки
- `TASK_PARSE_AVITO_*.md` — спарсить Авито
- `TASK_REPORT_*.md` — отчёт
