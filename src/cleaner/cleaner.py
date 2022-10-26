import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

s = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("start-maximized")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(service=s, options=options)


class Get_adress:
    """
    Class that try to compute the adress from the information given in scrapping
    get_proper_url: Goes to the proper district website on www.annuaire-mairie.fr to check
    if the adress found exists
    get_proper_street_name: Converts adress found in the description to have it matching with the website format
    check_correspondance: Checks if the street name found is in the annuary, if yes, returns it
    pipeline: Wraps all functions together to launch search"""

    def __init__(self):
        pass

    def get_proper_url(self, x):
        x = x.split("Paris")[1].split(" (")[0].split("è")[0].replace(" ", "") + "e"
        return f"https://www.annuaire-mairie.fr/rue-paris-{x}-arrondissement.html"

    def get_proper_street_name(self, x):
        x = x.lower().capitalize()
        x = x.replace(x.split(" ")[-1], x.split(" ")[-1].capitalize())
        return x

    def check_correspondance(self, x, text):
        result = "Inconnu"
        x = x.lower()
        try:
            x = "rue " + x.split("rue")[1]
        except:
            return result
        ref = re.findall(r"\w+", x)
        for length in range(2, 6):
            street_name_try = re.findall(r"\w+", x)[:length]
            street_name_try = self.get_proper_street_name(" ".join(street_name_try))
            if street_name_try and street_name_try.split(" ")[-1] not in [
                "De",
                "Du",
                "La",
                "Les",
                "Le",
                "Des",
                "-",
                "'",
                " ",
                "D'",
                "D",
                "L",
                "L'",
            ]:
                result = street_name_try
                break
        return result

    def pipeline(self, localisation, text):
        new_url = self.get_proper_url(localisation)
        driver.get(new_url)
        return self.check_correspondance(text, driver.page_source)


class DataFrame_cleaning:
    """
    Class that picks the DataFrame computed from scrapping and cleans it in order to have a usable database
    clean_price: Removes the useless signs and convert to float
    clean_surface: Removes useless signs and conversion to float
    global_cleaner: Wraps all functions together and cleans the whole dataframe
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def clean_price(self):
        try:
            self.df.price = self.df.price.apply(
                lambda x: float(x.replace("€", "").replace(" ", ""))
            ).astype(float)
        except:
            pass
        return self.df

    def clean_surface(self):
        try:

            self.df.surface = self.df.surface.apply(
                lambda x: float(x.replace("m² de surface", ""))
            )
        except:
            pass
        return self.df

    def global_cleaner(self):
        self.df = self.clean_price()
        self.df = self.clean_surface()

        if "Unnamed: 0" in self.df.columns:
            self.df.drop("Unnamed: 0", axis=1)
        return self.df
