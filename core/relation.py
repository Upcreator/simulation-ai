from dataclasses import dataclass


@dataclass
class Relation:

    source: str

    target: str

    trust: int = 50

    respect: int = 50

    fear: int = 0

    alliance: bool = False