import os
import gradio as gr
from dotenv import load_dotenv
from langfuse.openai import OpenAI
from langfuse import Langfuse
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# === ОТЛАДКА: Выводим все переменные окружения ===
logger.info("=" * 50)
logger.info("ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ:")
logger.info(f"PROXY_API_KEY: {'задан' if os.getenv('PROXY_API_KEY') else 'НЕ ЗАДАН'}")
logger.info(f"PROXY_BASE_URL: {os.getenv('PROXY_BASE_URL')}")
logger.info(f"DEFAULT_MODEL: {os.getenv('DEFAULT_MODEL')}")
logger.info(f"LANGFUSE_PUBLIC_KEY: {'задан' if os.getenv('LANGFUSE_PUBLIC_KEY') else 'НЕ ЗАДАН'}")
logger.info(f"LANGFUSE_SECRET_KEY: {'задан' if os.getenv('LANGFUSE_SECRET_KEY') else 'НЕ ЗАДАН'}")
# ИЗМЕНЕНО: Проверяем именно LANGFUSE_HOST
logger.info(f"LANGFUSE_HOST: {os.getenv('LANGFUSE_HOST')}")
logger.info("=" * 50)

# === Явная инициализация Langfuse ===
try:
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST")  # ИЗМЕНЕНО: Используем LANGFUSE_HOST (стандарт для Python SDK)
    )
    logger.info("✅ Langfuse успешно инициализирован!")
    
    # Проверяем соединение
    langfuse.flush()
    logger.info("✅ Langfuse flush выполнен успешно!")
    
except Exception as e:
    logger.error(f"❌ Ошибка инициализации Langfuse: {e}")
    raise

# === Инициализация клиента OpenAI ===
client = OpenAI(
    api_key=os.getenv("PROXY_API_KEY"),
    base_url=os.getenv("PROXY_BASE_URL", "https://api.proxyapi.ru/openai/v1"),
)

MODEL_NAME = os.getenv("DEFAULT_MODEL", "gpt-4o")
logger.info(f"🚀 Используем модель: {MODEL_NAME}")

def predict(message, history):
    logger.info(f"📩 Получено сообщение: {message[:50]}...")
    
    try:
        logger.info(f"📤 Отправка запроса к API...")
        
        response = client.responses.create(
            model=MODEL_NAME, 
            input=message
        )
        
        logger.info(f"✅ Получен ответ от API")
        logger.info(f"📝 Ответ: {response.output_text[:100]}...")
        
        return response.output_text
        
    except Exception as e:
        logger.error(f"❌ Ошибка при вызове API: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"Произошла ошибка: {str(e)}"

demo = gr.ChatInterface(
    fn=predict, 
    title="Мой AI Собеседник",
    description=f"Чат-интерфейс работает на модели: {MODEL_NAME} с мониторингом Langfuse"
)

if __name__ == "__main__":
    logger.info("🌐 Запуск сервера Gradio на порту 7860...")
    demo.launch(server_name="0.0.0.0", server_port=7860)
