import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("langgraph_characters")

# === Прокси / модель ===
PROXY_API_KEY = os.getenv("PROXY_API_KEY")
PROXY_BASE_URL = os.getenv("PROXY_BASE_URL", "https://api.proxyapi.ru/openai/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")

# === Langfuse (нужны только LANGFUSE_* переменные в .env — CallbackHandler читает их сам) ===
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

# === Управление долгосрочной памятью / контекстом ===
MAX_MESSAGES_BEFORE_SUMMARY = int(os.getenv("MAX_MESSAGES_BEFORE_SUMMARY", 12))
KEEP_LAST_MESSAGES = int(os.getenv("KEEP_LAST_MESSAGES", 6))

DB_PATH = os.getenv("DB_PATH", "data/checkpoints.sqlite")
os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)

logger.info("=" * 50)
logger.info("ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ:")
logger.info(f"PROXY_API_KEY: {'задан' if PROXY_API_KEY else 'НЕ ЗАДАН'}")
logger.info(f"PROXY_BASE_URL: {PROXY_BASE_URL}")
logger.info(f"DEFAULT_MODEL: {DEFAULT_MODEL}")
logger.info(f"LANGFUSE_PUBLIC_KEY: {'задан' if LANGFUSE_PUBLIC_KEY else 'НЕ ЗАДАН'}")
logger.info(f"LANGFUSE_SECRET_KEY: {'задан' if LANGFUSE_SECRET_KEY else 'НЕ ЗАДАН'}")
logger.info(f"LANGFUSE_HOST: {LANGFUSE_HOST}")
logger.info("=" * 50)


def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    """Клиент LLM поверх OpenAI-совместимого прокси."""
    return ChatOpenAI(
        model=DEFAULT_MODEL,
        api_key=PROXY_API_KEY,
        base_url=PROXY_BASE_URL,
        temperature=temperature,
    )


def get_langfuse_handler():
    """Возвращает langchain-callback для трейсинга в Langfuse, либо None."""
    try:
        from langfuse.langchain import CallbackHandler
        handler = CallbackHandler()
        logger.info("✅ Langfuse callback инициализирован")
        return handler
    except Exception as e:
        logger.warning(f"⚠️ Langfuse callback не инициализирован: {e}")
        return None
