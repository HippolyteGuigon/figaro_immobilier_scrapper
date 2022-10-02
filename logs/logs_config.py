import logging
import sys

def main():

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('/Users/hippolyteguigon/se_loger_scrapper/logs.log', mode='a')


    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

