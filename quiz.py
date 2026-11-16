
"""Логіка квізу: питання, переходи між вузлами, таймер та результати.

Формат сценаріїв: topic_id,node_id,text,option,next_node,result,explain,time_limit.
"""
import pandas as pd

OPTION_KEYS = ("a", "b", "c")


def get_questions(questions: pd.DataFrame, topic_id: str) -> pd.DataFrame:
    """Повертає до трьох питань з обраної теми."""
    return questions.loc[
        questions["topic_id"].astype(str).str.strip() == str(topic_id).strip()
    ].head(3).reset_index(drop=True)


def available_options(row: pd.Series) -> list[str]:
    """Показує лише непорожні варіанти a/b/c."""
    return [
        key for key in OPTION_KEYS
        if pd.notna(row.get(f"option_{key}"))
        and str(row.get(f"option_{key}")).strip()
    ]


def check_question(row: pd.Series, answer_key: str) -> bool:
    """Підтримує правильну відповідь як літеру a/b/c або число 1/2/3."""
    answer = str(answer_key).strip().lower()
    correct = str(row.get("correct_answer", row.get("correct", ""))).strip().lower()
    correct = {"1": "a", "2": "b", "3": "c"}.get(correct, correct)
    return answer in OPTION_KEYS and answer == correct


def start_node(topic_id: str) -> str:
    """Перший вузол сценарію."""
    return f"{str(topic_id).strip()}_1"


def get_node(scenarios: pd.DataFrame, node_id: str) -> pd.DataFrame:
    """Рядки-відповіді для обраного вузла з колонки node_id."""
    if "node_id" not in scenarios.columns:
        raise ValueError("У сценаріях немає колонки node_id")
    options = scenarios.loc[
        scenarios["node_id"].astype(str) == str(node_id)
    ].reset_index(drop=True)
    if options.empty:
        raise ValueError(f"Немає варіантів для сценарію {node_id}")
    return options


def choose(option_row: pd.Series, elapsed: float) -> dict:
    """Оцінка відповіді та часу, перехід до наступного вузла."""
    seconds = max(0.0, float(elapsed))
    limit = pd.to_numeric(option_row.get("time_limit", 15), errors="coerce")
    if pd.isna(limit) or limit <= 0:
        limit = 15.0
    result = str(option_row.get("result", "mistake")).strip().lower()
    if result == "ok" and seconds > float(limit):
        result = "late"
    explain = option_row.get("explain", "")
    if pd.isna(explain):
        explain = ""
    explain = str(explain)
    if result == "late" and not explain:
        explain = f"Правильно, але ви не вклалися в {int(limit)} с."
    return {
        "node_id": option_row["node_id"],
        "result": result,
        "next_node": option_row["next_node"],
        "explain": explain,
        "seconds": round(seconds, 1),
        "time": round(seconds, 1),
    }


def score(steps: list[dict]) -> dict:
    """Кількість кроків, помилок, загальний час, найповільніший крок."""
    if not steps:
        return {"steps": 0, "mistakes": 0, "total_time": 0.0, "slowest": None}
    slowest_index = max(range(len(steps)), key=lambda i: float(steps[i]["seconds"]))
    seconds = float(steps[slowest_index]["seconds"])
    return {
        "steps": len(steps),
        "mistakes": sum(s.get("result") != "ok" for s in steps),
        "total_time": round(sum(float(s["seconds"]) for s in steps), 1),
        "slowest": f"крок {slowest_index + 1} ({seconds:.1f} с)",
    }
