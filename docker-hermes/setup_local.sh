#!/bin/bash
# Hermes Local Setup для Windows (через Docker)

echo "=== Hermes Local Setup ==="
echo ""

# Проверка Docker
if ! command -docker &> /dev/null; then
    echo "Docker не найден. Установи Docker Desktop: https://docker.com/get-started"
    exit 1
fi

# Создаём папку для данных
mkdir -p hermes_data

# Копируем конфиг с VPS
echo "Копирование конфигурации..."
if [ -f /root/.hermes/config.yaml ]; then
    cp /root/.hermes/config.yaml hermes_data/
    echo "✓ config.yaml скопирован"
fi

# Создаём .env если нужен
if [ ! -f .env ]; then
    echo "Создание .env..."
    touch hermes_data/.env
    echo "# Добавь свои API ключи сюда"
fi

# Запуск
echo ""
echo "Запуск Hermes..."
docker run -d \
    --name hermes-local \
    -v $(pwd)/hermes_data:/root/.hermes \
    -p 9110:9110 \
    -p 9119:9119 \
    -it hermes-local bash

echo ""
echo "Готово! Dashboard: http://localhost:9119"
echo "Для входа: hermes / localhost:9110"
