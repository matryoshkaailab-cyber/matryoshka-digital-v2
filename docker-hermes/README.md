# Hermes Local — Windows Setup

## Быстрый старт

### 1. Установка
```bash
cd docker-hermes
docker build -t hermes-local .
```

### 2. Первый запуск
```bash
# Скопируй config.yaml с VPS
scp root@85.137.166.209:/root/.hermes/config.yaml ./hermes_data/

# Или просто создай новый
mkdir -p hermes_data
cp /root/.hermes/config.yaml hermes_data/ 2>/dev/null || true
```

### 3. Запуск
```bash
docker run -d \
    --name hermes-local \
    -v $(pwd)/hermes_data:/root/.hermes \
    -p 9110:9110 \
    hermes-local
```

## Структура
```
docker-hermes/
├── Dockerfile
├── setup_local.sh
├── README.md
└── hermes_data/        # сюда данные
```

## Важно
- Токены и ключи — в hermes_data/.env
- Конфиг — hermes_data/config.yaml
- Данные персистентны между запусками

## Проблемы?
- Windows: используй PowerShell или Git Bash
- Docker должен быть запущен
