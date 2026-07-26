from pydantic import BaseModel, Field

from src.core.persona import Persona
from src.core.relation import Relation
from src.core.memory import MemoryEvent
from src.core.world import WorldState


class SimulationContext(BaseModel):

    personas: list[Persona] = Field(default_factory=list)

    relations: list[Relation] = Field(default_factory=list)

    memories: list[MemoryEvent] = Field(default_factory=list)

    world: WorldState = Field(default_factory=WorldState)