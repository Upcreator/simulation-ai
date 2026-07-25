import os
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем данные из файла .env
load_dotenv()

# Инициализируем клиент, подставляя ключ из переменных окружения
client = OpenAI(
    api_key=os.getenv("PROXY_API_KEY"),
    base_url="https://api.proxyapi.ru/openai/v1",
)

response = client.responses.create(
    model="gpt-4o", 
    input="Привет!"
)

print(response.output_text)
