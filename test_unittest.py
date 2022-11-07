import unittest
from src.filter.filter import *
from src.scrapper.scrapper import *

filter=Filtering()

class Test(unittest.TestCase):
    def test_connexion(self):
        self.assertEqual(filter.check_connect(), "La connexion à la page d'acceuil a bien réussie")

    def test_search_result(self):
        self.assertEqual(filter.search_type("louer"),"La recherche a bien aboutie")

if __name__ == '__main__':
    unittest.main()