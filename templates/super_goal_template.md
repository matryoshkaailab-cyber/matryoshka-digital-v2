# SUPER GOAL — Human-AI Handshake Template

**Формат для задач требующих участия человека**

---

## СТРУКТУРА SUPER GOAL:

```markdown
## GOAL: [Название задачи]

## TRANSACTIONS
| # | Кто | Что делает | Критерий完成 |
|---|-----|------------|-------------|
| 1 | HERMES | Подготовить структуру | docs/ структура создана |
| 2 | HUMAN | Одобрить / скорректировать | OK от Олега |
| 3 | HERMES | Выполнить работу | N страниц/файлов |
| 4 | HUMAN | Принять результат | Approve |
| 5 | HERMES | Финальный фикс (если нужно) | Готово |

## JUDGE CRITERIA
[Как понять что цель достигнута]

## TIMELINE
- Начало: [дата]
- Дедлайн: [дата]
- Cost limit: [если есть]

## ESCALATION
[Что делать если HUMAN не отвечает X дней]
```

---

## ПРИМЕР: SEO статья для клиента

```markdown
## GOAL: SEO статья — [КЛИЕНТ]

## TRANSACTIONS
| # | Кто | Что делает | Критерий完成 |
|---|-----|------------|-------------|
| 1 | HERMES | Найти 5 ключевых слов | keywords.md создан |
| 2 | HUMAN | Утвердить ключевики | OK от клиента |
| 3 | HERMES | Написать черновик | article_draft.md |
| 4 | HUMAN | Правки | Список правок |
| 5 | HERMES | Финальная версия | article_final.md |
| 6 | HUMAN | Publish | Опубликовано |

## JUDGE CRITERIA
Статья опубликована на сайте клиента с правильными keywords.

## TIMELINE
- Начало: Понедельник
- Дедлайн: Пятница
- Cost limit: Free (MiniMax)

## ESCALATION
Если HUMAN не ответил 48ч → напомнить 1 раз, затем остановить.
```

---

## ПРИМЕР: Новый сайт для клиента

```markdown
## GOAL: Лендинг — [КЛИЕНТ]

## TRANSACTIONS
| # | Кто | Что делает | Критерий完成 |
|---|-----|------------|-------------|
| 1 | HERMES | Собрать бриф | brief.md |
| 2 | HUMAN | Заполнить бриф | brief_approved.md |
| 3 | HERMES | Wireframes (3 варианта) | wireframes/ |
| 4 | HUMAN | Выбрать вариант | variant_X selected |
| 5 | HERMES | Дизайн | design.png |
| 6 | HUMAN | Правки | change list |
| 7 | HERMES | Frontend | site/index.html |
| 8 | HUMAN | Тест | OK |
| 9 | HERMES | Deploy | https://site.com |

## JUDGE CRITERIA
Сайт работает на prod домене, клиент подтвердил.

## TIMELINE
- Начало: По получению брифа
- Дедлайн: 2 недели
- Cost limit: 18K ₽ (услуга MATRYOSHKA)

## ESCALATION
Если HUMAN не ответил 72ч → статус "blocked by client", продолжить без него.
```

---

## ПРАВИЛА SUPER GOALS:

1. **Всегда 2 стороны** — human и hermes
2. **Критерий完成 = условие перехода** к следующему шагу
3. **HUMAN не отвечает** → напомнить 1 раз, потом остановитьGoal
4. **Judge Criteria** — как понять что DONE
5. **Timeline** — реальные сроки

---

**Создан:** 25.05.2026