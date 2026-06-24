# DATALINK PRO — Еженедельный отчёт

**Генерируется автоматически каждую пятницу в 18:00 МСК**

---

## ШАБЛОН ОТЧЁТА:

```
📊 ОТЧЁТ DATALINK PRO — [НЕДЕЛЯ X]

📅 Период: [ДАТА] — [ДАТА]

💰 ФИНАНСЫ:
• Новых клиентов: X
• Продлений: X  
• Выручка: X ₽
• Trial → Paid конверсия: X%

👥 КЛИЕНТЫ:
• Активных: XX
• Новых: X
• Отвалившихся: X

🔧 ТЕХНИКА:
• Uptime: 99.X%
• Сбоев за неделю: X
• Саппорт тикетов: X

📱 БОТ @datalink_pro_bot:
• Обращений: XX
• Продаж: X
• Средний чек: XXX ₽

⚠️ ПРОБЛЕМЫ:
• [список или "нет"]

💡 РЕКОМЕНДАЦИИ:
• [2-3 actionable точки]

---
MATRYOSHKA DIGITAL | Hermes Agent
```

---

## КАК СОБИРАТЬ ДАННЫЕ:

```bash
# 1. База клиентов
sqlite3 /opt/vpn_bot/users.db "SELECT COUNT(*) FROM users WHERE active=1;"

# 2. Новые за неделю
sqlite3 /opt/vpn_bot/users.db "SELECT COUNT(*) FROM users WHERE created_at > date('now', '-7 days');"

# 3. Платежи из webhook логов
grep "yookassa" /root/matryoshka/logs/*.log | tail -50

# 4. Uptime
uptime && echo "---" && curl -s -o /dev/null -w "%{http_code}" https://vpn.xn----7sbaowmfrljlq.xn--p1ai/
```

---

**Создан:** 25.05.2026