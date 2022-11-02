import streamlit as st
import pandas as pd

df_result = pd.read_csv(
    "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/app/src/data_analysis/data_analysis_result.csv"
)


def write():
    st.title("Scrapper - Le Figaro Immobilier")
    st.header(
        """
        Analysis Page.
        """
    )
