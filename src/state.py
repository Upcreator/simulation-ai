from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class SimulationState(TypedDict):
    """Состояние единой непрерывной симуляции. Персонажи (NPC) не привязаны
    к state — они загружаются PromptBuilder'ом из personas/ на каждый ход."""
    messages: Annotated[List[BaseMessage], add_messages]
