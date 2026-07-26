from src.core.context import SimulationContext


class SimulationEngine:

    def __init__(self):

        self.context = SimulationContext()

    def build_context(self):

        return self.context

    def run(self):

        return self.build_context()