"""Оформлення інтерфейсу: жовто-червоний типографічний стиль (лише CSS, без логіки).

Підключення в app.py одразу після st.set_page_config(...):
    import styles
    styles.apply()
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@700;800;900&family=Inter:wght@400;500;600&display=swap');

:root {
    --red: #E3241B;
    --maroon: #A3161C;
    --yellow: #FCE38A;
    --cream: #FBF5EE;
    --ink: #2B1A16;
    --line: #E9DCCB;
    --r: 16px;  /* радіус скруглення кутів */
}

/* Фон і основний шрифт */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: var(--cream) !important;
    color: var(--ink) !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.block-container { max-width: 820px !important; padding-top: 2.5rem !important; }

/* Головний заголовок: великий червоний на жовтому блоці */
h1 {
    font-family: 'Inter Tight', sans-serif !important;
    font-weight: 900 !important;
    font-size: 3.4rem !important;
    line-height: 0.95 !important;
    letter-spacing: -0.045em;
    color: var(--red) !important;
    background: var(--yellow);
    padding: 2rem 1.6rem 1.6rem !important;
    border-radius: 24px;
    margin-bottom: 1rem !important;
}
/* Підзаголовки */
h2, h3 {
    font-family: 'Inter Tight', sans-serif !important;
    font-weight: 800 !important;
    color: var(--red) !important;
    letter-spacing: -0.03em;
    line-height: 1.1 !important;
}
p, li, label, span { color: var(--ink); }

/* Кнопки-варіанти: білі блоки, при наведенні жовті з червоним */
.stButton > button {
    width: 100%;
    min-height: 3.2rem;
    border-radius: var(--r) !important;
    border: 2px solid var(--line) !important;
    background: #FFFFFF !important;
    color: var(--ink) !important;
    font-weight: 600 !important;
    text-align: left;
    transition: background .12s ease, border-color .12s ease, color .12s ease;
}
.stButton > button:hover {
    background: var(--yellow) !important;
    border-color: var(--red) !important;
    color: var(--red) !important;
}
/* Головна кнопка (type="primary"): червона, як «Contact» у шаблоні */
.stButton > button[kind="primary"] {
    background: var(--red) !important;
    border-color: var(--red) !important;
    color: #FFFFFF !important;
    text-transform: uppercase;
    letter-spacing: .12em;
    font-size: .8rem !important;
    text-align: center;
    border-radius: 999px !important;
}
.stButton > button[kind="primary"]:hover { background: var(--maroon) !important; color: #FFFFFF !important; }

/* Варіанти відповіді у питаннях */
[data-testid="stRadio"] [role="radiogroup"] { gap: .5rem; }
[data-testid="stRadio"] [role="radiogroup"] > label {
    border: 2px solid var(--line);
    background: #FFFFFF;
    padding: .9rem 1rem;
    width: 100%;
    border-radius: var(--r);
}
[data-testid="stRadio"] [role="radiogroup"] > label:hover { background: var(--yellow); border-color: var(--red); }

/* Вибір теми */
[data-baseweb="select"] > div {
    border-radius: var(--r) !important;
    border: 2px solid var(--ink) !important;
    background: #FFFFFF !important;
}

/* Блоки повідомлень */
[data-testid="stAlert"], [data-testid="stAlert"] > div, [data-baseweb="notification"] {
    border-radius: var(--r) !important;
    border: none !important;
}
/* Конспект (info) — жовтий */
div:has(> [data-testid="stAlertContentInfo"]) { background: var(--yellow) !important; }
div:has(> [data-testid="stAlertContentInfo"]) * { color: var(--ink) !important; }
/* Успіх — червоний з білим текстом */
div:has(> [data-testid="stAlertContentSuccess"]) { background: var(--red) !important; }
div:has(> [data-testid="stAlertContentSuccess"]) * { color: #FFFFFF !important; font-weight: 600; }
/* Пояснення помилки (warning) — білий блок з червоною смугою */
div:has(> [data-testid="stAlertContentWarning"]) {
    background: #FFFFFF !important;
    border: 2px solid var(--red) !important;
}
div:has(> [data-testid="stAlertContentWarning"]) * { color: var(--ink) !important; }
/* Провал — бордовий */
div:has(> [data-testid="stAlertContentError"]) { background: var(--maroon) !important; }
div:has(> [data-testid="stAlertContentError"]) * { color: #FFFFFF !important; font-weight: 600; }

/* Метрики підсумку: жовті плитки з великими червоними цифрами */
[data-testid="stMetric"] {
    background: var(--yellow);
    padding: 1rem 1.1rem;
    border-radius: var(--r);
}
[data-testid="stMetricLabel"] * {
    text-transform: uppercase;
    letter-spacing: .1em;
    font-size: .72rem !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Inter Tight', sans-serif !important;
    font-weight: 900 !important;
    color: var(--red) !important;
}

/* Дрібні підписи: таймер, джерело */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {
    color: #8A6F62 !important;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-size: .72rem !important;
}

/* Смуга прогресу */
[data-testid="stProgress"] > div > div > div > div { background: var(--red) !important; border-radius: 999px !important; }
</style>
"""


def apply() -> None:
    """Підключає стилі до сторінки."""
    st.markdown(CSS, unsafe_allow_html=True)
