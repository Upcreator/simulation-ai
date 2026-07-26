from pydantic import BaseModel, Field


class Persona(BaseModel):

    id: str

    name: str

    role: str

    description: str = ""

    goals: list[str] = Field(default_factory=list)

    fears: list[str] = Field(default_factory=list)

    principles: list[str] = Field(default_factory=list)

    communication_style: str = ""

    current_emotion: str = "neutral"

    notes: list[str] = Field(default_factory=list)