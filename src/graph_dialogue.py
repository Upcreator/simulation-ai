import sqlite3
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.state import DialogueState
from src.personas import load_persona
from src.prompt_builder import build_system_prompt
from src.memory import compress_and_append
from src.config import get_llm, DB_PATH


def _speaker_key(state: DialogueState) -> str:
    return state["persona_a_key"] if state["current_speaker"] == "a" else state["persona_b_key"]


def _partner_key(state: DialogueState) -> str:
    return state["persona_b_key"] if state["current_speaker"] == "a" else state["persona_a_key"]


def speak_node(state: DialogueState) -> dict:
    speaker = load_persona(f"personas/{_speaker_key(state)}.md")
    partner = load_persona(f"personas/{_partner_key(state)}.md")

    extra_context = (
        f"Ты играешь роль персонажа «{speaker.name}» (первая карточка ниже). "
        f"«{partner.name}» — твой собеседник в этой сцене, его карточка "
        f"приведена только для контекста — не отвечай и не говори за него.\n"
        f"Тема разговора: {state['topic']}.\n"
        "Отвечай только своей репликой, без указания своего имени в начале, "
        "кратко и живо, как в настоящем диалоге. Не повторяй уже сказанное."
    )

    system_prompt = build_system_prompt(
        personas=[speaker.system_prompt, partner.system_prompt],
        extra_context=extra_context,
    )

    llm = get_llm()
    response = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    response.name = speaker.name  # помечаем, кто именно сказал реплику

    next_speaker = "b" if state["current_speaker"] == "a" else "a"

    return {
        "messages": [response],
        "current_speaker": next_speaker,
        "turns_left": state["turns_left"] - 1,
    }


def memory_node(state: DialogueState) -> dict:
    label = (
        f"Диалог персонажей «{state['persona_a_key']}» и «{state['persona_b_key']}» "
        f"на тему «{state['topic']}»"
    )
    remove_ops = compress_and_append(state["messages"], context_label=label)
    return {"messages": remove_ops}


def _route_after_memory(state: DialogueState):
    return "speak" if state["turns_left"] > 0 else END


def build_dialogue_graph():
    graph = StateGraph(DialogueState)
    graph.add_node("speak", speak_node)
    graph.add_node("memory", memory_node)

    graph.set_entry_point("speak")
    graph.add_edge("speak", "memory")
    graph.add_conditional_edges("memory", _route_after_memory, {"speak": "speak", END: END})

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return graph.compile(checkpointer=checkpointer)
