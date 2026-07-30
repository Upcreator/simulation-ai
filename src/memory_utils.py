from typing import List, Tuple
from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage

from src.config import get_llm, MAX_MESSAGES_BEFORE_SUMMARY, KEEP_LAST_MESSAGES, logger


def _messages_to_text(messages: List[BaseMessage]) -> str:
    lines = []
    for m in messages:
        speaker = getattr(m, "name", None) or m.type
        lines.append(f"{speaker}: {m.content}")
    return "\n".join(lines)


def summarize_if_needed(messages: List[BaseMessage], summary: str) -> Tuple[list, str]:
    """
    Ключевой механизм обхода ограничения долгосрочного контекста.

    Если сообщений накопилось больше MAX_MESSAGES_BEFORE_SUMMARY, старые
    сообщения (все, кроме последних KEEP_LAST_MESSAGES) сжимаются моделью
    в текстовое резюме и физически удаляются из состояния графа через
    RemoveMessage (стандартный механизм LangGraph). Резюме сохраняется
    отдельным полем state["summary"] и на каждом шаге подставляется в
    системный промпт — так модель "помнит" всё, что было, не таская за
    собой полный лог диалога.

    Возвращает:
        remove_ops: список RemoveMessage для удаления сжатых сообщений
                    (пустой список, если сжатие не требуется)
        new_summary: обновлённое резюме
    """
    if len(messages) <= MAX_MESSAGES_BEFORE_SUMMARY:
        return [], summary

    to_compress = messages[:-KEEP_LAST_MESSAGES]
    llm = get_llm(temperature=0.2)

    prompt = (
        "Ты — модуль памяти диалоговой системы. Сожми следующий фрагмент "
        "переписки в краткое связное резюме на русском языке. Сохрани все "
        "важные факты, договорённости, имена и эмоционально значимые моменты. "
        "Не добавляй ничего лишнего от себя.\n\n"
        f"Текущее резюме (может быть пустым):\n{summary or '(пусто)'}\n\n"
        f"Новый фрагмент переписки для сжатия:\n{_messages_to_text(to_compress)}\n\n"
        "Выдай ТОЛЬКО обновлённое резюме, без преамбулы и заголовков."
    )

    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        new_summary = result.content.strip()
        logger.info(
            f"🧠 Сжато {len(to_compress)} сообщений в резюме "
            f"(обход ограничения контекста)"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка суммаризации: {e}")
        new_summary = summary

    remove_ops = [RemoveMessage(id=m.id) for m in to_compress]
    return remove_ops, new_summary
