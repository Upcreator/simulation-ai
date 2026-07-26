from dataclasses import dataclass, field

from src.core.persona import Persona
from src.core.world import WorldState
from src.core.memory import MemoryEvent
from src.core.relation import Relation


@dataclass
class SimulationContext:

    personas: list[Persona] = field(default_factory=list)

    memories: list[MemoryEvent] = field(default_factory=list)

    relations: list[Relation] = field(default_factory=list)

    world: WorldState | None = None