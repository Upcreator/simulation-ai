import uuid
import gradio as gr
from langchain_core.messages import HumanMessage

from src.personas import (
    load_all_personas,
    load_persona,
    save_persona,
    delete_persona,
)
from src.skills import load_skill, save_skill, load_world, save_world
from src.memory import load_history, save_history
from src.graph_chat import build_chat_graph
from src.graph_dialogue import build_dialogue_graph
from src.config import get_langfuse_handler, logger

NEW_PERSONA_SENTINEL = "__new__"
NEW_PERSONA_TEMPLATE = (
    "# Имя персонажа\n\n"
    "## Роль\n"
    "Кто он(а) в мире и по жизни.\n\n"
    "## Характер\n"
    "- Черта 1\n- Черта 2\n- Черта 3\n\n"
    "## Стиль речи\n"
    "Как персонаж говорит: длина фраз, лексика, привычки.\n\n"
    "## Предыстория\n"
    "Коротко — что важно знать о прошлом персонажа.\n"
)

chat_graph = build_chat_graph()
dialogue_graph = build_dialogue_graph()

langfuse_handler = get_langfuse_handler()
callbacks = [langfuse_handler] if langfuse_handler else []


def get_persona_choices():
    personas = load_all_personas("personas")
    return [(p.name, p.key) for p in personas.values()]


def get_edit_choices():
    return [("➕ Новый персонаж", NEW_PERSONA_SENTINEL)] + get_persona_choices()


# ---------- Режим 1: чат пользователя с одним персонажем ----------

def chat_fn(message, history, persona_key):
    if not persona_key:
        return "⚠️ Сначала выбери персонажа (или создай его во вкладке «Мир и персонажи»)."
    config = {
        "configurable": {"thread_id": f"chat-{persona_key}"},
        "callbacks": callbacks,
    }
    result = chat_graph.invoke(
        {"messages": [HumanMessage(content=message)], "persona_key": persona_key},
        config=config,
    )
    return result["messages"][-1].content


# ---------- Режим 2: диалог двух персонажей друг с другом ----------

def dialogue_fn(persona_a_key, persona_b_key, topic, num_turns):
    if not persona_a_key or not persona_b_key:
        yield [(None, "⚠️ Выбери обоих персонажей.")]
        return

    thread_id = f"dialogue-{uuid.uuid4()}"
    config = {"configurable": {"thread_id": thread_id}, "callbacks": callbacks}

    initial_state = {
        "messages": [],
        "persona_a_key": persona_a_key,
        "persona_b_key": persona_b_key,
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


# ---------- Режим 3: мир, правила, персонажи, хроника ----------

def on_save_skill(text):
    save_skill(text)
    logger.info("📜 Правила симуляции обновлены через веб-интерфейс")
    return "✅ Правила симуляции сохранены."


def on_save_world(text):
    save_world(text)
    logger.info("🌍 Мир обновлён через веб-интерфейс")
    return "✅ Мир сохранён."


def on_load_persona_for_edit(selected_key):
    if not selected_key or selected_key == NEW_PERSONA_SENTINEL:
        return "", NEW_PERSONA_TEMPLATE
    persona = load_persona(f"personas/{selected_key}.md")
    return persona.key, persona.system_prompt


def on_save_persona(key_input, content_input):
    empty = gr.update()
    if not (key_input or "").strip():
        return "⚠️ Укажи ID персонажа (латиница, без пробелов).", empty, empty, empty, empty
    if not (content_input or "").strip():
        return "⚠️ Карточка персонажа не может быть пустой.", empty, empty, empty, empty
    try:
        slug = save_persona(key_input, content_input)
    except ValueError as e:
        return f"⚠️ {e}", empty, empty, empty, empty

    logger.info(f"🎭 Персонаж «{slug}» сохранён через веб-интерфейс")
    choices = get_persona_choices()
    edit_choices = get_edit_choices()
    status = f"✅ Персонаж «{slug}» сохранён."
    return (
        status,
        gr.update(choices=choices),
        gr.update(choices=choices),
        gr.update(choices=choices),
        gr.update(choices=edit_choices, value=slug),
    )


def on_delete_persona(key_input):
    empty = gr.update()
    if not (key_input or "").strip():
        return "⚠️ Нечего удалять — сначала выбери или загрузи персонажа.", empty, empty, empty, empty

    ok = delete_persona(key_input)
    choices = get_persona_choices()
    edit_choices = get_edit_choices()
    status = f"🗑️ Персонаж «{key_input}» удалён." if ok else f"⚠️ Персонаж «{key_input}» не найден."
    if ok:
        logger.info(f"🗑️ Персонаж «{key_input}» удалён через веб-интерфейс")
    return (
        status,
        gr.update(choices=choices),
        gr.update(choices=choices),
        gr.update(choices=choices),
        gr.update(choices=edit_choices, value=NEW_PERSONA_SENTINEL),
    )


def on_save_history(text):
    save_history(text)
    logger.info("📖 Хроника симуляции отредактирована вручную")
    return "✅ Хроника обновлена."


def on_clear_history():
    save_history("")
    logger.info("🧹 Хроника симуляции очищена вручную")
    return "🧹 Хроника очищена.", ""


def on_reload_history():
    return load_history()


with gr.Blocks(title="LangGraph Character Chat — MVP") as demo:
    gr.Markdown(
        "# 🧩 LangGraph Character Chat — MVP симуляция\n"
        "LLM не хранит ничего между запросами — весь долгосрочный контекст "
        "(персонажи, правила, мир, хроника) лежит в markdown-файлах и "
        "пересобирается заново на каждый запрос. Всё редактируется во "
        "вкладке «🌍 Мир и персонажи»."
    )

    initial_choices = get_persona_choices()

    with gr.Tab("💬 Чат с персонажем"):
        persona_dropdown = gr.Dropdown(
            choices=initial_choices,
            value=initial_choices[0][1] if initial_choices else None,
            label="Персонаж",
        )
        gr.ChatInterface(
            fn=chat_fn,
            additional_inputs=[persona_dropdown],
        )

    with gr.Tab("🎭 Диалог двух персонажей"):
        with gr.Row():
            persona_a = gr.Dropdown(
                choices=initial_choices, label="Персонаж A",
                value=initial_choices[0][1] if initial_choices else None,
            )
            persona_b = gr.Dropdown(
                choices=initial_choices, label="Персонаж B",
                value=initial_choices[-1][1] if len(initial_choices) > 1 else None,
            )
        topic_input = gr.Textbox(label="Тема разговора", placeholder="О чём говорят персонажи?")
        turns_input = gr.Slider(minimum=2, maximum=20, value=6, step=1, label="Количество реплик")
        start_btn = gr.Button("Начать диалог", variant="primary")
        dialogue_output = gr.Chatbot(label="Диалог", height=500)

        start_btn.click(
            fn=dialogue_fn,
            inputs=[persona_a, persona_b, topic_input, turns_input],
            outputs=dialogue_output,
        )

    with gr.Tab("🌍 Мир и персонажи"):
        gr.Markdown("## Правила симуляции")
        gr.Markdown("Общее поведение системы: как отвечать, формат, ограничения.")
        skill_box = gr.Textbox(label="skills/skill.md", lines=6, value=load_skill())
        skill_save_btn = gr.Button("💾 Сохранить правила")
        skill_status = gr.Markdown()
        skill_save_btn.click(fn=on_save_skill, inputs=[skill_box], outputs=[skill_status])

        gr.Markdown("---\n## Мир")
        gr.Markdown("Сеттинг, эпоха, атмосфера — общий фон для всех персонажей.")
        world_box = gr.Textbox(
            label="skills/world.md", lines=8, value=load_world(),
            placeholder="Например: тёмное фэнтези, XV век, магия под запретом...",
        )
        world_save_btn = gr.Button("💾 Сохранить мир")
        world_status = gr.Markdown()
        world_save_btn.click(fn=on_save_world, inputs=[world_box], outputs=[world_status])

        gr.Markdown("---\n## Персонажи")
        with gr.Row():
            edit_persona_dropdown = gr.Dropdown(
                choices=get_edit_choices(),
                value=NEW_PERSONA_SENTINEL,
                label="Выбери персонажа для редактирования",
                scale=3,
            )
            load_persona_btn = gr.Button("📂 Загрузить", scale=1)

        persona_key_input = gr.Textbox(
            label="ID персонажа (латиница/цифры/_/-, без пробелов — используется как имя файла)",
            placeholder="elf_warrior",
        )
        persona_content_input = gr.Textbox(
            label="Карточка персонажа (markdown, «# Имя» в первой строке — отображаемое имя)",
            lines=16,
            value=NEW_PERSONA_TEMPLATE,
        )
        with gr.Row():
            save_persona_btn = gr.Button("💾 Сохранить персонажа", variant="primary")
            delete_persona_btn = gr.Button("🗑️ Удалить персонажа", variant="stop")
        persona_status = gr.Markdown()

        load_persona_btn.click(
            fn=on_load_persona_for_edit,
            inputs=[edit_persona_dropdown],
            outputs=[persona_key_input, persona_content_input],
        )
        save_persona_btn.click(
            fn=on_save_persona,
            inputs=[persona_key_input, persona_content_input],
            outputs=[persona_status, persona_dropdown, persona_a, persona_b, edit_persona_dropdown],
        )
        delete_persona_btn.click(
            fn=on_delete_persona,
            inputs=[persona_key_input],
            outputs=[persona_status, persona_dropdown, persona_a, persona_b, edit_persona_dropdown],
        )

        gr.Markdown("---\n## Хроника симуляции (общая память)")
        gr.Markdown(
            "Единая история событий, доступная всем персонажам и во всех "
            "режимах — заполняется автоматически по мере разговоров "
            "(старые реплики сжимаются в записи хроники), но можно "
            "редактировать вручную — например, вписать стартовые события."
        )
        history_box = gr.Textbox(label="memory/history.md", lines=12, value=load_history())
        with gr.Row():
            history_reload_btn = gr.Button("🔄 Обновить из файла")
            history_save_btn = gr.Button("💾 Сохранить")
            history_clear_btn = gr.Button("🧹 Очистить", variant="stop")
        history_status = gr.Markdown()

        history_reload_btn.click(fn=on_reload_history, outputs=[history_box])
        history_save_btn.click(fn=on_save_history, inputs=[history_box], outputs=[history_status])
        history_clear_btn.click(fn=on_clear_history, outputs=[history_status, history_box])

if __name__ == "__main__":
    logger.info("🌐 Запуск сервера Gradio на порту 7860...")
    demo.launch(server_name="0.0.0.0", server_port=7860)
