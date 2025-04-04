# Используем официальный образ Python
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт для FastAPI
EXPOSE 8000

# Запускаем сервер (без --reload, он будет добавлен в docker-compose.override.yml)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
