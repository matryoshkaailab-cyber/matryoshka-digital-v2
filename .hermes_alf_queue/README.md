# Inter-agent очередь ALF ↔ HERMES

Создана: 2026-06-18 16:00 (по запросу Олега)

## Протокол

### HERMES → ALF
1. HERMES создаёт `/root/matryoshka/.hermes_alf_queue/.hermes_task_alf.json` (status=pending)
2. ALF обнаруживает (polling каждые 30 сек, или Telegram notify)
3. ALF читает, обрабатывает
4. ALF создаёт `/root/matryoshka/.hermes_alf_queue/.hermes_result_alf.json` (status=done)

### ALF → HERMES
1. ALF создаёт `/root/matryoshka/.hermes_alf_queue/.hermes_result_alf.json` (если нужна обратная связь)
2. HERMES читает результат

## Файлы
- `.hermes_task_alf.json` — задача от HERMES к ALF
- `.hermes_result_alf.json` — ответ от ALF

## Согласно Аликсу
> "Расширить существующую файловую очередь (`.hermes_task_alf.json` / `.hermes_result_alf.json` в `C:\matryoshka`), а не городить Redis/broker. Протокол уже работает для ALEX — handler на стороне ALF пишется за 1-2 часа."

## Статус: ТОЛЬКО ЧТО СОЗДАНО
