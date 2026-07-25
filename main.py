import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Инициализируем клиент OpenAI
client = OpenAI(
    api_key=os.getenv("PROXY_API_KEY"),
    base_url="https://proxyapi.ru",
)

# Загружаем модель из .env
MODEL_NAME = os.getenv("DEFAULT_MODEL", "gpt-4o")

def predict(message, history):
    try:
        # Отправляем запрос к API
        response = client.responses.create(
            model=MODEL_NAME, 
            input=message
        )
        # Возвращаем текстовый ответ
        return response.output_text
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

# Создаем стандартный интерфейс чата с помощью Gradio
demo = gr.ChatInterface(
    fn=predict, 
    title="Мой AI Собеседник",
    description=f"Чат-интерфейс работает на модели: {MODEL_NAME}"
)

if __name__ == "__main__":
    # Запускаем сервер на порту 7860 и разрешаем подключения извне (0.0.0.0)
    demo.launch(server_name="0.0.0.0", server_port=7860)
