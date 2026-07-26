from pydantic import BaseModel, Field


class MemoryEvent(BaseModel):

    id: str

    title: str

    summary: str

    participants: list[str] = Field(default_factory=list)

    consequences: list[str] = Field(default_factory=list)

    emotions: list[str] = Field(default_factory=list)