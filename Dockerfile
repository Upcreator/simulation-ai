# Используем легкий и стабильный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
# --no-cache-dir уменьшает размер образа
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY app.py .
COPY src/ ./src/
COPY characters/ ./characters/

# Папка для sqlite-чекпоинтов LangGraph (история диалогов, резюме).
# Создаём заранее, чтобы SqliteSaver не падал при первом запуске.
RUN mkdir -p data

# .env файл лучше не копировать в образ из соображений безопасности,
# его удобнее передавать при запуске контейнера через флаг --env-file
# Но если нужно для тестов, раскомментируйте строку ниже:
# COPY .env .

# Открываем порт, который использует Gradio
EXPOSE 7860

# Запускаем приложение
CMD ["python", "app.py"]
