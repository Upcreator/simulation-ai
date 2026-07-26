from langfuse import Langfuse
from langfuse.openai import OpenAI

from src.config import Config


class OpenAIService:

    def __init__(self):

        self.langfuse = Langfuse(
            public_key=Config.LANGFUSE_PUBLIC_KEY,
            secret_key=Config.LANGFUSE_SECRET_KEY,
            host=Config.LANGFUSE_HOST,
        )

        self.client = OpenAI(
            api_key=Config.PROXY_API_KEY,
            base_url=Config.PROXY_BASE_URL,
        )

    def ask(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self.client.responses.create(
            model=Config.DEFAULT_MODEL,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        self.langfuse.flush()

        return response.output_text