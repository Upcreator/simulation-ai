# Легкий образ Python
FROM python:3.11-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем список зависимостей
COPY requirements.txt .

# Устанавливаем библиотеки без сохранения кэша (для экономии места)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код и файл .env в контейнер
COPY main.py .
COPY .env .

# Команда для запуска скрипта
CMD ["python", "main.py"]
