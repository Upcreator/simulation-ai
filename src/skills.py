import os

# "Skills" в терминах проекта — это markdown-описания поведения системы:
# правила симуляции, формат вывода, ограничения. Отдельно от этого храним
# "мир" (сеттинг/атмосферу) — по сути тоже skill-контекст, но с другим
# назначением, поэтому вынесен в отдельный файл для удобства редактирования.

SKILL_PATH = os.path.join("skills", "skill.md")
WORLD_PATH = os.path.join("skills", "world.md")
PROTAGONIST_PATH = os.path.join("skills", "protagonist.md")

DEFAULT_SKILL = (
    "Ты — ведущий (GM) непрерывной ролевой симуляции. Каждый ход пользователь "
    "описывает свои действия, реплики или уточнения/корректировки к прошлому "
    "ходу от лица протагониста («ты» в тексте ниже).\n\n"
    "Порядок действий на каждый ход:\n"
    "1. Если пользователь что-то корректирует — молча прими корректировку как "
    "свершившийся факт, не переспрашивай и не спорь с ним.\n"
    "2. Разверни сцену: кратко опиши обстановку, кто присутствует.\n"
    "3. Веди диалог NPC реалистично, опираясь на их карточки персонажей — "
    "у каждого свои интересы, они не обязаны соглашаться с протагонистом.\n"
    "4. Никогда не пиши реплики или действия от лица самого протагониста — "
    "только описывай мир и NPC в ответ на его действия.\n"
    "5. Заверши ход коротким разделом «Итоги» от лица ведущего симуляции: "
    "отметь закономерности, свяжи с хроникой прошлых событий, обозначь, что "
    "может произойти дальше."
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


def load_protagonist() -> str:
    return _load(PROTAGONIST_PATH, "")


def save_protagonist(text: str) -> None:
    _save(PROTAGONIST_PATH, text)
