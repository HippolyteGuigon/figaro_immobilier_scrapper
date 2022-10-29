import streamlit as st


def write():
    st.title("Scrapper - Le Figaro Immobilier")
    st.header(
        """
        Analysis Page.
        """
    )


if "df_result" not in st.session_state:
    st.session_state[
        "df_result"
    ] = "Lancer le scrapping pour avoir un résultat de DataFrame"
df = st.session_state["df_result"]
