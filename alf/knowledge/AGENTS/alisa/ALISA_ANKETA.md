# ALISA — Анкета Агента

## Досье
- **Роль:** Маркетолог / Дизайнер / Таргетолог
- **Рой:** 🔴 Красный Рой (Витрина)
- **Платформа:** Python (aiogram + FastAPI)
- **Telegram:** @AlisaMatryBot
- **API:** 127.0.0.1:8448
- **Управляется:** `alisa2.service` (Telegram bot) + `alisa2-api.service` (FastAPI)

## Связи
- **HERMES** — дирижёр (нет прямой интеграции, потенциально через файловую очередь)
- **n8n** — автопостинг (workflow существует, не активирован)

## Текущий стек моделей
| Функция | Модель | Провайдер |
|---------|--------|-----------|
| Текст | `deepseek/deepseek-v4-flash:free` | OpenRouter |
| Видение | `google/gemini-2.0-flash-lite-preview-02-05:free` | OpenRouter |
| Изображение | `image-01` / `image-01-live` | MiniMax |
| Энхансер | `nvidia/nemotron-3-super-120b-a12b:free` | OpenRouter |
| Голос | ❌ НЕТ | — |

## Возможности (сейчас)
- ✅ Генерация постов (текст + изображение)
- ✅ Генерация рекламных креативов
- ✅ Маркетинговые стратегии
- ✅ Контент-планы
- ✅ Креативные идеи
- ✅ Анализ изображений (vision)
- ✅ Брендбук (обновляемый)
- ✅ Хранилище описаний (6 категорий)
- ✅ Swagger UI на :8448/docs

## План разработки

### P0 — СЕЙЧАС (26.05.2026) ✅
- [x] План сохранён на VPS и в Obsidian
- [x] 1. Промпт-инжиниринг — библиотека шаблонов (prompt_templates.py)
- [x] 2. DeepSeek V4 Flash — смена модели
- [x] 3. n8n автопостинг — активация (workflow ID: aaf33877)
- [x] 4. /design_image, /post_aida, /post_pas, /ad, /seo_post, /brand_post — новые команды
- [x] 5. API endpoints: /api/v1/generate-aida, /api/v1/generate-pas, /api/v1/generate-seo, /api/v1/generate-ad, /api/v1/design-style, /api/v1/styles

### P1 — ЭТА НЕДЕЛЯ
- [ ] 5. Instagram + VK постинг (social.py)
- [ ] 6. brand_memory.json — синхронизация полей
- [ ] 7. Voice (Whisper STT + MiniMax TTS)

### P2 — ЧЕРЕЗ НЕДЕЛЮ
- [ ] 8. Аналитика и контент-календарь

## Git
- Локальный код: `C:\matryoshka\bots\alisa\`
- VPS: `/root/matryoshka/alisa2/`
- VPS отстаёт от локального — требуется синхронизация

---
*Обновлено: 2026-05-26*
