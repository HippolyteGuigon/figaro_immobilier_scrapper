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

from logs_config import main
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

url = "https://immobilier.lefigaro.fr/"
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)
driver.maximize_window()
driver.get(url)


class Filtering:
    """
    Class that leads to the good page according to user's choices
    skip_error_page: If an announce is no longer available, bring back user
    to first page
    accept_cookie: Automatically accept the cookie pop-up page for
    better visibility
    check_connect: Checks that the website has well been reached
    and scrapping can be done
    search_type: Ask user to define the kind of search he wants,
    buying or renting"""

    def __init__(self):
        pass

    def skip_error_page(self):
        """The goal of this function is to avoid the situation
        when the main page is not found by going back to the main page"""
        if "La page demandée n'existe pas" in driver.page_source:
            driver.find_element("xpath", "//button[text()='Retour à l'accueil']")
        else:
            pass

    def accept_cookie(self):
        """The goal of this function is to accept cookies and make
        banner disappear"""
        # On accepte les cookies s'il y en a
        wait = WebDriverWait(driver, 2)
        try:
            wait.until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.XPATH, '//*[@id="appconsent"]/iframe')
                )
            )
            accept = driver.find_element(
                "xpath",
                "/html/body/div/div/div/div/div/div/div[2]/aside/section/button[1]",
            )
            driver.execute_script("arguments[0].click();", accept)
        except:
            pass
        driver.implicitly_wait(2)
        driver.switch_to.parent_frame()
        driver.implicitly_wait(2)

    def check_connect(self):
        """
        choice : str, The user chooses between acheter or louer
        The goal of this function is to make sure that, after the
        user has made his choice, the right page is hitted"""
        self.accept_cookie()
        main()
        # Trouver un moyen plus élégant de vérifier la connexion
        if "Saisissez une ou plusieurs villes" in driver.page_source:
            logging.info("La connexion à la page d'acceuil a bien réussie")
            return "La connexion à la page d'acceuil a bien réussie"
        else:
            return "La connexion à la page d'acceuil a echoué"

    def search_type(self, choice):
        """choice : str, The user chooses between acheter or louer.
        The goal of this function is to make user choosing between
        acheter or louer and to carry on the filtering"""
        choice = str(choice).lower()
        assert choice in [
            "acheter",
            "louer",
        ], "L'utilisateur doit choisir entre acheter et louer un bien"
        logging.warning(f"L'utilisateur a choisi l'otion {choice}")

        if driver.current_url != url:
            driver.get(url)

        if choice == "acheter":
            element = driver.find_element(
                "xpath", '//*[@id="homepage-v2"]/section[1]/div/div[1]/button[1]'
            )
            driver.execute_script("arguments[0].click();", element)

        else:

            element = driver.find_element(
                "xpath", '//*[@id="homepage-v2"]/section[1]/div/div[1]/button[2]'
            )
            driver.execute_script("arguments[0].click();", element)

        search_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="homepage-v2"]/section[1]/div/button[2]')
            )
        )

        driver.execute_script("arguments[0].click();", search_button)

        sleep(3.5)

        if "annonces" in driver.current_url:
            logging.info("La recherche a bien aboutie")
            return "La recherche a bien aboutie"
        else:
            logging.info("La recherche n'a pas aboutie")
            return "La recherche n'a pas aboutie"

    def filter_search(self, ville: List[str]):
        """ville: List[str]: The cities that the user want to filter on
        The goal of this function is to operate a filtering on a list
        of cities chosen by the user"""
        # On commence par réinitialiser la recherche
        localisation_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="search-engine"]/div/div[1]/div[2]/div/span/span')
            )
        )

        driver.execute_script("arguments[0].click();", localisation_button)

        sleep(3)

        reinitialise_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="search-engine"]/div/div[1]/div[2]/div[2]/div[3]/button[1]',
                )
            )
        )

        driver.execute_script("arguments[0].click();", reinitialise_button)

        # Faire en sorte que l'utilisateur puisse entrer une liste de ville
        if len(ville) == 1:
            logging.warning(
                f"L'utilisateur a choisi la région {ville[0]}".replace("[", "").replace(
                    "]", ""
                )
            )
        else:
            logging.warning(
                f"L'utilisateur a choisi les régions: {[v for v in ville]}".replace(
                    "[", ""
                ).replace("]", "")
            )
        search_engine_button = driver.find_element(
            "xpath",
            "//*[@id='search-engine']/div/div[1]/div[2]/div[2]/div[2]/div/div/input",
        )

        for choice_region in ville:
            search_engine_button.send_keys(choice_region)
            sleep(3)
            search_engine_button.send_keys(" ")
            sleep(3)

            first_choice = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="search-engine"]/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[1]',
                    )
                )
            )

            driver.execute_script("arguments[0].click();", first_choice)

        sleep(4)
        result_filter = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]'
        ).text
        filtered_cities = result_filter.split("à")[1].split(":")[0]

        validate_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="search-engine"]/div/div[1]/div[2]/div[2]/div[3]/button[2]',
                )
            )
        )

        driver.execute_script("arguments[0].click();", validate_button)

        sleep(4)

        number_result = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]/span'
        ).text

        logging.warning(
            f"Le filtrage a bien été opéré sur {filtered_cities}, il y a {number_result} annonces"
        )

        return f"Le filtrage a bien été opéré sur {filtered_cities}, il y a {number_result} annonces"

    def filter_price(self, price_min: int, price_max: int):
        """price_min: int  The minimal price filtered on
        price_max: int The maximal price filtered on
        The goal of this function is to carry out the
        filtering based on price, between minimum and maximum"""

        budget_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="search-engine"]/div/div[2]/div[2]/div')
            )
        )

        driver.execute_script("arguments[0].click();", budget_button)

        sleep(5)

        driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/input',
        ).send_keys(price_min)
        driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[2]/div[2]/div[2]/div[2]/div[1]/div[2]/input',
        ).send_keys(price_max)
        validation_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="search-engine"]/div/div[2]/div[2]/div[2]/div[3]/button[2]',
                )
            )
        )

        driver.execute_script("arguments[0].click();", validation_button)
        sleep(4)
        number_result = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]/span'
        ).text
        logging.info(
            f"L'utilisateur a filtré les prix entre {price_min}€ et {price_max}€, il y a {number_result} annonces"
        )

        return f"L'utilisateur a filtré les prix entre {price_min}€ et {price_max}€, il y a {number_result} annonces"

    def filter_surface(self, surface_min: int, surface_max: int):
        """surface_min: int  The minimum surface in m2 filtered on
        surface_max: int  The maximum surface in m2 filtered on"""
        criterion_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="search-engine"]/div/div[2]/div[3]/div[1]')
            )
        )

        driver.execute_script("arguments[0].click();", criterion_button)
        sleep(4)

        driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[2]/div[3]/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/div[1]/input',
        ).send_keys(surface_min)
        driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[2]/div[3]/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/input',
        ).send_keys(surface_max)

        validation_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="search-engine"]/div/div[2]/div[3]/div[2]/div[3]/button[2]',
                )
            )
        )

        driver.execute_script("arguments[0].click();", validation_button)

        sleep(4)
        number_result = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]/span'
        ).text
        logging.info(
            f"L'utilisateur a filtré la surface entre {surface_min}m2 et {surface_max}m2, il y a {number_result} annonces"
        )
        return f"L'utilisateur a filtré la surface entre {surface_min}m2 et {surface_max}m2, il y a {number_result} annonces"

    def url_recovering(self):
        """The goal of the function is, once the filtering is
        over, to recover the corresponding url and save it in
        a json named current_url.json that will then be used
        for scrapping"""
        current_url = driver.current_url
        json_path = os.path.join(current_path, "data")
        json_list = json.dumps(current_url)

        with open(os.path.join(json_path, "current_url.json"), "w") as f:
            json.dump(current_url, f)

    def global_filtering(
        self,
        ville: List[str],
        price_min: int,
        price_max: int,
        surface_min: int,
        surface_max: int,
    ):
        """ville: List[str]  The list of cities the user wants to filter on
        price_min: int    The minimum price the user wants to filter on
        price_max: int    The maximum price the user wants to filter on
        surface_min: int  The minimum surface the user wants to filter on
        surface_max: int  The maximum surface the user wants to filter on

        The goal of this function is to wrap out all functions coded so
        far in the filtering and operate the full filtering pipeline"""
        self.filter_search(ville)
        self.filter_surface(surface_min, surface_max)
        self.filter_price(price_min, price_max)
        self.url_recovering()
