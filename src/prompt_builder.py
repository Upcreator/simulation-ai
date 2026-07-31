from typing import List

from src.skills import load_skill, load_world, load_protagonist
from src.memory import load_history
from src.personas import load_all_personas


def _build_npc_roster() -> str:
    """Собирает карточки всех персонажей из personas/ в единый ростер NPC,
    доступных ведущему для введения в сцену по ходу симуляции."""
    personas = load_all_personas("personas")
    if not personas:
        return ""
    blocks = [p.system_prompt for p in personas.values()]
    return "\n\n---\n\n".join(blocks)


def build_simulation_prompt() -> str:
    """
    Единственная точка сборки системного промпта для симуляции (PromptBuilder
    из документа). Собирает: правила ведущего + протагонист + мир + ростер
    NPC + хроника. Никакой бизнес-логики — только загрузка и конкатенация.
    """
    parts: List[str] = []

    skill = load_skill()
    if skill:
        parts.append("### Правила и роль ведущего симуляции:\n" + skill)

    protagonist = load_protagonist()
    if protagonist:
        parts.append(
            "### Кто такой «ты» в этой симуляции "
            "(протагонист, за которого действует пользователь):\n" + protagonist
        )

    world = load_world()
    if world:
        parts.append("### Мир, в котором происходит действие:\n" + world)

    roster = _build_npc_roster()
    if roster:
        parts.append(
            "### Доступные персонажи (NPC), которых можно вводить в сцену по "
            "необходимости — играй их строго в соответствии с их карточками:\n"
            + roster
        )

    history = load_history()
    if history:
        parts.append("### Хроника симуляции (память о прошлых событиях):\n" + history)

    return "\n\n".join(parts)
