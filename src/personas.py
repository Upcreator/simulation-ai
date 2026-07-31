import os
import re
from dataclasses import dataclass
from typing import Dict


@dataclass
class Persona:
    key: str            # id персонажа = имя файла без расширения
    name: str            # отображаемое имя (из заголовка "# Имя")
    system_prompt: str   # полный текст .md, используется как системный промпт


def _extract_name(md_text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", md_text, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback


def load_persona(path: str) -> Persona:
    key = os.path.splitext(os.path.basename(path))[0]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    name = _extract_name(content, fallback=key)
    return Persona(key=key, name=name, system_prompt=content)


def load_all_personas(personas_dir: str = "personas") -> Dict[str, Persona]:
    personas: Dict[str, Persona] = {}
    os.makedirs(personas_dir, exist_ok=True)
    for filename in sorted(os.listdir(personas_dir)):
        if filename.endswith(".md"):
            path = os.path.join(personas_dir, filename)
            p = load_persona(path)
            personas[p.key] = p
    return personas


def sanitize_key(raw: str) -> str:
    """ID персонажа = имя файла, поэтому разрешаем только латиницу/цифры/_/-."""
    key = (raw or "").strip().lower().replace(" ", "_")
    key = re.sub(r"[^a-z0-9_\-]", "", key)
    return key


def save_persona(key: str, content: str, personas_dir: str = "personas") -> str:
    """Создаёт нового персонажа или перезаписывает существующего. Возвращает финальный key."""
    slug = sanitize_key(key)
    if not slug:
        raise ValueError("ID персонажа не может быть пустым после очистки (используй латиницу/цифры).")
    os.makedirs(personas_dir, exist_ok=True)
    path = os.path.join(personas_dir, f"{slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return slug


def delete_persona(key: str, personas_dir: str = "personas") -> bool:
    """Удаляет персонажа. Возвращает True, если файл существовал и был удалён."""
    slug = sanitize_key(key)
    path = os.path.join(personas_dir, f"{slug}.md")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
