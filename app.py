"""Роль 4 (Лєра): інтерфейс на Streamlit. Запуск: streamlit run app.py"""
import time

import streamlit as st

import charts
import data_loader
import quiz

st.set_page_config(page_title="Перші 10 секунд", page_icon="⛑")

state = st.session_state
state.setdefault("stage", "choose")


def go(stage: str) -> None:
    """Перемикає екран програми."""
    state.stage = stage
    st.rerun()


if state.stage == "choose":
    # TODO: вибір теми
    st.title("Перші 10 секунд")

elif state.stage == "summary":
    # TODO: конспект теми
    pass

elif state.stage == "questions":
    # TODO: 3 питання по конспекту
    pass

elif state.stage == "scenario":
    # TODO: сценарій на час
    pass

elif state.stage == "result":
    # TODO: підсумок і графіки
    pass
