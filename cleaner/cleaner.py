import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
s = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("start-maximized")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(service=s, options=options)

class Get_adress:

    def __init__(self):
        pass

    def get_proper_url(self,x):
        x=x.split("Paris")[1].split(" (")[0].split("è")[0].replace(" ","")+"e"
        return f'https://www.annuaire-mairie.fr/rue-paris-{x}-arrondissement.html'

    def get_proper_street_name(self,x):
        x=x.lower().capitalize()
        x=x.replace(x.split(" ")[-1],x.split(" ")[-1].capitalize())
        return x


    def check_correspondance(self,x,text):
        result="Inconnu"
        x=x.lower()
        try:
            x="rue "+x.split("rue")[1]
        except:
            return result
        for length in range(2,6):
            street_name_try=re.findall(r'\w+', x)[:length]
            street_name_try=self.get_proper_street_name(" ".join(street_name_try))
            if street_name_try and street_name_try.split(" ")[-1] not in ["De", "Du", "La", "Les", "Le", "Des", "-"]:
                result=street_name_try
                break
        return result

    def pipeline(self,localisation,text):
        new_url=self.get_proper_url(localisation)
        driver.get(new_url)
        return self.check_correspondance(text,driver.page_source)
        