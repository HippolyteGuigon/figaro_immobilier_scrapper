import streamlit as st
import sys
import pandas as pd
import awesome_streamlit as ast
import sys
import os

current_path = os.getcwd()
sys.path.append(os.path.join(current_path, "app/src"))
sys.path.append(os.path.join(current_path, "src/scrapper"))
sys.path.append(os.path.join(current_path, "src/model"))

from model import *
from scrapper import *
from analysis import *

df_ville = pd.read_csv(os.path.join(current_path, "app/Liste_commune.csv"))
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

    df_result = pd.DataFrame(
        columns=[
            "price",
            "surface",
            "localisation",
            "description",
            "nombre_pieces",
            "rue",
            "link",
        ]
    )

    if st.button("Begin Analysis of scrapped data"):

        for ville in ville_filtre:

            ville_path = (
                ville.rstrip("0123456789")
                .strip()
                .replace(" ", "_")
                .replace("-", "_")
                .lower()
                .capitalize()
            )
            path_search = os.path.join(
                current_path,
                "data_results",
                ville_path,
                "df_" + str(ville_path) + ".csv",
            )
            df = pd.read_csv(path_search)
            df = df[
                (df.surface >= filter_surface[0])
                & (df.surface <= filter_surface[1])
                & (df.price >= price_range[0])
                & (df.price <= price_range[1])
            ]

            df = df[[x for x in df.columns if "Unnamed" not in x]]
            df_result = pd.concat([df_result, df])

        pipeline = Clustering_Pipeline(df_result)
        df_result = pipeline.full_pipeline()
        pipeline_reduced = Clustering_Pipeline(df_result)
        df_reduced = pipeline_reduced.cleaning_df()
        df_reduced = pipeline_reduced.reduction_dimension()

        df_result.to_csv(
            os.path.join(
                current_path, "app/src/data_analysis/data_analysis_result.csv"
            ),
            index=False,
        )

        df_reduced.to_csv(
            os.path.join(current_path, "app/src/data_analysis/df_reduced.csv")
        )

        st.write(
            "Passez maintenant à la page d'analyse en cliquant sur le bouton en haut à gauche !"
        )
        if "df_result" not in st.session_state:
            st.session_state["df_result"] = df_result
