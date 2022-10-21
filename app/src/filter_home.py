import streamlit as st
import sys

sys.path.append(
    "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/scrapper/scrapper.py"
)

from scrapper import *


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
            # Faire en sorte que l'utilisateur puisse choisir plusieurs villes
            ville_filtre = st.selectbox("Entrer le lieux", ["Paris", "Marseille"])
        with col2:
            price_range = st.slider(
                "Champs de prix (en €)", min_value=1, max_value=30000, value=10, step=1
            )
        with col3:
            filter_surface = st.slider(
                "Champs de surface (en m2)",
                min_value=1,
                max_value=800,
                value=10,
                step=1,
            )
        with col4:
            type_recherche = st.selectbox("Type de recherche", ["Acheter", "Louer"], 0)
    # Mettre un bouton pour lancer le scrapping, et ensuite balancer la recherche
    scr = Scrapper(
        type_recherche.lower(), [ville_filtre], 0, filter_surface, 0, price_range
    )
