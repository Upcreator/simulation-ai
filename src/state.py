from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """Состояние для чата пользователя с одним персонажем."""
    messages: Annotated[List[BaseMessage], add_messages]
    summary: str
    character_key: str


class DialogueState(TypedDict):
    """Состояние для диалога двух персонажей друг с другом."""
    messages: Annotated[List[BaseMessage], add_messages]
    summary: str
    char_a_key: str
    char_b_key: str
    current_speaker: str  # "a" или "b"
    turns_left: int
    topic: str
