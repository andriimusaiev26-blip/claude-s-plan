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
    return str(answer_key).strip().lower() == str(row["correct"]).strip().lower()


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
    }    if key not in OPTION_KEYS:
        return False
    return key == str(row["correct_answer"]).strip().lower()


def start_node(topic_id: str) -> str:
    """Перший вузол сценарію, наприклад choking_1."""
    return f"{str(topic_id).strip()}_1"


def get_node(scenarios: pd.DataFrame, node_id: str) -> pd.DataFrame:
    """Повертає три варіанти для вузла (один рядок = варіант)."""
    if "node_id" in scenarios.columns and "option_key" in scenarios.columns:
        return scenarios[scenarios["node_id"].astype(str) == node_id].copy()

    # Підтримка CSV команди: один крок = один рядок із трьома варіантами.
    if "step" not in scenarios.columns:
        raise ValueError("CSV має містити step або node_id та option_key")
    try:
        prefix, number = node_id.rsplit("_", 1)
        step_number = int(number)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Невірний ID вузла: {node_id}") from exc

    matching = scenarios[pd.to_numeric(scenarios["step"], errors="coerce") == step_number]
    if matching.empty:
        return pd.DataFrame()
    row = matching.iloc[0]
    all_steps = pd.to_numeric(scenarios["step"], errors="coerce")
    next_id = f"{prefix}_{step_number + 1}" if (all_steps == step_number + 1).any() else None

    options = []
    for key in OPTION_KEYS:
        option_text = row.get(f"option_{key}")
        if pd.isna(option_text) or str(option_text).strip() == "":
            continue

        correct = check_question(row, key)

        options.append({
            "node_id": node_id,
            "question": row["question"],
            "option_key": key,
            "option_text": option_text,
            "is_correct": correct,
            "critical": _truth(row.get("critical_on_error", False)) and not correct,
            "next_node": next_id,
            "explanation": row.get("explanation", ""),
            "time_limit": row.get("time_limit", 20),
        })

    return pd.DataFrame(options)


def choose(option_row: pd.Series, elapsed: float) -> dict:
    """Оцінює вибір і час; повертає результат для інтерфейсу."""
    elapsed = max(0.0, float(elapsed))
    correct = _truth(option_row.get("is_correct", False))

    limit_value = option_row.get("time_limit", 20)
    limit = float(limit_value) if pd.notna(limit_value) else 20.0

    late = elapsed > limit
    critical = _truth(option_row.get("critical", False)) and not correct
    mistake = not correct or late

    return {
        "node_id": option_row.get("node_id"),
        "result": "critical" if critical else "late" if late else "correct" if correct else "wrong",
        "correct": correct and not late,
        "mistake": mistake,
        "critical": critical,
        "late": late,
        "next_node": option_row.get("next_node"),
        "explanation": option_row.get("explanation", ""),
        "elapsed": round(elapsed, 2),
        "time": round(elapsed, 2),
    }


def score(steps: list[dict]) -> dict:
    """Підсумок: кроки, помилки, час і найповільніший крок."""
    if not steps:
        return {
            "steps": 0,
            "correct": 0,
            "mistakes": 0,
            "critical_mistakes": 0,
            "total_time": 0.0,
            "slowest_step": None,
        }

    slowest_index = max(
        range(len(steps)),
        key=lambda i: float(
            steps[i].get("elapsed", steps[i].get("time", 0))
        )
    )

    return {
        "steps": len(steps),
        "correct": sum(bool(s.get("correct", False)) for s in steps),
        "mistakes": sum(bool(s.get("mistake", False)) for s in steps),
        "critical_mistakes": sum(bool(s.get("critical", False)) for s in steps),
        "total_time": round(
            sum(
                float(s.get("elapsed", s.get("time", 0)))
                for s in steps
            ),
            2
        ),
        "slowest_step": slowest_index + 1,
    }
