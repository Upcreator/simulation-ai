from pathlib import Path

import gradio as gr

from src.builders.prompt_builder import PromptBuilder
from src.services.openai_service import OpenAIService


ROOT = Path(__file__).parent

builder = PromptBuilder(ROOT)

service = OpenAIService()


def predict(message, history):

    prompt = builder.build()

    return service.ask(
        prompt,
        message,
    )


demo = gr.ChatInterface(
    fn=predict,
    title="AI Government Simulator",
    description="Version 0.1",
)


if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
    )
