from pydantic import BaseModel, Field


class WorldState(BaseModel):

    inflation: float = 0

    key_rate: float = 0

    budget_deficit: float = 0

    gdp_growth: float = 0

    news: list[str] = Field(default_factory=list)