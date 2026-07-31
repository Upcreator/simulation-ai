import os

# "Skills" в терминах проекта — это markdown-описания поведения системы:
# правила симуляции, формат вывода, ограничения. Отдельно от этого храним
# "мир" (сеттинг/атмосферу) — по сути тоже skill-контекст, но с другим
# назначением, поэтому вынесен в отдельный файл для удобства редактирования.

SKILL_PATH = os.path.join("skills", "skill.md")
WORLD_PATH = os.path.join("skills", "world.md")

DEFAULT_SKILL = (
    "Веди диалог от первого лица персонажа. Отвечай только репликой самого "
    "персонажа, без ремарок автора и пояснений от себя, если явно не "
    "попросили иначе. Не выходи из роли ни при каких обстоятельствах."
)


def _load(path: str, default: str = "") -> str:
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def _save(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write((text or "").strip())


def load_skill() -> str:
    return _load(SKILL_PATH, DEFAULT_SKILL)


def save_skill(text: str) -> None:
    _save(SKILL_PATH, text)


def load_world() -> str:
    return _load(WORLD_PATH, "")


def save_world(text: str) -> None:
    _save(WORLD_PATH, text)
