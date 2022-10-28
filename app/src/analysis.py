import streamlit as st


def write():
    st.title("Scrapper - Le Figaro Immobilier")
    st.header(
        """
        Analysis Page.
        """
    )


if "df" not in st.session_state:
    st.session_state["df"] = "value"

df = st.session_state["df"]
