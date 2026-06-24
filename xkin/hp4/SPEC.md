# XKIN HP4 — TWS Наушники

**Папка товара:** `/root/matryoshka/xkin/hp4/`
**Статус:** Готов к работе
**Дата создания:** 2026-06-04

---

## 📁 СТРУКТУРА ПАПКИ

```
hp4/
├── SPEC.md          ← Этот файл (характеристики, промты, шаблон)
├── refs/             ← Референсы для Gemini (PNG, изолированные)
│   ├── ref_nobg_1.png
│   ├── ref_nobg_2.png
│   ├── ref_nobg_3.png
│   ├── ref_nobg_4.png
│   └── ref_nobg_5.png
└── cards/            ← Сгенерированные карточки
    ├── card_1.png
    ├── card_2.png
    └── card_3.png
```

---

## 🎧 ХАРАКТЕРИСТИКИ (из Gemini, 2026-06-04)

```
Модель:           XKIN HP4
Тип:               TWS (True Wireless Stereo) наушники

Водные данные:
• IPX5 — водостойкость (защита от брызг воды)

Батарея:
• Ёмкость батареи: 500 mAh
• Время работы музыки: 40 часов
• Время ожидания: 400 часов

Зарядка:
• Порт зарядки: USB-C

Беспроводность:
• Bluetooth 5.3
• Радиус действия: ≥10 метров

Функции:
• ANC — активное шумоподавление
• ENC — чёткий звук при звонках
• Сенсорное управление
• Холл переключатель (Hall switch)

Гарантия:         12 месяцев
```

---

## 🎨 УТВЕРЖДЁННЫЙ СТИЛЬ КАРТОЧЕК

```
Фон:    #0f0f1a → #1a1a2e (тёмный градиент)
Акцент: #FF6600 (оранжевый)
Текст:  белый, крупный, жирный sans-serif, РУССКИЙ
```

---

## 📝 ПРОМТЫ ДЛЯ 3 КАРТОЧЕК

### Карточка 1 — ГЛАВНАЯ (инфографика на белом)

```
Place this device in a modern minimalist infographic card.

The device is shown in the reference images — use it as-is, do not modify.

Card design:
- Background: white #FFFFFF
- Device at top, centered
- Clean typography below
- Orange #FF6600 accent lines

Text (russian):
🎧 XKIN HP4
TWS НАУШНИКИ
• Bluetooth 5.3
• IPX5 водостойкость
• 40 часов музыки
• ANC + ENC
• 500 mAh
• Сенсорное управление
Гарантия 12 месяцев

Keep the device exactly as shown in reference — do not add elements not in the reference.
```

### Карточка 2 — SPLIT LAYOUT (тёмный фон)

```
Place this device in a modern minimalist infographic card with split layout.

The device is shown in the reference images — use it as-is, do not modify.

Card design:
- Background: dark gradient #0f0f1a to #1a1a2e
- Left side: large device image
- Right side: specs in clean typography
- Orange #FF6600 accent lines

Text (russian):
🎧 XKIN HP4
TWS НАУШНИКИ

40 ЧАСОВ
музыки без подзарядки

IPX5
водостойкость

Bluetooth 5.3
≥10 метров

ANC + ENC
чёткий звук

Гарантия 12 месяцев

Keep the device exactly as shown in reference.
```

### Карточка 3 — КОМПАКТНОСТЬ (рука держит)

```
Place this compact device in a modern minimalist infographic card showing a hand holding it.

The device is shown in the reference images — use it as-is, do not modify.

IMPORTANT: Show a human hand holding the device. The device fits in the palm. This emphasizes compact size.

Card design:
- Background: dark gradient #0f0f1a to #1a1a2e
- Device being held in a human hand (palm up, device resting on it)
- Modern clean layout
- Orange #FF6600 accent lines

Text (russian):
КОМПАКТНОСТЬ
Всегда с собой

• Лёгкие — всего 35г
• Помещается в ладонь
• USB-C зарядка
• 40 часов музыки

Гарантия 12 месяцев

Keep the device exactly as shown in reference — small TWS earbuds, no case, compact form.
```

---

## 🔑 КЛЮЧЕВЫЕ ПРАВИЛА АЛГОРИТМА

### При получении задачи "делаем карточки для X":

1. **Найти папку товара** → `/root/matryoshka/xkin/{product}/SPEC.md`
2. **Прочитать характеристики** из SPEC.md
3. **Взять референсы** из `{product}/refs/` (PNG файлы)
4. **Следовать промтам** из SPEC.md (Карточка 1, 2, 3)
5. **Генерировать** через Gemini с 4 референсами за один запрос
6. **Сохранять** результат в `{product}/cards/`
7. **Проверять формат** (JPEG → .jpg, PNG → .png)
8. **Отправлять** через curl напрямую в Telegram API

### НИКОГДА НЕ:
- Брать референсы из другой папки
- Использовать файлы не из папки товара
- Гадать характеристики — брать из SPEC.md
- Смешивать продукты между собой

---

## 📦 ПУТИ

```
Референсы:  /root/matryoshka/xkin/hp4/refs/
Карточки:   /root/matryoshka/xkin/hp4/cards/
Этот файл:  /root/matryoshka/xkin/hp4/SPEC.md
```