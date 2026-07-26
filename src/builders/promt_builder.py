from pathlib import Path

from src.loaders.markdown_loader import MarkdownLoader


class PromptBuilder:

    def __init__(self, project_root: Path):

        self.loader = MarkdownLoader(project_root)

    def build(self) -> str:

        system = self.loader.read(
            "prompts/system.md"
        )

        skill = self.loader.read(
            "prompts/skill.md"
        )

        chairman = self.loader.read(
            "personas/chairman.md"
        )

        return f"""
{system}

=========================

{skill}

=========================

{chairman}
"""