import unittest
import sys
import os

current_dir = os.getcwd()
sys.path.append(os.path.join(current_dir, "src/filter"))
from filter import *
from src.scrapper.scrapper import *

filter = Filtering()


class Test(unittest.TestCase):
    def test_connexion(self):
        self.assertEqual(
            filter.check_connect("louer"),
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
        filter.search_type("louer")

        result_filter_ville=filter.filter_search(["Paris","Lyon 12"])
        result_filter_surface=filter.filter_surface(10, 50)
        result_filter_price=filter.filter_price(10, 3000)

        if "Le filtrage a bien été opéré" in result_filter_ville:
            bool_result_ville=True
        else:
            bool_result_ville=False

        if "L'utilisateur a filtré les prix entre" in result_filter_price:
            bool_result_price=True
        else:
            bool_result_price=False

        if "L'utilisateur a filtré la surface entre" in result_filter_surface:
            bool_result_surface=True
        else:
            bool_result_surface=False

        self.assertTrue(all([bool_result_ville,bool_result_price,bool_result_surface]))

if __name__ == "__main__":
    unittest.main()
