# ТЕХНИЧЕСКИЙ ДОКУМЕНТ: РЕЖИМ АНВАЖЕНС
## Система распределения задач HERMES → AGENTS
## Дата: 08.05.2026 | Версия: 1.0

---

## 1. АРХИТЕКТУРА СИСТЕМЫ

### Схема взаимодействия:

```
                    ОЛЕГ ЧУТ
                   (Telegram)
                        │
                        ▼
              ┌─────────────────┐
              │  HERMES (Я)     │
              │  Дирижёр        │
              │  MiniMax M2.7   │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ КИМ2,6   │  │OPEN DES. │  │ OTHER    │
   │ (Kimi)   │  │ (Design) │  │ AGENTS   │
   │ Инженер  │  │ Промты   │  │          │
   └──────────┘  └──────────┘  └──────────┘
        │              │
        └──────────────┘
               │
               ▼
        /root/matryoshka/
        ├── tasks/      ← задачи от HERMES
        ├── results/     ← результаты от агентов
        └── docs/        ← документация
```

---

## 2. РОЛИ И ОБЯЗАННОСТИ

### HERMES (Дирижёр) — Я
```
Обязанности:
• Получать задачи от Олега (Telegram)
• Анализировать задачу
• Генерировать промты для Open Design
• Создавать изображения (image_01)
• Распределять задачи агентам
• Контролировать выполнение
• Проверять результаты
• Доставлять результат Олегу

Инструменты:
• Telegram (связь с Олегом)
• GitHub (синхронизация с агентами)
• Kanban (трекинг задач)
• image_generation (создание картинок)
• terminal (управление сервером)
```

### КИМ2,6 (Инженер) — OpenCode + Kimi K2.6
```
Обязанности:
• Читать задачи из /root/matryoshka/tasks/
• Запускать Open Design
• Генерировать дизайны через Kimi CLI
• Дорабатывать код через OpenCode
• Сохранять результаты в /root/matryoshka/results/
• Push в GitHub

Инструменты:
• OpenCode (редактор)
• Kimi CLI / OpenCode Agent (AI)
• Open Design (дизайн-генератор)
• Git (версионирование)
```

### OPEN DESIGN (Инструмент генерации)
```
Обязанности:
• Генерировать прототипы по промтам
• Создавать HTML/CSS код
• Экспортировать в PDF/PPTX/MP4
• Использовать 72+ дизайн-систем

Промты получает от HERMES, выполняет КИМ2,6
```

---

## 3. ПРОЦЕСС РАБОТЫ

### ЭТАП 1: Получение задачи (HERMES)
```
1. Олег присылает задачу в Telegram
2. HERMES анализирует: что нужно?
3. Определяет исполнителя (КИМ2,6)
4. Если нужны картинки — генерирует
5. Составляет промт для Open Design
6. Создаёт файл задачи в /tasks/
7. Push в GitHub
8. Отмечает в Kanban: in_progress
```

### ЭТАП 2: Выполнение (КИМ2,6)
```
1. Git pull — получил задачу
2. Читает /root/matryoshka/tasks/task_XXX.md
3. Открывает Open Design (http://localhost:7456)
4. Загружает картинки от HERMES (если есть)
5. Вставляет промт из задачи
6. Kimi CLI генерирует дизайн
7. OpenCode дорабатывает код
8. Сохраняет в /root/matryoshka/results/result_XXX/
9. Git add . && git commit && git push
10. Отмечает в Kanban: done
```

### ЭТАП 3: Проверка (HERMES)
```
1. Git pull — получил результат
2. Проверяет файлы в results/
3. Если нужно — делает правки сам
4. Формирует отчёт для Олега
5. Отправляет результат в Telegram
6. Закрывает задачу в Kanban
```

---

## 4. СТРУКТУРА ФАЙЛОВ

### Задача (tasks/task_XXX.md):
```markdown
# ЗАДАЧА №XXX — Название
## Дата: XX.XX.XXXX
## Статус: Ожидает | В работе | Готово

---

## ТИТУЛ
Краткое описание задачи

## ПРИОРИТЕТ
HIGH | MEDIUM | LOW

## ПРОМТ ДЛЯ OPEN DESIGN
[Промт который нужно вставить в Open Design]

## КАРТИНКИ (Urls)
- [url картинки 1]
- [url картинки 2]

## ДИЗАЙН-СИСТЕМА
[Какую систему использовать: Stripe / Airbnb / и т.д.]

## ДЕДЛАЙН
XX.XX.XXXX

## ОЖИДАЕМЫЙ РЕЗУЛЬТАТ
[Что должно получиться]

## КОНТАКТЫ
@oleg_industry_bot (Hermes)
```

### Результат (results/result_XXX.md):
```markdown
# РЕЗУЛЬТАТ №XXX
## Дата: XX.XX.XXXX
## Задача: task_XXX

---

## СТАТУС
✅ Готово | ⚠️ Частично | ❌ Проблема

## ССЫЛКИ НА ФАЙЛЫ
- /root/matryoshka/results/result_XXX/index.html
- /root/matryoshka/results/result_XXX/assets/

## ЧТО СДЕЛАНО
[Описание результата]

## ПРОБЛЕМЫ (если есть)
[Описание проблем]

## СКРИНШОТЫ
[Urls скриншотов если есть]
```

---

## 5. КОМАНДЫ УПРАВЛЕНИЯ

### HERMES — Создать задачу:
```bash
# Создать задачу
cat > /root/matryoshka/tasks/task_XXX.md << 'EOF'
# ЗАДАЧА: [Название]
...
EOF

# Push в GitHub
cd /root/matryoshka && git add . && git commit -m "New task for Kim2,6" && git push

# Добавить в Kanban
hermes kanban --board default create "[Название]" --triage
hermes kanban --board default assign [task_id] kimi2-6
```

### КИМ2,6 — Взять задачу:
```bash
# Получить задачи
git clone https://github.com/matryoshkaailab-cyber/matryoshka-digital-v2.git
cd matryoshka-digital-v2
cat tasks/task_XXX.md

# Запустить Open Design
cd open-design && docker compose up -d
# Открыть http://localhost:7456

# Выполнить и сохранить
# ... работа ...
mv result /root/matryoshka/results/result_XXX/

# Push результат
git add . && git commit -m "Result task_XXX complete" && git push
```

### HERMES — Проверить результат:
```bash
git pull
ls -la /root/matryoshka/results/result_XXX/
cat /root/matryoshka/results/result_XXX.md
```

---

## 6. КАНАЛЫ СВЯЗИ

### Telegram (ОЛЕГ ↔ HERMES):
```
Олег → HERMES: Задачи, вопросы, правки
HERMES → Олег: Результаты, отчёты, статусы
```

### GitHub (HERMES ↔ КИМ2,6):
```
HERMES → GitHub: tasks/, картинки, промты
КИМ2,6 → GitHub: results/, код, скриншоты
```

### Open Design (КИМ2,6 ↔ Дизайн):
```
КИМ2,6 → Open Design: промт
Open Design → КИМ2,6: HTML/CSS код
```

---

## 7. СХЕМА РАБОТЫ С OPEN DESIGN

### Шаг 1: HERMES готовит промт
```
HERMES:
1. Получил задачу от Олега
2. Сгенерировал картинки (image_01)
3. Написал промт для Open Design
4. Создал task_XXX.md с промтом и картинками
5. Push в GitHub
```

### Шаг 2: КИМ2,6 выполняет
```
КИМ2,6:
1. git pull
2. Открывает Open Design
3. Загружает картинки из task_XXX.md
4. Вставляет промт
5. Kimi CLI генерирует дизайн
6. OpenCode дорабатывает
7. Сохраняет результат
8. Push в GitHub
```

### Шаг 3: HERMES проверяет
```
HERMES:
1. git pull
2. Проверяет results/result_XXX/
3. Если ок — отправляет Олегу
4. Если нет — отправляет на доработку
```

---

## 8. MONITORING И КОНТРОЛЬ

### Kanban — Статусы задач:
```
TRIAGE    → Новая задача, высокий приоритет
READY     → Готова к выполнению
RUNNING   → В работе (КИМ2,6)
BLOCKED   → Заблокирована
DONE      → Завершена
```

### Команды мониторинга:
```bash
# HERMES — Посмотреть все задачи
hermes kanban --board default ls

# HERMES — Статистика
hermes kanban --board default stats

# HERMES — Следить в реальном времени
hermes kanban --board default watch
```

### GitHub — Синхронизация:
```bash
# HERMES — Push задачу
git add . && git commit -m "Task for Kim2-6" && git push

# КИМ2,6 — Получить задачу
git clone https://github.com/matryoshkaailab-cyber/matryoshka-digital-v2.git
git pull

# HERMES — Получить результат
git pull
```

---

## 9. АВТОМАТИЗАЦИЯ

### Cron задачи HERMES:
```
# Каждые 30 минут — проверять новые задачи
*/30 * * * * git -C /root/matryoshka pull

# Каждый час — отчёт Олегу
0 * * * * hermes kanban --board default ls >> /tmp/status.txt
```

### GitHub Webhook (опционально):
```
Событие: push
URL: http://85.137.166.209:8080/webhook
Триггер: новый коммит в main
Действие: HERMES проверяет results/
```

---

## 10. ПЕРВЫЕ ЗАДАЧИ ДЛЯ ТЕСТИРОВАНИЯ

### Задача 1: Лендинг DATALINK PRO
```bash
# HERMES создаёт
cat > /root/matryoshka/tasks/task_002_landing.md << 'EOF'
# ЗАДАЧА: Лендинг DATALINK PRO
# Промт: "Design a modern VPN service landing page with navy blue theme"
# Картинки: [generated images]
# Система: Stripe-style
EOF
git push
```

### Задача 2: Дашборд MATRYOSHKA
```bash
# HERMES создаёт
cat > /root/matryoshka/tasks/task_003_dashboard.md << 'EOF'
# ЗАДАЧА: Дашборд MATRYOSHKA DIGITAL
# Промт: "Design an analytics dashboard with dark theme"
# Картинки: [none]
# Система: Linear-style
EOF
git push
```

---

## 11. РЕЗЕРВНОЕ КОПИРОВАНИЕ

### Автобэкап результатов:
```bash
# HERMES — Бэкап results/
0 */6 * * * tar -czf /root/backups/results_$(date+\%Y\%m\%d\%H).tar.gz /root/matryoshka/results/

# Отправка на Яндекс.Диск
0 */6 * * * curl -T /root/backups/results_*.tar.gz https://uploader.yandex.ru/
```

---

## 12. КОНТАКТЫ И АККАУНТЫ

### HERMES (Я):
- Telegram: @oleg_industry_bot
- Сервер: 85.137.166.209
- GitHub: matryoshkaailab-cyber

### КИМ2,6:
- OpenCode на ПК
- GitHub: [указать]
- Telegram: [указать]

### OPEN DESIGN:
- GitHub: nexu-io/open-design
- Локально: http://localhost:7456

---

## 13. ВЕРСИИ И ОБНОВЛЕНИЯ

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0 | 08.05.2026 | Начальная версия документа |

---

## 14. ЧЕКЛИСТ ЗАПУСКА

```
□ HERMES: Git синхронизация настроена
□ HERMES: Kanbanboard создан
□ HERMES: tasks/results папки готовы
□ КИМ2,6: SSH ключ на сервере
□ КИМ2,6: OpenCode установлен
□ КИМ2,6: Open Design установлен
□ КИМ2,6: GitHub доступ настроен
□ ОЛЕГ: Понимает схему работы
□ ОЛЕГ: Готов давать задачи
□ ГОТОВО К РАБОТЕ
```

---

## 15. ПРИМЕР ПОЛНОГО ЦИКЛА

```
ОЛЕГ → "Сделай лендинг для DATALINK PRO"
      ↓
HERMES:
  1. Анализирует задачу
  2. Генерирует logo и иллюстрации (image_01)
  3. Пишет промт для Open Design
  4. Создаёт task_002_landing.md
  5. Push в GitHub
  6. Kanban: t_XXX triage → ready → assigned to kimi2-6
      ↓
КИМ2,6:
  1. git pull
  2. Читает task_002_landing.md
  3. Запускает Open Design
  4. Вставляет промт + картинки
  5. Kimi K2.6 генерирует дизайн
  6. OpenCode дорабатывает
  7. Сохраняет в results/result_002/
  8. Git push
  9. Kanban: done
      ↓
HERMES:
  1. git pull
  2. Проверяет результат
  3. Отправляет Олегу в Telegram
      ↓
ОЛЕГ: "Отлично, ещё дашборд!"
```

---

**КОНЕЦ ДОКУМЕНТА**
Дата: 08.05.2026
Автор: HERMES (MATRYOSHKA DIGITAL)