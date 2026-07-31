import os
import datetime
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage

from src.config import get_llm, MAX_MESSAGES_BEFORE_SUMMARY, KEEP_LAST_MESSAGES, logger

# Единственная постоянная память всей симуляции — по документу это
# "The simulation has a single persistent memory". Общая для чата с одним
# персонажем и для диалога нескольких — так события в одной сцене становятся
# известны симуляции в целом, а не запираются в отдельном thread_id.
HISTORY_PATH = os.path.join("memory", "history.md")


def load_history() -> str:
    """Загружает всю хронику целиком. MVP намеренно не решает проблему
    бесконечного роста файла (это explicit non-goal по документу) — в
    будущем эта функция может быть заменена на Retriever.search(...) без
    изменения графов, которые её вызывают."""
    if not os.path.exists(HISTORY_PATH):
        return ""
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_history(full_text: str) -> None:
    """Полная перезапись хроники — используется UI-редактором."""
    os.makedirs(os.path.dirname(HISTORY_PATH) or ".", exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        text = (full_text or "").strip()
        f.write(text + ("\n" if text else ""))


def _append(entry: str) -> None:
    os.makedirs(os.path.dirname(HISTORY_PATH) or ".", exist_ok=True)
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + entry.strip() + "\n")


def _messages_to_text(messages: List[BaseMessage]) -> str:
    lines = []
    for m in messages:
        speaker = getattr(m, "name", None) or m.type
        lines.append(f"{speaker}: {m.content}")
    return "\n".join(lines)


def compress_and_append(messages: List[BaseMessage], context_label: str) -> list:
    """
    Механизм обхода ограничения долгосрочного контекста + одновременно
    единственный писатель в постоянную память.

    Если "рабочих" сообщений в состоянии графа накопилось больше
    MAX_MESSAGES_BEFORE_SUMMARY, всё кроме последних KEEP_LAST_MESSAGES
    сжимается моделью в структурированную запись хроники (в духе примера
    из документа: заголовок / участники / суть / последствия) и дописывается
    в конец memory/history.md. Сжатые сообщения удаляются из состояния графа
    через RemoveMessage — LangGraph это распознаёт как физическое удаление,
    а не игнорирование.

    Возвращает список RemoveMessage (пустой, если сжатие не требовалось).
    """
    if len(messages) <= MAX_MESSAGES_BEFORE_SUMMARY:
        return []

    to_compress = messages[:-KEEP_LAST_MESSAGES]
    llm = get_llm(temperature=0.2)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    prompt = (
        "Ты — модуль памяти симуляции. Сожми фрагмент переписки ниже в "
        "структурированную запись хроники на русском языке, строго в формате:\n\n"
        "### <короткий заголовок события>\n"
        "Участники: <имена>\n"
        "Суть: <2-4 предложения о том, что произошло>\n"
        "Последствия: <значимые факты/договорённости, если есть — иначе '—'>\n\n"
        f"Контекст: {context_label}\n"
        f"Время: {timestamp}\n\n"
        f"Переписка для сжатия:\n{_messages_to_text(to_compress)}\n\n"
        "Выдай ТОЛЬКО запись в указанном формате, без преамбулы и пояснений."
    )

    try:
        result = llm.invoke([HumanMessage(content=prompt)])
        entry = result.content.strip()
        _append(entry)
        logger.info(
            f"🧠 Хроника дополнена ({len(to_compress)} сообщений сжато) -> {HISTORY_PATH}"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка записи в хронику: {e}")
        return []

    return [RemoveMessage(id=m.id) for m in to_compress]
