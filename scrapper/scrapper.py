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


class Scrapper:
    def __init__(self):
        pass
    def connect(self):
        url = "https://immobilier.lefigaro.fr/"
        s = Service(ChromeDriverManager(log_level=3).install())
        driver = webdriver.Chrome(service=s, options=options)
        driver.maximize_window()
        driver.get(url)
        main()

        # Trouver un moyen plus élégant de vérifier la connexion
        if (
            driver.find_element_by_xpath(
                "/html/body/div[1]/div/div/main/section[1]/div/div[2]/div/input"
            ).get_attribute("placeholder")
            == "Saisissez une ou plusieurs villes"
        ):
            logging.warning("La connexion a bien réussie")
