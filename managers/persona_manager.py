from pathlib import Path

from src.core.persona import Persona


class PersonaManager:

    def __init__(self, folder: Path):

        self.folder = folder

    def load(self):

        personas = []

        for file in self.folder.glob("*.md"):

            personas.append(

                Persona(

                    id=file.stem,

                    name=file.stem,

                    role=file.stem

                )

            )

        return personas