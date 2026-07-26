from dataclasses import dataclass


@dataclass
class WorldState:

    inflation: float = 0.0

    key_rate: float = 0.0

    budget_deficit: float = 0.0

    gdp_growth: float = 0.0

    news: list[str] = None

    def __post_init__(self):

        if self.news is None:
            self.news = []