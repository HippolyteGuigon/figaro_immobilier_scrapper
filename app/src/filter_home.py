import streamlit as st
import sys
import pandas as pd
import awesome_streamlit as ast
import sys
import os

sys.path.append(
    "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/app/src"
)
sys.path.append(
    "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/src/scrapper"
)

from scrapper import *
from analysis import *

df_ville = pd.read_csv(
    "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/app/Liste_commune.csv"
)
liste_ville = df_ville["Nom_commune"].unique()


def write():
    st.title("Scrapper - Le Figaro Immobilier")
    st.header(
        """
        Filtering Page.
        """
    )

    with st.expander("Paramètre de filtre", expanded=True):

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            type_recherche = st.selectbox("Type de recherche", ["Acheter", "Louer"], 0)
        with col2:
            ville_filtre = st.multiselect("Entrer les lieux", liste_ville)

        with col3:
            filter_surface = st.slider(
                "Champs de surface (en m2)",
                value=[1, 2000],
                step=1,
            )
        with col4:

            if type_recherche == "Acheter":

                price_range = st.slider(
                    "Champs de prix (en €)", value=[1, 1000000], step=1
                )
            else:
                price_range = st.slider(
                    "Champs de prix (en €)", value=[1, 30000], step=1
                )

    if st.button("Launch scrapping"):
        # Mettre un bouton pour lancer le scrapping, et ensuite balancer la recherche
        scr = Scrapper(
            type_recherche.lower(),
            ville_filtre,
            filter_surface[0],
            filter_surface[1],
            price_range[0],
            price_range[1],
        )
        scr.get_links()
        scr.launch_scrapping()

    if st.button("Begin Analysis of scrapped data"):
        ville = (
            ville_filtre[0]
            .rstrip("0123456789")
            .strip()
            .replace(" ", "_")
            .replace("-", "_")
            .lower()
            .capitalize()
        )
        path_search = os.path.join(
            "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/data_results",
            ville,
            "df_" + str(ville) + ".csv",
        )
        df = pd.read_csv(path_search)
        df = df[
            (df.surface >= filter_surface[0])
            & (df.surface <= filter_surface[1])
            & (df.price >= price_range[0])
            & (df.price <= price_range[1])
        ]
        os.chdir(
            "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/app/src"
        )
        df.to_csv("checking.csv", index=False)
        if "df" not in st.session_state:
            st.session_state["df"] = df
