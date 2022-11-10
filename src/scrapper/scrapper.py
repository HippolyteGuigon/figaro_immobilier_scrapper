from selenium import webdriver
import warnings
from tqdm import tqdm
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import os
import sys
from stqdm import stqdm
import streamlit as st

current_path = os.getcwd()
sys.path.insert(0, os.path.join(current_path, "logs"))
sys.path.insert(0, os.path.join(current_path, "src/cleaner"))
sys.path.insert(0, os.path.join(current_path, "src/filter"))

from logs_config import main
from filter import *
import logging
import pandas as pd
from selenium.webdriver.common.by import By
from typing import List
from time import sleep
import json
import os
from cleaner import Get_adress, DataFrame_cleaning

warnings.filterwarnings("ignore")

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("start-maximized")
options.add_argument("--log-level=3")


cleaner = Get_adress()


url = "https://immobilier.lefigaro.fr/"
driver = webdriver.Chrome(service=s, options=options)
driver.maximize_window()


class Scrapper(Filtering):
    """
    Class that inherits from Filtering and launchs the scrapping itslef
    get_links: Recovers all links that will be scrapped from the filtered page provided
    individual_extractor: Get all information (surface,price etc) from individual announce
    launch_scrapping: Global function to launch scrapping and have all results saved under certain path
    """

    def __init__(
        self,
        choix: str,
        ville: List,
        surface_min: float,
        surface_max: float,
        price_min: float,
        price_max: float,
    ):
        self.ville = ville
        super().skip_error_page()
        super().check_connect()
        super().search_type(choix)
        super().global_filtering(ville, price_min, price_max, surface_min, surface_max)

        url_path = open(os.path.join(current_path, "data/current_url.json"))
        current_url = json.load(url_path)
        driver.get(current_url)

    def get_links(self):
        """
        The goal of this function is, after filtering has been performed, 
        to recover all links of annonces refering to this filtering 
        """
        df_save = pd.DataFrame(columns=["check"])
        elems = [
            x.get_attribute("href")
            for x in driver.find_elements("xpath", "//a[@href]")
            if "/annonces/annonce" in x.get_attribute("href")
        ]

        while True:
            try:
                next_button = driver.find_element(
                    By.XPATH, "//a[@title='Aller à la page suivante']"
                )

                driver.execute_script("arguments[0].click();", next_button)
                sleep(4)
                new_elems = [
                    x.get_attribute("href")
                    for x in driver.find_elements("xpath", "//a[@href]")
                    if "/annonces/annonce" in x.get_attribute("href")
                ]
                elems += new_elems
                if len(list(set(elems))) != len(elems):
                    elems = list(set(elems))
                    break
            except:
                break
        json_path = os.path.join(current_path, "data")
        json_list = json.dumps(elems)

        with open(os.path.join(json_path, "links_to_scrap.json"), "w") as f:
            json.dump(elems, f)


    def individual_extractor(self, link: str):
        try:
            price = driver.find_element(
                By.XPATH, './/span[@class = "price"]'
            ).get_attribute("innerHTML")
        except NoSuchElementException:
            price = "Inconnu"
        try:
            surface = driver.find_element(By.CLASS_NAME, "feature").get_attribute(
                "textContent"
            )
        except NoSuchElementException:
            surface = "Inconnu"

        # Trouver une manière plus élégante pour les try/except
        try:
            localisation = driver.find_element(
                "xpath", '//*[@id="classified-main-infos"]/span'
            ).text.replace("à", "")
        except NoSuchElementException:
            try:
                localisation = driver.find_element(
                    "xpath", '//*[@id="app-bis"]/main/div[1]/div/section/div[6]/p'
                ).get_attribute("innerHTML")

            except:
                try:
                    localisation = driver.find_element(
                        "xpath", '//*[@id="app-bis"]/main/div[1]/div/section/div[5]/p'
                    )
                except:
                    localisation = "Inconnu"
        try:
            description = driver.find_element(
                "xpath", '//*[@id="app-bis"]/main/div[1]/div/section/div[6]/p'
            ).text
        except NoSuchElementException:
            try:
                description = driver.find_element(
                    "xpath", "//*[@id='app-bis']/main/div[1]/div/section/div[5]/p"
                ).get_attribute("innerHTML")
            except NoSuchElementException:
                try:
                    description = driver.find_element(
                        "xpath", "//*[@id='app-bis']/main/div[1]/div/section/div[6]/p"
                    ).get_attribute("innerHTML")
                except:
                    description = "Inconnu"

        try:
            nombre_pieces = driver.find_element(
                "xpath", '//*[@id="app-bis"]/main/div[1]/div/div[1]/ul/li[2]/span'
            ).text
        except NoSuchElementException:
            nombre_pieces = "Inconnu"
        return price, surface, localisation, description, nombre_pieces, link

    def launch_scrapping(self):

        logging.warning("Le scrapping vient de commencer")
        data_result_path = os.path.join(current_path, "data_results")
        path_link_to_scrap = os.path.join(current_path, "data/links_to_scrap.json")
        path_scrapped = os.path.join(current_path, "data/links_scrapped.json")

        to_scrap = open(path_link_to_scrap)
        scrapped = open(path_scrapped)

        for city in self.ville:
            city = (
                city.rstrip("0123456789").strip().replace(" ", "_").lower().capitalize()
            )
            if not os.path.exists(os.path.join(data_result_path, city)):
                os.makedirs(os.path.join(data_result_path, city))
                df_city = pd.DataFrame(
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
                os.chdir(os.path.join(data_result_path, city))
                df_city.to_csv(f"df_{city}.csv")
        data_to_scrap = json.load(to_scrap)
        data_scrapped = json.load(scrapped)

        os.chdir(data_result_path)

        st.write(
            f"Il y a {len(data_to_scrap)} annonces correspondant à vos critères de recherche"
        )
        for link_scrap in stqdm(data_to_scrap):
            if link_scrap not in data_scrapped:
                driver.get(link_scrap)

                if "Cette annonce a expiré" in driver.page_source:
                    pass
                else:
                    try:

                        (
                            price,
                            surface,
                            localisation,
                            description,
                            nombre_pieces,
                            link,
                        ) = self.individual_extractor(link_scrap)
                        data_scrapped.append(link_scrap)
                        with open(path_scrapped, "w") as f:
                            json.dump(data_scrapped, f)
                        ville = (
                            localisation.split(" ")[1]
                            .replace(" ", "_")
                            .replace("-", "_")
                            .lower()
                            .capitalize()
                        )
                        df_city = pd.read_csv(ville + "/df_" + ville + ".csv")
                        df_city = df_city[
                            [
                                "price",
                                "surface",
                                "localisation",
                                "description",
                                "nombre_pieces",
                                "rue",
                                "link",
                            ]
                        ]

                        cleaner = Get_adress()
                        df_city.loc[df_city.shape[0] + 1, :] = [
                            price,
                            surface,
                            localisation,
                            description,
                            nombre_pieces,
                            "TBD",
                            link,
                        ]
                        if "Paris" in ville:

                            df_city.loc[df_city.shape[0], "rue"] = cleaner.pipeline(
                                df_city.loc[df_city.shape[0], "localisation"],
                                df_city.loc[df_city.shape[0], "description"],
                            )
                        else:
                            df_city.loc[df_city.shape[0], "rue"] = "Inconnu"
                        df_city = df_city[
                            [
                                "price",
                                "surface",
                                "localisation",
                                "description",
                                "nombre_pieces",
                                "rue",
                                "link",
                            ]
                        ]
                        df_city.to_csv(ville + "/df_" + ville + ".csv", index=False)
                    except:
                        pass

        path_cleaning = os.path.join(current_path, "data_results")

        for file_ville in os.listdir(path_cleaning):
            df_path = os.path.join(path_cleaning, file_ville, f"df_{file_ville}.csv")
            df_to_clean = pd.read_csv(df_path)
            cleaner_df = DataFrame_cleaning(df_to_clean)
            df_cleaned = cleaner_df.global_cleaner()
            os.remove(df_path)
            df_cleaned.to_csv(df_path)

        st.write("Le scrapping est terminé !")
