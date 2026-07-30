import sqlite3
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.state import DialogueState
from src.characters import load_character
from src.memory_utils import summarize_if_needed
from src.config import get_llm, DB_PATH


def _speaker_key(state: DialogueState) -> str:
    return state["char_a_key"] if state["current_speaker"] == "a" else state["char_b_key"]


def _partner_key(state: DialogueState) -> str:
    return state["char_b_key"] if state["current_speaker"] == "a" else state["char_a_key"]


def speak_node(state: DialogueState) -> dict:
    speaker = load_character(f"characters/{_speaker_key(state)}.md")
    partner = load_character(f"characters/{_partner_key(state)}.md")

    system_prompt = (
        f"{speaker.system_prompt}\n\n"
        f"Ты сейчас разговариваешь с персонажем по имени {partner.name}. "
        f"Тема разговора: {state['topic']}.\n"
    )
    if state.get("summary"):
        system_prompt += f"\nРанее в разговоре произошло (резюме):\n{state['summary']}\n"
    system_prompt += (
        "\nОтвечай только своей репликой, без указания своего имени в начале, "
        "кратко и живо, как в настоящем диалоге. Не повторяй то, что уже сказано."
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
    remove_ops, new_summary = summarize_if_needed(state["messages"], state.get("summary", ""))
    return {"messages": remove_ops, "summary": new_summary}


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
