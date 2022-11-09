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


if __name__ == "__main__":
    unittest.main()
