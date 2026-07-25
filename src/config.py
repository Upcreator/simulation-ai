import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    PROXY_API_KEY = os.getenv("PROXY_API_KEY")

    PROXY_BASE_URL = os.getenv(
        "PROXY_BASE_URL",
        "https://api.proxyapi.ru/openai/v1"
    )

    DEFAULT_MODEL = os.getenv(
        "DEFAULT_MODEL",
        "gpt-4o"
    )

    LANGFUSE_PUBLIC_KEY = os.getenv(
        "LANGFUSE_PUBLIC_KEY"
    )

    LANGFUSE_SECRET_KEY = os.getenv(
        "LANGFUSE_SECRET_KEY"
    )

    LANGFUSE_HOST = os.getenv(
        "LANGFUSE_HOST"
    )