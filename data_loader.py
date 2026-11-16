"""Роль 1 (Маша): завантаження та перевірка даних з CSV."""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def load_all(prefix: str) -> pd.DataFrame:
    """Читає всі файли data/<prefix>_*.csv і об'єднує в одну таблицю."""
    # TODO
    pass


def load_topics() -> pd.DataFrame:
    """Теми з конспектами."""
    # TODO
    pass


def load_questions() -> pd.DataFrame:
    """Питання по конспекту (3 на тему)."""
    # TODO
    pass


def load_scenarios() -> pd.DataFrame:
    """Вузли сценаріїв: один рядок = один варіант відповіді."""
    # TODO
    pass


def check_scenarios(df: pd.DataFrame) -> list[str]:
    """Повертає список помилок у даних (наприклад, next_node, якого не існує)."""
    # TODO
    pass
