import streamlit as st
import pandas as pd
import os
import plotly.express as px

current_path = os.getcwd()

df_result = pd.read_csv(
    os.path.join(current_path, "app/src/data_analysis/data_analysis_result.csv")
)
df_reduced = pd.read_csv(
    os.path.join(current_path, "app/src/data_analysis/df_reduced.csv")
)
df_reduced = df_reduced[["0", "1", "2"]]
df_reduced.columns = ["First dimension", "Second dimension", "Third dimension"]
df_reduced[["link", "cluster"]] = df_result[["link", "labels_predicted"]]
city = df_result["localisation"][0].strip().split(" ")[0]


def write():
    st.title("Scrapper - Le Figaro Immobilier")
    st.header(
        """
        Analysis Page.
        """
    )

    plot = px.scatter(
        df_reduced,
        x="First dimension",
        y="Second dimension",
        color="cluster",
        title=f"Scatter Plot in 2 dimensions of clustered city {city}",
    )
    st.plotly_chart(plot)
