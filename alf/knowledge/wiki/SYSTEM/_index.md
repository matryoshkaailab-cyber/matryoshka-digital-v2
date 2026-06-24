---
created: 2026-05-12
updated: 2026-05-20
tags: [system, infrastructure]
---

# SYSTEM — Инфраструктура MATRYOSHKA DIGITAL

## Серверы

| Сервер | IP | Доступ | Назначение |
|--------|-----|--------|------------|
| **VPS** | 85.137.166.209 | root/Jktu22051987 | HERMES, ALF, ALINA, n8n |

## SSH
`ash
sshpass -p 'Jktu22051987' ssh -o StrictHostKeyChecking=accept-new root@85.137.166.209
`

## Файлы на сервере
| Путь | Назначение |
|------|------------|
| /root/matryoshka/ | Основной проект |
| /root/.hermes/ | HERMES Agent профили |
| /root/matryoshka/PRIORITY_PLAN.md | Приоритетный план (P0) |
| /var/log/ | Системные логи |

## Команда — 3 РОЯ
- ⚪ Белый: HERMES (дирижёр), ALF (стратег + библиотекарь)
- 🔵 Синий: ALEX (инженер, Windows ПК)
- 🔴 Красный: ALISA (маркетинг, отложена)

> ⚠️ ECLER НЕ СУЩЕСТВУЕТ. Это имя старого агента → переименован в ALINA (клиентский кейс Николая, @NikolaAlinaBot). На VPS работают HERMES + ALF + ALINA (8 systemd сервисов).

## ❌ НЕ СУЩЕСТВУЕТ
- **ECLER** — переименован в ALINA 07.06.2026
- ILON / TOLIK — удалены
- OpenClaw — заменён на HERMES
