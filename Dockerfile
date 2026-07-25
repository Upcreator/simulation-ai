FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY .env .

# Открываем порт для веб-интерфейса
EXPOSE 7860

CMD ["python", "main.py"]
