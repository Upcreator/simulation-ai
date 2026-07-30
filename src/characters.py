import os
import re
from dataclasses import dataclass
from typing import Dict


@dataclass
class Character:
    key: str            # id персонажа = имя файла без расширения
    name: str            # отображаемое имя (из заголовка "# Имя")
    system_prompt: str   # полный текст .md, используется как системный промпт


def _extract_name(md_text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", md_text, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback


def load_character(path: str) -> Character:
    key = os.path.splitext(os.path.basename(path))[0]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    name = _extract_name(content, fallback=key)
    return Character(key=key, name=name, system_prompt=content)


def load_all_characters(characters_dir: str = "characters") -> Dict[str, Character]:
    characters: Dict[str, Character] = {}
    for filename in sorted(os.listdir(characters_dir)):
        if filename.endswith(".md"):
            path = os.path.join(characters_dir, filename)
            char = load_character(path)
            characters[char.key] = char
    return characters
