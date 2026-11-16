
import streamlit as st
from open_data import find_nearest_aeds

st.title("❤️ Пошук дефібриляторів AED")
st.write("Пошук найближчих AED за відкритими даними OpenStreetMap.")

st.info("У надзвичайній ситуації телефонуйте 103 або 112.")

latitude = st.number_input(
    "Широта",
    min_value=-90.0,
    max_value=90.0,
    value=50.4501,
    format="%.6f"
)

longitude = st.number_input(
    "Довгота",
    min_value=-180.0,
    max_value=180.0,
    value=30.5234,
    format="%.6f"
)

if st.button("Знайти найближчі AED"):
    try:
        with st.spinner("Завантажуємо відкриті дані..."):
            aeds = find_nearest_aeds(latitude, longitude)

        st.success(f"Знайдено {len(aeds)} найближчих точок")

        st.dataframe(
            aeds[["name", "distance_km", "location", "access"]],
            hide_index=True
        )

        st.map(
            aeds.rename(
                columns={
                    "latitude": "lat",
                    "longitude": "lon"
                }
            )
        )

    except Exception as error:
        st.error(f"Не вдалося завантажити дані: {error}")

st.caption(
    "Джерело: OpenStreetMap contributors, ODbL. "
    "Відстань по прямій. Фактичну доступність AED "
    "потрібно перевіряти."
)
