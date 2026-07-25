import os
import gradio as gr
from dotenv import load_dotenv

# 1. Импортируем OpenAI через Langfuse для автоматического перехвата и логирования
from langfuse.openai import OpenAI

# Загружаем переменные окружения из файла .env
load_dotenv()

# 2. Инициализируем клиент. Langfuse автоматически начнет записывать все вызовы этого клиента
client = OpenAI(
    api_key=os.getenv("PROXY_API_KEY"),
    base_url=os.getenv("PROXY_BASE_URL", "https://proxyapi.ru/v1"), # Добавлен /v1, так как это стандарт для OpenAI-совместимых API
)

# Загружаем модель из .env
MODEL_NAME = os.getenv("DEFAULT_MODEL", "gpt-4o")

def predict(message, history):
    try:
        # Формируем сообщения в формате, ожидаемом OpenAI API
        # Если вы хотите передавать историю диалога, ее нужно преобразовать в список словарей
        messages = [{"role": "user", "content": message}]
        
        # Отправляем запрос к API (стандартный chat.completions)
        response = client.chat.completions.create(
            model=MODEL_NAME, 
            messages=messages
        )
        
        # Возвращаем текстовый ответ
        return response.choices[0].message.content
        
        # ПРИМЕЧАНИЕ: Если ваш прокси требует именно новый Responses API, 
        # замените блок выше на:
        # response = client.responses.create(model=MODEL_NAME, input=message)
        # return response.output_text
        
    except Exception as e:
        # Langfuse автоматически запишет эту ошибку в трейс вместе со стеком вызовов
        return f"Произошла ошибка: {str(e)}"

# Создаем стандартный интерфейс чата с помощью Gradio
demo = gr.ChatInterface(
    fn=predict, 
    title="Мой AI Собеседник",
    description=f"Чат-интерфейс работает на модели: {MODEL_NAME} с мониторингом Langfuse"
)

if __name__ == "__main__":
    # Запускаем сервер на порту 7860 и разрешаем подключения извне (0.0.0.0)
    demo.launch(server_name="0.0.0.0", server_port=7860)
