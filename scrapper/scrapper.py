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
from pathlib import Path
from selenium.webdriver.common.by import By
from typing import List
from time import sleep
import json
import os

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

        search_engine_button=driver.find_element(
                "xpath",
                "//*[@id='search-engine']/div/div[1]/div[2]/div[2]/div[2]/div/div/input",
            )
        for choice_region in ville:
            search_engine_button.send_keys(choice_region)
            sleep(3)
            search_engine_button.send_keys(" ")
            sleep(2)
            first_choice = driver.find_element(
                "xpath",
                "//*[@id='search-engine']/div/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/div/div[1]/div/div[1]",
            )
            
            driver.execute_script("arguments[0].click();", first_choice)
        sleep(3)
        result_filter = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]'
        ).text
        filtered_cities=result_filter.split("à")[1].split(":")[0]
        validate_button = driver.find_element(
            "xpath",
            '//*[@id="search-engine"]/div/div[1]/div[2]/div[2]/div[3]/button[2]',
        )
        driver.execute_script("arguments[0].click();", validate_button)
        sleep(3)
        number_result = driver.find_element(
            "xpath", '//*[@id="bloc-list-classifieds"]/span'
        ).text
        
        logging.warning(f"Le filtrage a bien été opéré sur {filtered_cities}, il y a {number_result} annonces")

    def filter_price(self, price_min:int,price_max:int):

        budget_button = driver.find_element("xpath",'//*[@id="search-engine"]/div/div[2]/div[2]/div')
        driver.execute_script("arguments[0].click();", budget_button)
        sleep(2)

        driver.find_element("xpath",'//*[@id="search-engine"]/div/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/input').send_keys(price_min)
        driver.find_element("xpath",'//*[@id="search-engine"]/div/div[2]/div[2]/div[2]/div[2]/div[1]/div[2]/input').send_keys(price_max)

        validation_button=driver.find_element("xpath",'//*[@id="search-engine"]/div/div[2]/div[2]/div[2]/div[3]/button[2]')
        driver.execute_script("arguments[0].click();", validation_button)
        sleep(3)
        number_result=driver.find_element("xpath",'//*[@id="bloc-list-classifieds"]/span').text
        logging.info(f"L'utilisateur a filtré les prix entre {price_min}€ et {price_max}€, il y a {number_result} annonces")
    
    def filter_surface(self, surface_min:int,surface_max:int):
        criterion_button = driver.find_element("xpath",'//*[@id="search-engine"]/div/div[2]/div[3]/div[1]')
        driver.execute_script("arguments[0].click();", criterion_button)
        sleep(2)

        driver.find_element("xpath",'//*[@id="search-engine"]/div/div[2]/div[3]/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/div[1]/input').send_keys(surface_min)
        driver.find_element("xpath",'//*[@id="search-engine"]/div/div[2]/div[3]/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/div[2]/input').send_keys(surface_max)

        validation_button=driver.find_element("xpath",'//*[@id="search-engine"]/div/div[2]/div[3]/div[2]/div[3]/button[2]')
        driver.execute_script("arguments[0].click();", validation_button)
        sleep(3)
        number_result=driver.find_element("xpath",'//*[@id="bloc-list-classifieds"]/span').text
        logging.info(f"L'utilisateur a filtré les prix entre {surface_min}m2 et {surface_max}m2, il y a {number_result} annonces")


    def global_filtering(self,ville: List,price_min:int,price_max:int,surface_min:int,surface_max:int):
        self.filter_search(ville)
        self.filter_surface(surface_min,surface_max)
        self.filter_price(price_min,price_max)

    def get_links(self):
        elems=[x.get_attribute("href") for x in driver.find_elements("xpath","//a[@href]") if "/annonces/annonce" in x.get_attribute("href")]
        while True:
            try:
                next_button=driver.find_element("xpath",'//*[@id="listAnnoncesBloc"]/section/div[40]/a[2]/div/span')
                driver.execute_script("arguments[0].click();", next_button)
                sleep(5)
                new_elems=[x.get_attribute("href") for x in driver.find_elements("xpath","//a[@href]") if "/annonces/annonce" in x.get_attribute("href")]
                elems+=new_elems
            except:
                break
        json_path="/Users/hippodouche/se_loger_scrapping/figaro_immobilier_scrapper/data"
        json_list=json.dumps(elems) 

        with open(os.path.join(json_path, 'links.json'), 'w') as f:
            json.dump(elems, f)
