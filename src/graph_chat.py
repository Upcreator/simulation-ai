import sqlite3
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.state import ChatState
from src.characters import load_character
from src.memory_utils import summarize_if_needed
from src.world import load_world
from src.config import get_llm, DB_PATH


def _build_system_prompt(character_system_prompt: str, summary: str) -> str:
    parts = []
    world = load_world()
    if world:
        parts.append("### Мир, в котором происходит действие:\n" + world)
    parts.append(character_system_prompt)
    if summary:
        parts.append(
            "\n\n### Память о предыдущих разговорах (сжатое резюме):\n" + summary
        )
    parts.append(
        "\n\nВажно: оставайся в образе персонажа на протяжении всего диалога "
        "и опирайся на резюме выше как на свои собственные воспоминания."
    )
    return "\n".join(parts)


def agent_node(state: ChatState) -> dict:
    character = load_character(f"characters/{state['character_key']}.md")
    system_prompt = _build_system_prompt(character.system_prompt, state.get("summary", ""))
    llm = get_llm()
    response = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    return {"messages": [response]}


def memory_node(state: ChatState) -> dict:
    remove_ops, new_summary = summarize_if_needed(state["messages"], state.get("summary", ""))
    return {"messages": remove_ops, "summary": new_summary}


def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("agent", agent_node)
    graph.add_node("memory", memory_node)

    graph.set_entry_point("agent")
    graph.add_edge("agent", "memory")
    graph.add_edge("memory", END)

    # SqliteSaver даёт персистентность между запусками приложения:
    # история конкретного thread_id (у нас = персонаж) переживает рестарт.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return graph.compile(checkpointer=checkpointer)
