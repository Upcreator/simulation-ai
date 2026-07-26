from pathlib import Path


class MarkdownLoader:

    def __init__(self, root: Path):
        self.root = root

    def read(self, relative_path: str) -> str:

        file_path = self.root / relative_path

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        return file_path.read_text(
            encoding="utf-8"
        )