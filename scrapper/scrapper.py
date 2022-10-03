from selenium import webdriver
import warnings

warnings.filterwarnings("ignore")
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("start-maximized")
options.add_argument("--log-level=3")
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys
from logs.logs_config import main
import logging

url = "https://immobilier.lefigaro.fr/"
s = Service(ChromeDriverManager(log_level=3).install())
driver = webdriver.Chrome(service=s, options=options)
driver.maximize_window()
driver.get(url)


class Scrapper:
    def __init__(self):
        pass

    def connect(self):

        main()

        # Trouver un moyen plus élégant de vérifier la connexion
        if "Saisissez une ou plusieurs villes" in driver.page_source:
            logging.info("La connexion à la page d'acceuil a bien réussie")

    def search_type(self, choice):
        self.connect()
        choice = str(choice).lower()
        assert choice in [
            "acheter",
            "louer",
        ], "L'utilisateur doit choisir entre acheter et louer un bien"
        logging.info(f"L'utilisateur a choisi l'otion {choice}")

        if choice == "acheter":
            element = driver.find_element_by_xpath(
                '//*[@id="homepage-v2"]/section[1]/div/div[1]/button[1]'
            )
            driver.execute_script("arguments[0].click();", element)
        else:
            element = driver.find_element_by_xpath(
                '//*[@id="homepage-v2"]/section[1]/div/div[1]/button[2]'
            )
            driver.execute_script("arguments[0].click();", element)

        search_button = driver.find_element_by_xpath(
            '//*[@id="homepage-v2"]/section[1]/div/button[2]'
        )
        driver.execute_script("arguments[0].click();", search_button)
        driver.implicitly_wait(3)
        if "Créer une alerte" in driver.page_source:
            logging.info("La recherche a bien aboutie")
        else:
            logging.info("La recherche n'a pas aboutie")
