import uuid
import gradio as gr
from langchain_core.messages import HumanMessage

from src.characters import load_all_characters
from src.graph_chat import build_chat_graph
from src.graph_dialogue import build_dialogue_graph
from src.config import get_langfuse_handler, logger

characters = load_all_characters("characters")
character_choices = [(c.name, c.key) for c in characters.values()]

logger.info(f"🎭 Загружены персонажи: {[c.key for c in characters.values()]}")

chat_graph = build_chat_graph()
dialogue_graph = build_dialogue_graph()

langfuse_handler = get_langfuse_handler()
callbacks = [langfuse_handler] if langfuse_handler else []


# ---------- Режим 1: чат пользователя с одним персонажем ----------

def chat_fn(message, history, character_key):
    config = {
        "configurable": {"thread_id": f"chat-{character_key}"},
        "callbacks": callbacks,
    }
    result = chat_graph.invoke(
        {"messages": [HumanMessage(content=message)], "character_key": character_key},
        config=config,
    )
    return result["messages"][-1].content


# ---------- Режим 2: диалог двух персонажей друг с другом ----------

def dialogue_fn(char_a_key, char_b_key, topic, num_turns):
    if not char_a_key or not char_b_key:
        yield [(None, "⚠️ Выбери обоих персонажей.")]
        return

    thread_id = f"dialogue-{uuid.uuid4()}"
    config = {"configurable": {"thread_id": thread_id}, "callbacks": callbacks}

    initial_state = {
        "messages": [],
        "summary": "",
        "char_a_key": char_a_key,
        "char_b_key": char_b_key,
        "current_speaker": "a",
        "turns_left": int(num_turns),
        "topic": topic or "свободная беседа",
    }

    history = []
    for event in dialogue_graph.stream(initial_state, config=config, stream_mode="values"):
        msgs = event.get("messages", [])
        if not msgs:
            continue
        last = msgs[-1]
        speaker_name = getattr(last, "name", None) or "?"
        history.append((None, f"**{speaker_name}:** {last.content}"))
        yield history


with gr.Blocks(title="LangGraph Character Chat — MVP") as demo:
    gr.Markdown(
        "# 🧩 LangGraph Character Chat — MVP прототип\n"
        "Персонажи задаются `.md`-файлами в папке `characters/`. Долгий диалог "
        "автоматически сжимается в резюме, чтобы не упираться в лимит контекста."
    )

    with gr.Tab("💬 Чат с персонажем"):
        char_dropdown = gr.Dropdown(
            choices=character_choices,
            value=character_choices[0][1] if character_choices else None,
            label="Персонаж",
        )
        gr.ChatInterface(
            fn=chat_fn,
            additional_inputs=[char_dropdown],
        )

    with gr.Tab("🎭 Диалог двух персонажей"):
        with gr.Row():
            char_a = gr.Dropdown(
                choices=character_choices, label="Персонаж A",
                value=character_choices[0][1] if character_choices else None,
            )
            char_b = gr.Dropdown(
                choices=character_choices, label="Персонаж B",
                value=character_choices[-1][1] if len(character_choices) > 1 else None,
            )
        topic_input = gr.Textbox(label="Тема разговора", placeholder="О чём говорят персонажи?")
        turns_input = gr.Slider(minimum=2, maximum=20, value=6, step=1, label="Количество реплик")
        start_btn = gr.Button("Начать диалог", variant="primary")
        dialogue_output = gr.Chatbot(label="Диалог", height=500)

        start_btn.click(
            fn=dialogue_fn,
            inputs=[char_a, char_b, topic_input, turns_input],
            outputs=dialogue_output,
        )

if __name__ == "__main__":
    logger.info("🌐 Запуск сервера Gradio на порту 7860...")
    demo.launch(server_name="0.0.0.0", server_port=7860)
