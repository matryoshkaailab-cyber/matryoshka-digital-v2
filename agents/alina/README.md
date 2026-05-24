# Агент: АЛИНА (@NikolaAlinaBot)

**Статус:** Активен
**Владелец:** Nikolay (Варнаков Николай)
**Назначение:** Персональный напарник для Николая — продажи, поддержка, общение
**Платформа:** Telegram
**Gateway profile:** nikolay

## Вводные данные (из nikolay-alina-briefing.md)

### Кто Nikolay
- В разводе, одинокий
- Бывший бизнесмен (недвижимость), потерял всё
- Продаёт последнее чтобы запустить проект (бюджет ~400к руб)
- Нужен НАПАРНИК, не просто бот
- Nikolay должен ГОРДИТЬСЯ АЛИНОЙ перед другими = маркетинг MATROSHKA

### Ключевые правила
1. **ТОЛЬКО РУССКИЙ** — всегда, без исключений. Никогда на английском
2. **SOUL.md** — /root/.hermes/profiles/nikolay/SOUL.md
3. **Голосовые** — полные предложения с точками и запятыми, не обрывать мысль

## Конфигурация (реальная)

### /root/.hermes/profiles/nikolay/config.yaml
```yaml
model:
  provider: minimax
  default: MiniMax-M2.7

tts:
  provider: edge
  edge:
    voice: ru-RU-SvetlanaNeural
  speed: 0.95

voice:
  auto_tts: true
  provider: edge
  edge:
    voice: ru-RU-SvetlanaNeural

terminal:
  timeout: 600
  cwd: /root/matryoshka/cases/nikolay

tirth_enabled: false (из памяти HERMES)
```

### Файлы
- SOUL.md: /root/.hermes/profiles/nikolay/SOUL.md
- Config: /root/.hermes/profiles/nikolay/config.yaml
- Папка кейса: /root/matryoshka/cases/nikolay/

## Исправленные проблемы (21.05.2026)
1. Голосовые приходили как файлы — исправлено в tts_tool.py:1861
2. Скорость голоса 0.95 (чуть медленнее, естественнее)
3. Пунктуация в голосовых (полные предложения)

## Проблемы и боли Nikolay
(Заполняется в pain-log.md)

## Кейсы
- Nikolay: /root/matryoshka/cases/nikolay/
  - pain-log: /root/matryoshka/agents/alina/cases/nikolay/pain-log.md
  - PASSPORT.md: /root/matryoshka/cases/nikolay/PASSPORT.md (если есть)

## TODO
- [ ] Проверить Bookmate API (статус: 404)
- [ ] Наблюдать за разговорами Nikolay + Алина
- [ ] Фиксировать боли Nikolay в pain-log.md
- [ ] Проверить что SOUL.md и конфиг совпадают