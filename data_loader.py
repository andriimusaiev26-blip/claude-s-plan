"""Роль 1 (Маша): завантаження та перевірка даних з CSV.

Джерела даних у папці data/:
- protocol.csv — основний набір: 5 сценаріїв за протоколами МОЗ
  (scenario_name, step_number, action_text, is_correct, explanation);
- choking.csv — сценарій «Людина вдавилася» у форматі «один крок = один рядок»;
- topics_*.csv, questions_*.csv, scenarios_*.csv — теми, заповнені вручну.

Усі джерела перетворюються на три однакові таблиці: теми, питання, сценарії.
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
PROTOCOL_FILE = DATA_DIR / "protocol.csv"
PROTOCOL_SOURCE = "Наказ МОЗ №441 від 09.03.2022"
DEFAULT_TIME_LIMIT = 15


END_NODES = {"END_OK", "END_FAIL"}
RESULTS = {"ok", "mistake", "fatal"}
TOPIC_COLUMNS = ["topic_id", "title", "summary", "source"]
QUESTION_COLUMNS = ["topic_id", "question", "option_a", "option_b",
                    "option_c", "correct", "explain"]
SCENARIO_COLUMNS = ["topic_id", "node_id", "text", "option", "next_node",
                    "result", "explain", "time_limit"]


# Короткі коди для сценаріїв із protocol.csv
PROTOCOL_TOPIC_IDS = {
    "Зупинка кровообігу у дорослих": "arrest",
    "Масивна зовнішня кровотеча": "bleeding",
    "Опіки": "burn",
    "Травма голови": "head",
    "Шок": "shock",
}

# Сценарії у форматі «один крок = один рядок»: код теми -> назва
WIDE_TOPICS = {
    "choking": "Людина вдавилася",
}


def load_all(prefix: str, columns: list[str] | None = None) -> pd.DataFrame:
    """Читає всі файли data/<prefix>_*.csv і об'єднує в одну таблицю."""
    files = sorted(DATA_DIR.glob(f"{prefix}_*.csv"))
    if not files:
        return pd.DataFrame(columns=columns or [])
    frames = [pd.read_csv(path, dtype=str).fillna("") for path in files]
    return pd.concat(frames, ignore_index=True)


def _questions_from_steps(topic_id: str, steps: list[dict]) -> list[dict]:
    """Робить 3 питання з кроків, де 2–3 варіанти відповіді."""
    candidates = [s for s in steps if 2 <= len(s["options"]) <= 3]
    if len(candidates) < 3:
        return []
    picked = [candidates[1 if len(candidates) > 3 else 0],
              candidates[len(candidates) // 2],
              candidates[-1]]
    questions = []
    for step in picked:
        options = step["options"]
        # Зсуваємо варіанти, щоб правильний не був завжди першим
        shift = step["number"] % len(options)
        options = options[shift:] + options[:shift]
        row = {"topic_id": topic_id, "question": step["question"],
               "option_a": "", "option_b": "", "option_c": "", "correct": "", "explain": ""}
        for key, (text, correct, explain) in zip("abc", options):
            row[f"option_{key}"] = text
            if correct:
                row["correct"] = key
                row["explain"] = explain
        questions.append(row)
    return questions


def protocol_to_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Перетворює protocol.csv на таблиці тем, питань і сценаріїв."""
    topics, questions, scenarios = [], [], []
    for i, (title, group) in enumerate(df.groupby("scenario_name", sort=False)):
        topic_id = PROTOCOL_TOPIC_IDS.get(title, f"topic{i}")
        group = group.sort_values("step_number")
        numbers = sorted(group["step_number"].unique())
        last = numbers[-1]

        correct_actions = group[group["is_correct"] == 1]["action_text"].tolist()
        summary = " ".join(f"{n}. {text}." for n, text in enumerate(correct_actions, 1))
        topics.append({"topic_id": topic_id, "title": title,
                       "summary": summary, "source": PROTOCOL_SOURCE})

        steps = []
        for position, number in enumerate(numbers, 1):
            node_id = f"{topic_id}_{position}"
            next_ok = f"{topic_id}_{position + 1}" if number != last else "END_OK"
            text = f"«{title}». Крок {position} з {len(numbers)}. Що робите?"
            options = []
            for _, act in group[group["step_number"] == number].iterrows():
                is_ok = int(act["is_correct"]) == 1
                options.append((act["action_text"], is_ok, act["explanation"]))
                scenarios.append({
                    "topic_id": topic_id, "node_id": node_id, "text": text,
                    "option": act["action_text"],
                    # Помилка: залишаємось на тому ж кроці й пробуємо ще раз
                    "next_node": next_ok if is_ok else node_id,
                    "result": "ok" if is_ok else "mistake",
                    "explain": "" if is_ok else act["explanation"],
                    "time_limit": DEFAULT_TIME_LIMIT,
                })
            steps.append({"number": position, "options": options,
                          "question": f"«{title}», крок {position}: яка дія правильна?"})
        questions += _questions_from_steps(topic_id, steps)
    return pd.DataFrame(topics), pd.DataFrame(questions), pd.DataFrame(scenarios)


def wide_to_tables(df: pd.DataFrame, topic_id: str, title: str):
    """Перетворює сценарій «один крок = один рядок» (step, question, option_a/b/c,
    correct_answer, time_limit, critical_on_error, explanation) на три таблиці."""
    df = df.sort_values("step")
    last = df["step"].max()
    scenarios, questions = [], []
    for _, row in df.iterrows():
        node_id = f"{topic_id}_{int(row['step'])}"
        next_ok = "END_OK" if row["step"] == last else f"{topic_id}_{int(row['step']) + 1}"
        correct_key = str(row["correct_answer"]).strip().lower()
        critical = str(row.get("critical_on_error", "")).strip().lower() in ("true", "1", "так")
        for key in "abc":
            option = str(row.get(f"option_{key}", "")).strip()
            if not option or option == "nan":
                continue
            is_ok = key == correct_key
            scenarios.append({
                "topic_id": topic_id, "node_id": node_id, "text": row["question"],
                "option": option,
                "next_node": next_ok if is_ok else ("END_FAIL" if critical else node_id),
                "result": "ok" if is_ok else ("fatal" if critical else "mistake"),
                "explain": "" if is_ok else row["explanation"],
                "time_limit": row.get("time_limit", DEFAULT_TIME_LIMIT),
            })
        questions.append({"topic_id": topic_id, "question": row["question"],
                          "option_a": row["option_a"], "option_b": row["option_b"],
                          "option_c": row["option_c"], "correct": correct_key,
                          "explain": row["explanation"]})
    summary = " ".join(f"{i}. {text}" for i, text in enumerate(df["explanation"], 1))
    topics = [{"topic_id": topic_id, "title": title, "summary": summary,
               "source": PROTOCOL_SOURCE}]
    return pd.DataFrame(topics), pd.DataFrame(questions[:3]), pd.DataFrame(scenarios)


@lru_cache(maxsize=1)
def _generated_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Таблиці, зібрані з protocol.csv і choking.csv (рахуються один раз)."""
    parts = []
    if PROTOCOL_FILE.exists():
        parts.append(protocol_to_tables(pd.read_csv(PROTOCOL_FILE)))
    for topic_id, title in WIDE_TOPICS.items():
        for path in DATA_DIR.glob(f"{topic_id}.csv*"):
            parts.append(wide_to_tables(pd.read_csv(path), topic_id, title))
            break
    if not parts:
        empty = pd.DataFrame()
        return empty, empty, empty
    return tuple(pd.concat([p[i] for p in parts], ignore_index=True).astype(str)
                 for i in range(3))


def load_topics() -> pd.DataFrame:
    """Теми з конспектами (лише ті, для яких є сценарій)."""
    topics = pd.concat([load_all("topics", TOPIC_COLUMNS), _generated_tables()[0]],
                       ignore_index=True)
    with_scenarios = set(load_scenarios()["topic_id"])
    return topics[topics["topic_id"].isin(with_scenarios)].reset_index(drop=True)


def load_questions() -> pd.DataFrame:
    """Питання по конспекту (3 на тему)."""
    return pd.concat([load_all("questions", QUESTION_COLUMNS), _generated_tables()[1]],
                     ignore_index=True)


def load_scenarios() -> pd.DataFrame:
    """Вузли сценаріїв: один рядок = один варіант відповіді."""
    df = pd.concat([load_all("scenarios", SCENARIO_COLUMNS), _generated_tables()[2]],
                   ignore_index=True)
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
    # Файли, які програма читає окремо (protocol.csv, choking.csv, дані AED)
    known = {PROTOCOL_FILE.name, "aed_kyiv.csv"} | {f"{t}.csv" for t in WIDE_TOPICS}
    errors = []
    for path in sorted(DATA_DIR.iterdir()):
        if path.name.rstrip(".") in known:
            continue
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
    print("Теми:", ", ".join(load_topics()["title"]))
    problems = check_all()
    print("Усе гаразд" if not problems else "\n".join(problems))
