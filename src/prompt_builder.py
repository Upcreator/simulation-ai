from typing import List

from src.skills import load_skill, load_world
from src.memory import load_history


def build_system_prompt(personas: List[str], extra_context: str = "") -> str:
    """
    PromptBuilder: единственная ответственность — собрать полный системный
    промпт из внешних markdown-источников. Никакой бизнес-логики здесь нет —
    только загрузка и конкатенация.

    personas: тексты карточек персонажей (system_prompt каждого), в порядке
              "сначала тот, за кого говорим, потом контекстные").
    extra_context: разовая инструкция для конкретного узла графа (например,
                    тема диалога или напоминание оставаться в роли) —
                    формально не относится к скиллам/персонам/памяти, но
                    удобно прокинуть в этом же вызове.
    """
    parts: List[str] = []

    skill = load_skill()
    if skill:
        parts.append("### Правила симуляции:\n" + skill)

    world = load_world()
    if world:
        parts.append("### Мир, в котором происходит действие:\n" + world)

    history = load_history()
    if history:
        parts.append("### Хроника симуляции (память о прошлых событиях):\n" + history)

    parts.extend(personas)

    if extra_context:
        parts.append(extra_context)

    return "\n\n".join(parts)
