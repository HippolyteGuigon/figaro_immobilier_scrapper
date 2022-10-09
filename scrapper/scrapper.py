from selenium import webdriver
import warnings

warnings.filterwarnings("ignore")
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("start-maximized")
options.add_argument("--log-level=3")
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import sys
from logs.logs_config import main
import logging
from selenium.webdriver.common.by import By
from typing import List
from time import sleep

url = "https://immobilier.lefigaro.fr/"
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)
driver.maximize_window()
driver.get(url)


class Scrapper:
    def __init__(self):
        pass
    
    def accept_cookie(self):

        # On accepte les cookies s'il y en a
        wait = WebDriverWait(driver, 2)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="appconsent"]/iframe')))
        accept=driver.find_element("xpath",'/html/body/div/div/div/div/div/div/div[2]/aside/section/button[1]')
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
    
    def search_type(self, choice):
        choice = str(choice).lower()
        assert choice in [
            "acheter",
            "louer",
        ], "L'utilisateur doit choisir entre acheter et louer un bien"
        logging.warning(f"L'utilisateur a choisi l'otion {choice}")

        if driver.current_url != url:
            driver.get(url)

        if choice == "acheter":
            driver.save_screenshot("screenshot1.png")
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
        
        print(driver.current_url)
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
        driver.implicitly_wait(3)
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


        for choice_region in ville:
            driver.find_element(
                "xpath",
                "//*[@id='search-engine']/div/div[1]/div[2]/div[2]/div[2]/div/div/input",
            ).send_keys(choice_region)
            driver.implicitly_wait(3)
            first_choice = driver.find_element(
                "xpath",
                "//*[@id='search-engine']/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[1]",
            )
            try:
                driver.execute_script("arguments[0].click();", first_choice)
            except:
                driver.find_element(
                "xpath",
                "//*[@id='search-engine']/div/div[1]/div[2]/div[2]/div[2]/div/div/input",
            ).send_keys(choice_region)
                driver.implicitly_wait(3)
                first_choice = driver.find_element(
                    "xpath",
                    "//*[@id='search-engine']/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[1]",
                )
                driver.execute_script("arguments[0].click();", first_choice)
        driver.implicitly_wait(5)
        result_filter = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]'
        ).text
        validate_button = driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[1]/div[2]/div[2]/div[3]/button[2]',
        )
        driver.execute_script("arguments[0].click();", validate_button)
        number_result = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]/span'
        ).text
        if len(ville) == 1:
            if all([x.lower() in result_filter.lower() for x in ville]):
                logging.info(
                    f"Le filtrage opéré sur la région de {ville[0]} a bien fonctionné, il y a {number_result} résultats".replace(
                        "[", ""
                    ).replace(
                        "]", ""
                    )
                )
        else:
            if all([x.lower() in result_filter.lower() for x in ville]):
                logging.info(
                    f"Le filtrage opéré sur les régions de {[x for x in ville]} a bien fonctionné, il y a {number_result} résultats".replace(
                        "[", ""
                    ).replace(
                        "]", ""
                    )
                )
