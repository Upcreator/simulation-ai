import sqlite3
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.state import ChatState
from src.personas import load_persona
from src.prompt_builder import build_system_prompt
from src.memory import compress_and_append
from src.config import get_llm, DB_PATH


def agent_node(state: ChatState) -> dict:
    persona = load_persona(f"personas/{state['persona_key']}.md")

    system_prompt = build_system_prompt(
        personas=[persona.system_prompt],
        extra_context=(
            "Оставайся полностью в образе персонажа выше на протяжении всего "
            "диалога. Хроника симуляции (если приведена) — это твои "
            "собственные воспоминания, а не чужой пересказ."
        ),
    )

    llm = get_llm()
    response = llm.invoke([SystemMessage(content=system_prompt)] + state["messages"])
    return {"messages": [response]}


def memory_node(state: ChatState) -> dict:
    remove_ops = compress_and_append(
        state["messages"],
        context_label=f"Личный разговор пользователя с персонажем «{state['persona_key']}»",
    )
    return {"messages": remove_ops}


def build_chat_graph():
    graph = StateGraph(ChatState)
    graph.add_node("agent", agent_node)
    graph.add_node("memory", memory_node)

    graph.set_entry_point("agent")
    graph.add_edge("agent", "memory")
    graph.add_edge("memory", END)

    # SqliteSaver хранит только короткий "рабочий" хвост сообщений текущей
    # сессии (per thread_id) — не источник истины для долгосрочной памяти,
    # той самой, что описана в документе. Источник истины — memory/history.md.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return graph.compile(checkpointer=checkpointer)
