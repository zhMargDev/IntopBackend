# Используем официальный образ Python 3.11-slim как основу
FROM python:3.11-slim-buster

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем requirements.txt в контейнер
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . .

# Создаем директорию для конфигурации Firebase
COPY firebase_conf/firebase_config.json /app/firebase_conf/firebase_config.json

# Устанавливаем порт для веб-сервера
EXPOSE 8000

# Команда для запуска приложения (примените свое имя модуля и порта)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
