import sqlite3
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.state import SimulationState
from src.prompt_builder import build_simulation_prompt
from src.memory import compress_and_append
from src.config import get_llm, DB_PATH


def narrate_node(state: SimulationState) -> dict:
    """Ведущий разворачивает ход: строит промпт из skill+protagonist+world+
    NPC-ростер+хроника и генерирует ответ по ходу пользователя."""
    system_prompt = build_simulation_prompt()
    llm = get_llm()
    response = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    return {"messages": [response]}


def memory_node(state: SimulationState) -> dict:
    remove_ops = compress_and_append(
        state["messages"], context_label="Симуляция (единая сюжетная линия)"
    )
    return {"messages": remove_ops}


def build_simulation_graph():
    graph = StateGraph(SimulationState)
    graph.add_node("narrate", narrate_node)
    graph.add_node("memory", memory_node)

    graph.set_entry_point("narrate")
    graph.add_edge("narrate", "memory")
    graph.add_edge("memory", END)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return graph.compile(checkpointer=checkpointer)
