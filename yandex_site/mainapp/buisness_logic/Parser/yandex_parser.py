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

    def _change_parser_status(self) -> None:
        """Change status is_active_parser"""
        if int(self.is_active_task) == 1:
            Task.objects.filter(pk=1).update(status=0)
        else:
            Task.objects.filter(pk=1).update(status=1)

    @staticmethod
    def _is_active_task():
        """Find out is task running"""
        return Task.objects.all().values('status')[0].get('status')

    @staticmethod
    def _get_all_params_from_db():
        """Get all necessary configs from database"""
        apartments_page_config = Task.objects.all().values('main_page_config')[0].get('apartments_page_config')
        apartment_page_sections_config = Task.objects.all().values('apartments_page_config')[0].get('apartment_page_sections_config')
        apartment_page_config = Task.objects.all().values('apartment_page_config').get('apartment_page_config')
        return apartments_page_config, apartment_page_sections_config, apartment_page_config

    def start_task(self) -> None:
        """Start new parsing task"""
        # Create new thread, give it name ParserThread and run
        task = threading.Thread(target=YandexParser, args=(self._get_all_params_from_db(), ))
        task.start()

    def stop_task(self) -> None:
        """Stop running task by change task status in database"""
        self._change_parser_status()


class YandexParser:

    def __init__(self, configs):
        self.page = 'https://realty.yandex.ru/moskva/kupit/kvartira/studiya,1,2,3,4-i-bolee-komnatnie/?newFlat=YES&' \
                    'deliveryDate=FINISHED&buildingClass=BUSINESS'
        self.apartments_config = configs[0]
        self.apartment_sections = configs[1]
        self.apartment = configs[2]
        self.driver = self.start_driver()

    @staticmethod
    def start_driver() -> webdriver.Chrome:
        """Start selenium webdriver"""
        return webdriver.Chrome(executable_path=os.getenv('DRIVER_PATH'))

    def set_driver_options(self):
        """Set options for selenium webdriver"""
        pass

    def load_page(self, page) -> None:
        """load page"""
        self.driver.get(page)

    def get_html_markup_from_page(self) -> BeautifulSoup:
        """Get html markup from the page"""
        return BeautifulSoup(self.driver.page_source, 'html.parser')

    def get_all_apartments_links_from_page(self) -> list:
        """Get all apartments links from current page"""
        current_page_html_markup = self.get_html_markup_from_page()
        apartments = current_page_html_markup.find_all('div', {'class': 'OffersSerpItem__generalInfo'})
        apartments_links = []

        for apartment in apartments:
            link = f"https://realty.yandex.ru/{apartment.find('a').get('href')}"
            apartments_links.append(link)

        return apartments_links

    def get_apartments_main_section_html_markup(self, page: str) -> dict:
        """
        Get all necessary sections from apartment page
        You can find tag SECTION in html markup in the reality.yandex site
        """
        sections_bs_markup = {}  # sections with needed info bs4 elements
        apart_page_html_markup = self.get_html_markup_from_page(page)

        # get all main sections with information
        for section in self.apartment_sections.keys():
            section_config = self.apartment_sections.get(section)
            sections_bs_markup.update({
                section: apart_page_html_markup.find(section_config.get('tag'), section_config.get('tag_attrs'))
            })

        return sections_bs_markup

    def get_info_from_apartment_page(self, page) -> dict:
        """Get info about apartment"""
        sections_bs_markup = self.get_apartments_main_section_html_markup(page)
        all_apartment_info = {}  # dict with all apartment info

        for param, markup in self.apartment.items():
            param_name, section_name = param.split('__')
            tags = sections_bs_markup.get(section_name).find_all(markup.get('tag'), markup.get('tag_attrs'))
            for tag in tags:
                try:
                    clear_text = tag.get_text(strip=True)
                except (AttributeError, Exception):
                    continue
                subs_for_search = markup.get('subs')
                if clear_text == subs_for_search or clear_text in subs_for_search:
                    all_apartment_info.update({
                        param_name: clear_text
                    })
            else:
                all_apartment_info.update({
                    param_name: 'NULL'
                })

        return all_apartment_info

    def go_to_next_page(self, page: str, page_num: str) -> str:
        """Paginate to the next page"""
        now_page_num = page.split('&')[-1].split('=')[-1]

        if now_page_num:
            next_num = int(now_page_num) + 1
        else:
            next_num = 1

        return self.page + f'&page={next_num}'


test = ParserController()
test.stop_task()