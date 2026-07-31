import os

# Мир храним в data/, так как эта папка уже монтируется как volume в Docker —
# описание мира переживёт пересоздание контейнера так же, как sqlite-чекпоинты.
WORLD_PATH = os.path.join("data", "world.md")


def load_world() -> str:
    """Возвращает текущее описание мира или пустую строку, если оно не задано."""
    if not os.path.exists(WORLD_PATH):
        return ""
    with open(WORLD_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_world(text: str) -> None:
    """Сохраняет описание мира на диск."""
    os.makedirs(os.path.dirname(WORLD_PATH) or ".", exist_ok=True)
    with open(WORLD_PATH, "w", encoding="utf-8") as f:
        f.write((text or "").strip())
