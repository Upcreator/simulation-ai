from dataclasses import dataclass, field


@dataclass
class MemoryEvent:

    id: str

    title: str

    summary: str

    participants: list[str] = field(default_factory=list)

    consequences: list[str] = field(default_factory=list)

    emotions: list[str] = field(default_factory=list)