"""Роль 1 (Маша): завантаження та перевірка даних з CSV."""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"

END_NODES = {"END_OK", "END_FAIL"}
RESULTS = {"ok", "mistake", "fatal"}
TOPIC_COLUMNS = ["topic_id", "title", "summary", "source"]
QUESTION_COLUMNS = ["topic_id", "question", "option_a", "option_b",
                    "option_c", "correct", "explain"]
SCENARIO_COLUMNS = ["topic_id", "node_id", "text", "option", "next_node",
                    "result", "explain", "time_limit"]


def load_all(prefix: str, columns: list[str] | None = None) -> pd.DataFrame:
    """Читає всі файли data/<prefix>_*.csv і об'єднує в одну таблицю."""
    files = sorted(DATA_DIR.glob(f"{prefix}_*.csv"))
    if not files:
        return pd.DataFrame(columns=columns or [])
    frames = [pd.read_csv(path, dtype=str).fillna("") for path in files]
    return pd.concat(frames, ignore_index=True)


def load_topics() -> pd.DataFrame:
    """Теми з конспектами."""
    return load_all("topics", TOPIC_COLUMNS)


def load_questions() -> pd.DataFrame:
    """Питання по конспекту (3 на тему)."""
    return load_all("questions", QUESTION_COLUMNS)


def load_scenarios() -> pd.DataFrame:
    """Вузли сценаріїв: один рядок = один варіант відповіді."""
    df = load_all("scenarios", SCENARIO_COLUMNS)
    if "time_limit" in df.columns:
        df["time_limit"] = pd.to_numeric(df["time_limit"], errors="coerce")
    return df


def get_node_options(scenarios: pd.DataFrame, node_id: str) -> pd.DataFrame:
    """Варіанти відповіді для одного кроку сценарію."""
    return scenarios[scenarios["node_id"] == node_id]


def check_scenarios(df: pd.DataFrame) -> list[str]:
    """Повертає список помилок у даних (наприклад, next_node, якого не існує)."""
    if df.empty:
        return ["Сценарії не знайдено"]
    missing = [col for col in SCENARIO_COLUMNS if col not in df.columns]
    if missing:
        return [f"У сценаріях немає стовпців: {', '.join(missing)}"]

    errors = []
    nodes = set(df["node_id"])
    for topic_id in df["topic_id"].unique():
        if f"{topic_id}_1" not in nodes:
            errors.append(f"{topic_id}: немає першого кроку {topic_id}_1")
    for _, row in df.iterrows():
        node = row["node_id"]
        if row["next_node"] not in nodes | END_NODES:
            errors.append(f"{node}: невідомий next_node '{row['next_node']}'")
        if row["result"] not in RESULTS:
            errors.append(f"{node}: result має бути ok, mistake або fatal")
        if pd.isna(row["time_limit"]) or row["time_limit"] <= 0:
            errors.append(f"{node}: time_limit має бути числом більше 0")
    return errors


def check_questions(df: pd.DataFrame) -> list[str]:
    """Перевіряє питання: по 3 на тему, correct = a, b або c."""
    if df.empty:
        return ["Питання не знайдено"]
    missing = [col for col in QUESTION_COLUMNS if col not in df.columns]
    if missing:
        return [f"У питаннях немає стовпців: {', '.join(missing)}"]

    errors = []
    for topic_id, group in df.groupby("topic_id"):
        if len(group) != 3:
            errors.append(f"{topic_id}: має бути 3 питання, є {len(group)}")
    bad = df[~df["correct"].str.lower().isin(["a", "b", "c"])]
    for _, row in bad.iterrows():
        errors.append(f"{row['topic_id']}: correct має бути a, b або c")
    return errors


def check_topics(df: pd.DataFrame, scenarios: pd.DataFrame) -> list[str]:
    """Перевіряє теми: є конспект і джерело, у кожного сценарію є тема."""
    if df.empty:
        return ["Теми не знайдено"]
    missing = [col for col in TOPIC_COLUMNS if col not in df.columns]
    if missing:
        return [f"У темах немає стовпців: {', '.join(missing)}"]

    errors = []
    for _, row in df.iterrows():
        if not row["summary"].strip():
            errors.append(f"{row['topic_id']}: порожній конспект summary")
        if not row["source"].strip():
            errors.append(f"{row['topic_id']}: порожнє джерело source")
    for topic_id in set(scenarios["topic_id"]) - set(df["topic_id"]):
        errors.append(f"{topic_id}: є сценарій, але немає теми в topics_*.csv")
    return errors


def check_files() -> list[str]:
    """Знаходить файли в data/, які програма не читає через неправильну назву."""
    if not DATA_DIR.exists():
        return [f"Папку data не знайдено: {DATA_DIR}"]
    prefixes = ("topics_", "questions_", "scenarios_")
    errors = []
    for path in sorted(DATA_DIR.iterdir()):
        if not (path.name.startswith(prefixes) and path.name.endswith(".csv")):
            errors.append(f"{path.name}: файл не читається, назва має бути "
                          "topics_/questions_/scenarios_<тема>.csv")
    return errors


def check_all() -> list[str]:
    """Перевіряє всі дані одразу."""
    scenarios = load_scenarios()
    return (check_files()
            + check_topics(load_topics(), scenarios)
            + check_scenarios(scenarios)
            + check_questions(load_questions()))


if __name__ == "__main__":
    problems = check_all()
    print("Усе гаразд" if not problems else "\n".join(problems))
