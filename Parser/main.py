import os

from selenium import webdriver
from dotenv import load_dotenv
from bs4 import BeautifulSoup


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class ParserController:

    def __init__(self):
        self.sql = None  # instance of the class for interacting with the database
        self.is_active_parser = False

    def find_out_task(self):
        """Try to find new task for parsing the site"""
        pass

    def change_parser_status(self):
        """Change status is_active_parser"""
        pass

    def get_all_params_from_db(self):
        """Get all necessary parameters from database"""
        pass

    def start_task(self):
        """Start new parsing task"""
        pass

    def stop_task(self):
        """Stop running task"""
        pass


class SiteInteraction:

    def __init__(self, apartment_parameters, main_page_html_markup, apartments_page_html_markup,
                 apartment_page_html_markup):
        self.apartment_parameters = apartment_parameters  # json/dict that
        self.main_page_html_markup = main_page_html_markup  # HTML markup for main page
        self.apartments_page_html_markup = apartments_page_html_markup  # HTML markup for page with apartments
        self.apartment_page_html_markup = apartment_page_html_markup  # HTML markup for apartment page
        self.driver = self.start_driver()
        pass

    def start_driver(self):
        """initialize selenium webdriver"""
        options = self.set_driver_options()
        return webdriver.Chrome(os.getenv('DRIVER_PATH', options))

    def set_driver_options(self):
        """Set necessary driver options"""
        return False

    def load_page(self, page):
        """Load page"""
        pass

    def get_html_markup_from_page(self):
        """Get html markup from the page"""
        pass

    def set_city(self):
        """Set necessary city"""
        pass

    def set_all_params(self):
        """Set all parameters on the site"""
        pass

    def confirm_set_params(self):
        """Confirm all params"""
        pass

    def get_all_apartments_on_page(self):
        """
        Get all apartments on the page
        :return list of links for apartments
        """
        pass


class YandexParser:

    def __init__(self):
        pass
