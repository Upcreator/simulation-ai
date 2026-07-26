from dataclasses import dataclass, field


@dataclass
class Persona:

    id: str

    name: str

    role: str

    goals: list[str] = field(default_factory=list)

    fears: list[str] = field(default_factory=list)

    principles: list[str] = field(default_factory=list)

    communication_style: str = ""

    current_emotion: str = "neutral"

    notes: list[str] = field(default_factory=list)