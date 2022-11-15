import unittest
import sys
import os
import yaml
from yaml.loader import SafeLoader

current_path = os.getcwd()
with open(os.path.join(current_path, "configs/filter_search.yml"), "r") as f:
    data_search = list(yaml.load_all(f, Loader=SafeLoader))[0]

current_dir = os.getcwd()
sys.path.append(os.path.join(current_dir, "src/filter"))
sys.path.append(os.path.join(current_dir, "src/model"))
from filter import *
from src.scrapper.scrapper import *
from model import *


df_test = pd.read_csv(os.path.join(current_path, "unittest/df_Paris.csv"))
model = Clustering_Pipeline(df_test)
filter = Filtering()


class Test(unittest.TestCase):

    def test_connexion(self):
        self.assertEqual(
            filter.check_connect(),
            "La connexion à la page d'acceuil a bien réussie",
        )

    def test_search_result(self):
        self.assertEqual(filter.search_type("louer"), "La recherche a bien aboutie")

    def test_filter_result_global(self):
        url = "https://immobilier.lefigaro.fr/"
        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s, options=options)
        driver.maximize_window()
        driver.get(url)
        filter.skip_error_page()
        filter.accept_cookie()
        filter.check_connect()
        filter.search_type(data_search["choix"])

        result_filter_ville = filter.filter_search(data_search["cities"])
        result_filter_surface = filter.filter_surface(data_search["surface_min"], data_search["surface_max"])
        result_filter_price = filter.filter_price(data_search["price_min"], data_search["price_max"])

        if "Le filtrage a bien été opéré" in result_filter_ville:
            bool_result_ville = True
        else:
            bool_result_ville = False

        if "L'utilisateur a filtré les prix entre" in result_filter_price:
            bool_result_price = True
        else:
            bool_result_price = False

        if "L'utilisateur a filtré la surface entre" in result_filter_surface:
            bool_result_surface = True
        else:
            bool_result_surface = False

        self.assertTrue(
            all([bool_result_ville, bool_result_price, bool_result_surface])
        )

    def test_filter_model(self):
        try:
            model.full_pipeline()
        except:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
