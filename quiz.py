"""Роль 2 (Андрій): логіка квізу та навчального сценарію.

Формат сценарію: один рядок = один варіант відповіді
(topic_id, node_id, text, option, next_node, result, explain, time_limit).
Тут немає медичних рішень: правильні відповіді беруться з CSV.
"""
import pandas as pd

OPTION_KEYS = ["a", "b", "c"]


def get_questions(questions: pd.DataFrame, topic_id: str) -> pd.DataFrame:
    """Повертає питання обраної теми (три)."""
    result = questions[questions["topic_id"].astype(str) == str(topic_id)]
    return result.head(3).reset_index(drop=True)


def available_options(row: pd.Series) -> list[str]:
    """Ключі a/b/c, для яких у питанні є текст варіанта."""
    return [key for key in OPTION_KEYS if str(row.get(f"option_{key}", "")).strip()]


def check_question(row: pd.Series, answer_key: str) -> bool:
    """Перевіряє відповідь a/b/c."""
    return key == str(row["correct_answer"]).strip().lower()


def start_node(topic_id: str) -> str:
    """Перший вузол сценарію, наприклад choking_1."""
    return f"{str(topic_id).strip()}_1"


def get_node(scenarios: pd.DataFrame, node_id: str) -> pd.DataFrame:
    """Усі варіанти відповіді для вузла."""
    return scenarios[scenarios["node_id"] == node_id].reset_index(drop=True)


def choose(option_row: pd.Series, elapsed: float) -> dict:
    """Оцінює вибір і час. Правильна відповідь із запізненням — це «late»."""
    elapsed = max(0.0, float(elapsed))
    limit = option_row["time_limit"]
    limit = float(limit) if pd.notna(limit) else 15.0
    too_late = elapsed > limit

    result = option_row["result"]
    if too_late and result == "ok":
        result = "late"

    explain = option_row["explain"]
    if not explain and too_late:
        explain = f"Правильно, але ви не вклалися в {int(limit)} с."
    return {
        "node_id": option_row["node_id"],
        "result": result,
        "next_node": option_row["next_node"],
        "explain": explain,
        "seconds": round(elapsed, 1),
        "time": round(elapsed, 1),  # цей ключ використовує charts.py
    }


def score(steps: list[dict]) -> dict:
    """Підсумок: кроки, помилки, загальний час і найповільніший крок."""
    if not steps:
        return {"steps": 0, "mistakes": 0, "total_time": 0.0, "slowest": None}
    log = pd.DataFrame(steps)
    slowest = int(log["seconds"].idxmax())
    return {
        "steps": len(log),
        "mistakes": int((log["result"] != "ok").sum()),
        "total_time": float(round(log["seconds"].sum(), 1)),
        "slowest": f"крок {slowest + 1} ({log.loc[slowest, 'seconds']} с)",
    }
