import os
import psycopg2
import threading
import json
import time

from selenium import webdriver
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# from mainapp.models import ApartmentInfo, Task


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
        # self.apartments_config = configs[0]
        # self.apartment_sections = configs[1]
        # self.apartment = configs[2]
        self.apartments_config = json.load(open('json_page_with_apartments.json', 'r', encoding='utf-8'))
        self.apartment_sections = json.load(open('json_apartment_page_sections.json', 'r', encoding='utf-8'))
        self.apartment = json.load(open('json_apartment_page.json', 'r', encoding='utf-8'))
        self.driver = self.start_driver()

    def start_driver(self) -> webdriver.Chrome:
        """Start selenium webdriver"""
        options = self.set_driver_options()
        return webdriver.Chrome(executable_path=os.getenv('DRIVER_PATH'), options=options)

    def set_driver_options(self):
        """Set options for selenium webdriver"""
        return None

    def start_parsing(self):
        """Start parsing yandex site"""
        try:
            current_page_html_markup = self.get_html_markup_from_page(self.page)
            apartments = []
            while True:
                apartments_links = self.get_all_apartments_links_from_page(current_page_html_markup)
                for apartment_link in apartments_links:
                    apartment_info = self.get_info_from_apartment_page(apartment_link)
                    apartments.append(apartment_info)
                print(apartments)
                break
        finally:
            self.close_driver()

    def load_page(self, page) -> None:
        """load page"""
        self.driver.get(page)

    def close_driver(self) -> None:
        """Close driver"""
        self.driver.close()

    def get_html_markup_from_page(self, page: str) -> BeautifulSoup:
        """Get html markup from the page"""
        self.load_page(page)
        time.sleep(7)
        return BeautifulSoup(self.driver.page_source, 'html.parser')

    def get_all_apartments_links_from_page(self, current_page_html_markup) -> list:
        """Get all apartments links from current page"""
        apartments_markup = self.apartments_config.get('apartment_ad')
        apartments = current_page_html_markup.find_all(apartments_markup.get('tag'), apartments_markup.get('tag_attrs'))
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
            if section_name == 'none':
                continue
            if section_name != 'stations_info':
                new_apartment_info = self.get_another_info_from_apartment_page(sections_bs_markup, section_name,
                                                                               markup, param_name)
                print(new_apartment_info)
            else:
                new_apartment_info = self.get_stations_info_from_apartment_page(sections_bs_markup, section_name,
                                                                                markup, param_name)
                print(new_apartment_info)
            all_apartment_info.update(new_apartment_info)

        return all_apartment_info

    @staticmethod
    def get_tags_with_text_inside(sections_bs_markup: dict, markup: dict, section_name: str) -> list:
        """Get all tags with text that we need"""
        try:
            tag = markup.get('tag')
            tag_attrs = markup.get('tag_attrs')
            if tag_attrs == 'NULL':
                tag_attrs = None
            return sections_bs_markup.get(section_name).find_all(tag, tag_attrs)
        except AttributeError:
            print('ВОт тут ошибка')
            return False

    def get_stations_info_from_apartment_page(self, sections_bs_markup: dict, section_name: str,
                                              markup: dict, param_name: str) -> dict:
        """Get info about nearest metro stations to the house"""
        tags = self.get_tags_with_text_inside(sections_bs_markup, markup, section_name)

        if tags is False:
            return {param_name: 'NULL'}

        time_to_nearest_station = []

        for tag in tags:
            try:
                clear_time = tag.get_text(strip=True).replace(' мин.', '')
                time_to_nearest_station.append(int(clear_time))
            except (AttributeError, ValueError, Exception):
                continue

        return {param_name: min(time_to_nearest_station)} if time_to_nearest_station else {param_name: 'NULL'}

    def get_another_info_from_apartment_page(self, sections_bs_markup: dict, section_name: str,
                                             markup: dict, param_name: str) -> dict:
        """Get info about apartment exclude nearest stations to the house"""
        def is_sub_in_clear_text(sub: str, clear_text: str) -> (True, False):
            """Compare substring that we are trying to find with text that we got from tag"""
            if sub.lower() in clear_text or sub.lower() == clear_text.lower():
                return True
            elif sub.capitalize() in clear_text or sub.capitalize() == clear_text.capitalize():
                return True
            else:
                return False

        needed_text = None
        tags = self.get_tags_with_text_inside(sections_bs_markup, markup, section_name)

        if not tags:
            return {param_name: 'NULL'}

        for tag in tags:
            try:
                clear_text = tag.get_text(strip=True)
            except (AttributeError, Exception):
                continue
            subs_for_search = markup.get('subs')

            print(clear_text, subs_for_search)

            if type(subs_for_search) == list:
                for sub in subs_for_search:
                    if is_sub_in_clear_text(sub, clear_text):
                        needed_text = self.edit_text_by_section(section_name, clear_text, subs_for_search)
                        print('ТО ЧТО НУЖНО', needed_text)
                        return {param_name: needed_text}
            elif type(subs_for_search) == str:
                if is_sub_in_clear_text(subs_for_search, clear_text):
                    needed_text = self.edit_text_by_section(section_name, clear_text, subs_for_search)
                    return {param_name: needed_text}

        else:
            return {param_name: 'NULL'}

    def go_to_next_page(self, page: str, page_num: str) -> str:
        """Paginate to the next page"""
        now_page_num = page.split('&')[-1].split('=')[-1]

        if now_page_num:
            next_num = int(now_page_num) + 1
        else:
            next_num = 1

        return self.page + f'&page={next_num}'

    def edit_text_by_section(self, section_name: str, clear_text: str, subs_for_search: str) -> str:
        """Get normal text from clear_text"""
        if section_name == 'tech_info':
            return self.edit_text_for_tech_info(clear_text, subs_for_search)
        elif section_name == 'detail_info':
            return self.edit_text_for_detail_info(clear_text, subs_for_search)
        elif section_name == 'building_info':
            return self.edit_text_for_building_info(clear_text, subs_for_search)
        elif section_name == 'stations_info':
            return self.edit_text_for_stations_info(clear_text, subs_for_search)

    @staticmethod
    def edit_text_for_tech_info(clear_text: str, subs_for_search: str):
        """Get text for tech info"""
        non_break_space = u'\xa0'
        if type(subs_for_search) == list:
            for sub in subs_for_search:
                if sub in ["этаж из", "этажиз"]:
                    for num in clear_text.split(' '):
                        try:
                            return int(num)
                        except TypeError:
                            continue
                    else:
                        return 'NULL'
                clear_text = clear_text.lower().replace(sub, '').replace('м²—', '')
            return clear_text.strip().replace(non_break_space, '')
        else:
            return clear_text.lower().replace(subs_for_search, '').strip().replace(non_break_space, '').replace('м²—', '')

    @staticmethod
    def edit_text_for_detail_info(clear_text: str, subs_for_search=None):
        """Get text for detail info"""
        return clear_text

    @staticmethod
    def edit_text_for_building_info(clear_text: str, subs_for_search=None):
        """Get text for building info"""
        return clear_text

    @staticmethod
    def edit_text_for_stations_info(clear_text: str, subs_for_search=None):
        """Get text for building info"""
        return clear_text


if __name__ == '__main__':
    test = YandexParser(1)
    test.start_parsing()