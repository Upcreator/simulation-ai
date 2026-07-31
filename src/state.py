from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """Состояние для чата пользователя с одним персонажем.

    Поля 'summary' больше нет: долгосрочная память живёт снаружи, в
    memory/history.md (см. src/memory.py), а не в состоянии графа."""
    messages: Annotated[List[BaseMessage], add_messages]
    persona_key: str


class DialogueState(TypedDict):
    """Состояние для диалога двух персонажей друг с другом."""
    messages: Annotated[List[BaseMessage], add_messages]
    persona_a_key: str
    persona_b_key: str
    current_speaker: str  # "a" или "b"
    turns_left: int
    topic: str
