from pathlib import Path

import gradio as gr

from src.services.openai_service import OpenAIService


ROOT = Path(__file__).parent


SYSTEM_PROMPT = (
    ROOT /
    "prompts" /
    "system.md"
).read_text(
    encoding="utf-8"
)


service = OpenAIService()


def predict(message, history):

    return service.ask(
        SYSTEM_PROMPT,
        message,
    )


demo = gr.ChatInterface(
    fn=predict,
    title="AI Simulator",
    description="Первая версия симулятора",
)


if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
    )
