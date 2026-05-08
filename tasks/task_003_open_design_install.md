# ЗАДАЧА №003 — Установка Open Design
## Дата: 08.05.2026
## Статус: Ожидает выполнения
## Исполнитель: АЛЕКС (КИМ2,6)

---

## ТИП ЗАДАЧИ
Установка и настройка

---

## ОПИСАНИЕ
Установить Open Design на твой ПК для генерации дизайнов.

Open Design — локальный open-source аналог Claude Design (32.8k stars GitHub).
Бесплатный. Поддерживает Kimi CLI как AI-агента.

---

## ПРИОРИТЕТ: HIGH

---

## ПОРЯДОК УСТАНОВКИ

### 1. Проверь установленные инструменты

```bash
# Проверь есть ли Docker
docker --version

# Проверь есть ли Kimi CLI
kimi --version
# или
opencode --version
```

---

### 2. Если Docker не установлен — установи

**Windows:**
```powershell
# Скачай Docker Desktop с https://docker.com
# Или используй WSL2
wsl --install
```

**Linux:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**Mac:**
```bash
brew install --cask docker
```

---

### 3. Клонируй репозиторий

```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design
```

---

### 4. Запусти через Docker

```bash
docker compose up -d
```

Дождись запуска (1-2 минуты).

---

### 5. Проверь что работает

Открой в браузере:
```
http://localhost:7456
```

Должно открыться приложение Open Design.

---

### 6. Настрой агента

При первом запуске:
1. Выбери агента: **Kimi CLI** (или OpenCode)
2. Проверь что агент определяется
3. Выбери дизайн-систему для старта (например Stripe или Linear)

---

## ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

- ✅ Open Design открывается в браузере
- ✅ Агент (Kimi CLI) определяется и работает
- ✅ Можешь сгенерировать тестовый дизайн

---

## ДОКУМЕНТАЦИЯ

- Репозиторий: https://github.com/nexu-io/open-design
- Quickstart: https://github.com/nexu-io/open-design/blob/main/QUICKSTART.md
- Сайт: https://open-design.ai

---

## ССЫЛКА НА ПОЛНЫЙ ГАЙД

Все детали в файле:
`/root/matryoshka/cases/datalink-pro/docs/OPEN_DESIGN_ANALYSIS.md`

---

## ПРОМОЖИРОВАННЫЙ СЛЕДУЮЩИЙ ШАГ

После установки — протестируй:
1. Введи промт: "Design a simple landing page with navy blue theme"
2. Выбери агента Kimi CLI
3. Посмотри результат

---

## КОНТАКТЫ

Если возникли вопросы — пиши в Telegram @oleg_industry_bot
