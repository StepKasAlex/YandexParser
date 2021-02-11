import os
import psycopg2
import threading

from selenium import webdriver
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from mainapp.models import ApartmentInfo, Task


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class ParserController:

    def change_parser_status(self) -> None:
        """Change status is_active_parser"""
        if int(self.is_active_task) == 1:
            Task.objects.filter(pk=1).update(status=0)
        else:
            Task.objects.filter(pk=1).update(status=1)

    @staticmethod
    def is_active_task():
        """Find out is task running"""
        return Task.objects.all().values('status')[0].get('status')

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
        self.apartment_parameters = apartment_parameters  # HTML markup for main page
        self.apartments_page_html_markup = apartments_page_html_markup  # HTML markup for page with apartments
        self.apartment_page_html_markup = apartment_page_html_markup  # HTML markup for apartment page
        self.driver = self.start_driver()
        pass

    def start_driver(self):
        """
        initialize selenium webdriver
        return webdriver copy
        """
        options = self.set_driver_options()
        return webdriver.Chrome(os.getenv('DRIVER_PATH', options))

    def set_driver_options(self):
        """Set necessary driver options"""
        return False

    def load_page(self, page):
        """Load page"""
        self.driver.get(page)
        return None

    def get_html_markup_from_page(self):
        """Get html markup from the page"""
        return BeautifulSoup(self.driver.page_source, 'html.parser')

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
