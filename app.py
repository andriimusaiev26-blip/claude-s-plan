"""Роль 4 (Лєра): інтерфейс на Streamlit. Запуск: streamlit run app.py"""
import time

import streamlit as st

import charts
import data_loader
import quiz

st.set_page_config(page_title="Перші 10 секунд", page_icon="⛑")

topics = data_loader.load_topics()
questions = data_loader.load_questions()
scenarios = data_loader.load_scenarios()

state = st.session_state
state.setdefault("stage", "choose")
state.setdefault("feedback", "")


def go(stage: str) -> None:
    """Перемикає екран програми."""
    state.stage = stage
    st.rerun()


def show_feedback() -> None:
    """Показує пояснення до попередньої відповіді."""
    if state.feedback:
        st.warning(state.feedback)
        state.feedback = ""


def start_scenario() -> None:
    """Готує сценарій обраної теми з першого кроку."""
    state.node = quiz.start_node(state.topic["topic_id"])
    state.steps = []
    state.shown_at = time.time()
    go("scenario")


# 1. Вибір теми
if state.stage == "choose":
    st.title("Перші 10 секунд")
    st.write("Тренажер домедичної допомоги за протоколами МОЗ.")
    title = st.selectbox("Оберіть тему", topics["title"])
    if st.button("Почати"):
        state.topic = topics[topics["title"] == title].iloc[0]
        state.q_index = 0
        state.q_correct = 0
        go("summary")

# 2. Конспект
elif state.stage == "summary":
    st.header(state.topic["title"])
    st.info(state.topic["summary"])
    st.caption(f"Джерело: {state.topic['source']}")
    if st.button("До питань"):
        go("questions")

# 3. Три питання по конспекту
elif state.stage == "questions":
    show_feedback()
    topic_q = quiz.get_questions(questions, state.topic["topic_id"])
    if state.q_index >= len(topic_q):
        st.success(f"Правильних відповідей: {state.q_correct} з {len(topic_q)}")
        if st.button("Перейти до сценарію на час"):
            start_scenario()
    else:
        row = topic_q.iloc[state.q_index]
        st.subheader(f"Питання {state.q_index + 1} з {len(topic_q)}")
        answer = st.radio(
            row["question"],
            quiz.OPTION_KEYS,
            format_func=lambda key: row[f"option_{key}"],
            index=None,
        )
        if st.button("Відповісти") and answer:
            if quiz.check_question(row, answer):
                state.q_correct += 1
            else:
                state.feedback = f"Неправильно. {row['explain']}"
            state.q_index += 1
            st.rerun()

# 4. Сценарій з розгалуженнями на час
elif state.stage == "scenario":
    show_feedback()
    options = quiz.get_node(scenarios, state.node)
    st.subheader(options.iloc[0]["text"])
    st.caption(f"⏱ У вас {options.iloc[0]['time_limit']} секунд")
    shuffled = options.sample(frac=1, random_state=len(state.steps))
    for i, opt in shuffled.iterrows():
        if st.button(opt["option"], key=f"{state.node}_{i}"):
            step = quiz.choose(opt, time.time() - state.shown_at)
            state.steps.append(step)
            state.feedback = step["explain"]
            if step["next_node"] in ("END_OK", "END_FAIL"):
                state.final = step["next_node"]
                go("result")
            state.node = step["next_node"]
            state.shown_at = time.time()
            st.rerun()

# 5. Підсумок і графіки
elif state.stage == "result":
    summary = quiz.score(state.steps)
    if state.final == "END_OK":
        st.success("Ви впоралися! Допомога приїхала вчасно.")
    else:
        st.error("Стан постраждалого погіршився. Спробуйте ще раз.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Кроків", summary["steps"])
    col2.metric("Помилок", summary["mistakes"])
    col3.metric("Час, с", summary["total_time"])
    if summary.get("slowest"):
        st.write(f"Найповільніший крок: {summary['slowest']}")

    st.pyplot(charts.plot_step_times(state.steps))
    if hasattr(charts, "plot_results_pie"):
        st.pyplot(charts.plot_results_pie(state.steps))

    for step in state.steps:
        if step["explain"]:
            st.write(f"• {step['explain']}")

    if st.button("Пройти сценарій ще раз"):
        start_scenario()
    if st.button("Обрати іншу тему"):
        go("choose")
