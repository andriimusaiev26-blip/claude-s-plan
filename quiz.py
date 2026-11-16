"""Роль 2 (Андрій): логіка квізу — питання по конспекту і сценарій з розгалуженнями."""
import pandas as pd

OPTION_KEYS = ["a", "b", "c"]


def get_questions(questions: pd.DataFrame, topic_id: str) -> pd.DataFrame:
    """Питання по конспекту для обраної теми."""
    # TODO
    pass


def check_question(row: pd.Series, answer_key: str) -> bool:
    """True, якщо обрано правильний варіант (a/b/c)."""
    # TODO
    pass


def start_node(topic_id: str) -> str:
    """Перший вузол сценарію теми, наприклад cpr_1."""
    # TODO
    pass


def get_node(scenarios: pd.DataFrame, node_id: str) -> pd.DataFrame:
    """Усі варіанти відповіді для вузла."""
    # TODO
    pass


def choose(option_row: pd.Series, elapsed: float) -> dict:
    """Обробляє вибір: результат, наступний вузол, пояснення, витрачені секунди."""
    # TODO
    pass


def score(steps: list[dict]) -> dict:
    """Підсумок сценарію: кроки, помилки, загальний час, найповільніший крок."""
    # TODO
    pass
