import streamlit as st
import sys
import pandas as pd 

sys.path.append(
    "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/scrapper"
)

from scrapper import *

df_ville=pd.read_csv("Liste_commune.csv")
liste_ville=df_ville["Nom_commune"].unique()

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
                "Champs de surface (en m2)", value=[1,2000],
                step=1,
            )
        with col4:

            if type_recherche=="Acheter":

                price_range = st.slider(
                "Champs de prix (en €)", value=[1,1000000],  step=1
            )
            else:
                price_range = st.slider(
                "Champs de prix (en €)", value=[1,30000],  step=1
            )
            

    if st.button('Launch scrapping'):
        # Mettre un bouton pour lancer le scrapping, et ensuite balancer la recherche
        scr = Scrapper(
            type_recherche.lower(), ville_filtre, filter_surface[0], filter_surface[1], price_range[0], price_range[1]
        )
        scr.get_links()
        scr.launch_scrapping()

    st.write('Scrapping is over !')