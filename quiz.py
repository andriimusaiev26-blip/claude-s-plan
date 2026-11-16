65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
    next_id = f"{prefix}_{step_number + 1}" if (all_steps == step_number + 1).any() else None

    options = []
    for key in OPTION_KEYS:
        text = row.get(f"option_{key}")
        if pd.isna(text) or str(text).strip() == "":
            continue
        correct = check_question(row, key)
        options.append({
            "node_id": node_id,
            "question": row["question"],
            "option_key": key,
            "option_text": text,
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
        "time": round(elapsed, 2),  # Зручно для charts.py
    }


def score(steps: list[dict]) -> dict:
    """Підсумок: кроки, помилки, час і найповільніший крок."""
    if not steps:
        return {"steps": 0, "correct": 0, "mistakes": 0,
                "critical_mistakes": 0, "total_time": 0.0, "slowest_step": None}

    slowest_index = max(range(len(steps)), key=lambda i: float(steps[i].get("elapsed", steps[i].get("time", 0))))
    return {
        "steps": len(steps),
        "correct": sum(bool(s.get("correct", False)) for s in steps),
        "mistakes": sum(bool(s.get("mistake", False)) for s in steps),
        "critical_mistakes": sum(bool(s.get("critical", False)) for s in steps),
        "total_time": round(sum(float(s.get("elapsed", s.get("time", 0))) for s in steps), 2),
        "slowest_step": slowest_index + 1,
    }
