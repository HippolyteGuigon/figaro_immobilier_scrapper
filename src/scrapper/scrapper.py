from selenium import webdriver
import warnings
from tqdm import tqdm
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sys

sys.path.append(
    "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/logs"
)
sys.path.append(
    "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/src/cleaner"
)

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


cleaner = Get_adress()

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
        if "La page demandée n'existe pas" in driver.page_source:
            driver.find_element("xpath", "//button[text()='Retour à l'accueil']")
        else:
            pass

    def accept_cookie(self):

        # On accepte les cookies s'il y en a
        wait = WebDriverWait(driver, 2)
        wait.until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, '//*[@id="appconsent"]/iframe')
            )
        )
        accept = driver.find_element(
            "xpath", "/html/body/div/div/div/div/div/div/div[2]/aside/section/button[1]"
        )
        driver.execute_script("arguments[0].click();", accept)
        driver.implicitly_wait(2)
        driver.switch_to.parent_frame()
        driver.implicitly_wait(2)

    def check_connect(self):
        self.accept_cookie()
        main()
        # Trouver un moyen plus élégant de vérifier la connexion
        if "Saisissez une ou plusieurs villes" in driver.page_source:
            logging.info("La connexion à la page d'acceuil a bien réussie")

    def search_type(self, choice: str):
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

        search_button = driver.find_element(
            "xpath", '//*[@id="homepage-v2"]/section[1]/div/button[2]'
        )
        driver.execute_script("arguments[0].click();", search_button)
        sleep(5)

        if "annonces" in driver.current_url:
            logging.info("La recherche a bien aboutie")
        else:
            logging.info("La recherche n'a pas aboutie")

    def filter_search(self, ville: List):
        # On commence par réinitialiser la recherche
        localisation_button = driver.find_element(
            "xpath", '//*[@id="search-engine"]/div/div[1]/div[2]/div/span/span'
        )
        driver.execute_script("arguments[0].click();", localisation_button)
        sleep(3)
        reinitialise_button = driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[1]/div[2]/div[2]/div[3]/button[1]',
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
            sleep(5)
            search_engine_button.send_keys(" ")
            sleep(5)
            first_choice = driver.find_element(
                "xpath",
                "//*[@id='search-engine']/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[1]",
            )

            driver.execute_script("arguments[0].click();", first_choice)
        sleep(5)
        result_filter = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]'
        ).text
        print(result_filter)
        filtered_cities = result_filter.split("à")[1].split(":")[0]
        validate_button = driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[1]/div[2]/div[2]/div[3]/button[2]',
        )
        driver.execute_script("arguments[0].click();", validate_button)
        sleep(5)
        number_result = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]/span'
        ).text

        logging.warning(
            f"Le filtrage a bien été opéré sur {filtered_cities}, il y a {number_result} annonces"
        )

    def filter_price(self, price_min: int, price_max: int):

        budget_button = driver.find_element(
            "xpath", '//*[@id="search-engine"]/div/div[2]/div[2]/div'
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

        validation_button = driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[2]/div[2]/div[2]/div[3]/button[2]',
        )
        driver.execute_script("arguments[0].click();", validation_button)
        sleep(5)
        number_result = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]/span'
        ).text
        logging.info(
            f"L'utilisateur a filtré les prix entre {price_min}€ et {price_max}€, il y a {number_result} annonces"
        )

    def filter_surface(self, surface_min: int, surface_max: int):
        criterion_button = driver.find_element(
            "xpath", '//*[@id="search-engine"]/div/div[2]/div[3]/div[1]'
        )
        driver.execute_script("arguments[0].click();", criterion_button)
        sleep(5)

        driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[2]/div[3]/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/div[1]/input',
        ).send_keys(surface_min)
        driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[2]/div[3]/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/input',
        ).send_keys(surface_max)

        validation_button = driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[2]/div[3]/div[2]/div[3]/button[2]',
        )
        driver.execute_script("arguments[0].click();", validation_button)
        sleep(5)
        number_result = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]/span'
        ).text
        logging.info(
            f"L'utilisateur a filtré la surface entre {surface_min}m2 et {surface_max}m2, il y a {number_result} annonces"
        )

    def global_filtering(
        self,
        ville: List,
        price_min: int,
        price_max: int,
        surface_min: int,
        surface_max: int,
    ):
        self.filter_search(ville)
        self.filter_surface(surface_min, surface_max)
        self.filter_price(price_min, price_max)


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

    def get_links(self):
        elems = [
            x.get_attribute("href")
            for x in driver.find_elements("xpath", "//a[@href]")
            if "/annonces/annonce" in x.get_attribute("href")
        ]
        while True:
            try:
                next_button = driver.find_element(
                    "xpath", '//*[@id="listAnnoncesBloc"]/section/div[40]/a[2]/div/span'
                )
                driver.execute_script("arguments[0].click();", next_button)
                sleep(5)
                new_elems = [
                    x.get_attribute("href")
                    for x in driver.find_elements("xpath", "//a[@href]")
                    if "/annonces/annonce" in x.get_attribute("href")
                ]
                elems += new_elems
            except:
                break
        json_path = (
            "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/data"
        )
        json_list = json.dumps(elems)

        with open(os.path.join(json_path, "links_to_scrap.json"), "w") as f:
            json.dump(elems, f)

    def individual_extractor(self, link: str):
        try:
            price = driver.find_element(
                "xpath", '//*[@id="app-bis"]/main/div[1]/div/section/div[2]/div/strong'
            ).text
        except NoSuchElementException:
            price = "Inconnu"
        try:
            surface = driver.find_element(
                "xpath", '//*[@id="app-bis"]/main/div[1]/div/div[1]/ul/li[1]/span'
            ).text
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
        data_result_path = "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/data_results"
        path_link_to_scrap = "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/data/links_to_scrap.json"
        path_scrapped = "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/data/links_scrapped.json"

        to_scrap = open(path_link_to_scrap)
        scrapped = open(path_scrapped)

        for city in self.ville:
            city=city.rstrip('0123456789').strip().replace(" ","_").lower().capitalize()
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

        for link_scrap in tqdm(data_to_scrap):
            if link_scrap not in data_scrapped:
                driver.get(link_scrap)

                if "Cette annonce a expiré" in driver.page_source:
                    pass
                else:

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
                    ville = localisation.split(" ")[1].replace(" ","_").replace("-","_").lower().capitalize()
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
                    df_city.to_csv(ville + "/df_" + ville + ".csv")

        path_cleaning = "/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/data_results"

        #Faire en sorte que le nettoyage ne s'applique que sur les nouvelles villes scrappées
        for file_ville in os.listdir(path_cleaning):
            df_path = os.path.join(path_cleaning, file_ville, f"df_{file_ville}.csv")
            df_to_clean = pd.read_csv(df_path)
            cleaner_df = DataFrame_cleaning(df_to_clean)
            df_cleaned = cleaner_df.global_cleaner()
            os.remove(df_path)
            df_cleaned.to_csv(df_path)