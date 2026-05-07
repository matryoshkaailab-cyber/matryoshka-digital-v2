FROM nikolaik/python-nodejs:python3.11-nodejs20

# Устанавливаем Hermes Agent
RUN pip install hermes-agent

# Создаём рабочую директорию
WORKDIR /root

# Порт для dashboard (если понадобится)
EXPOSE 9110

# Команда запуска
CMD ["hermes", "gateway", "run"]
