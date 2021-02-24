import os
import random
import threading
import csv
import requests
import time

from django.http import HttpResponse
from selenium import webdriver
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from mainapp.models import ApartmentInfo, Task


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class ParserController:

    def change_parser_status(self, stop=None, start=None, from_parser_stop=None) -> None:
        """Change status is_active_parser"""
        if from_parser_stop:
            Task.objects.filter(pk=1).update(status=0)
        elif int(self._is_active_task()) == 1 and stop is True:
            Task.objects.filter(pk=1).update(status=2)
        elif int(self._is_active_task()) == 0 and start is True:
            Task.objects.filter(pk=1).update(status=1)

    @staticmethod
    def _is_active_task():
        """Find out is task running"""
        return Task.objects.all().values('status')[0].get('status')

    @staticmethod
    def _get_all_params_from_db():
        """Get all necessary configs from database"""
        apartments_page_config = Task.objects.all().values('apartments_page_config')[0].get('apartments_page_config')
        apartment_page_sections_config = Task.objects.all().values('apartment_page_sections_config')[0].get('apartment_page_sections_config')
        apartment_page_config = Task.objects.all().values('apartment_page_config')[0].get('apartment_page_config')
        return apartments_page_config, apartment_page_sections_config, apartment_page_config

    @staticmethod
    def is_parser_running():
        """
        Get status of the parser
        returns: True if running, False if isn't running
        """
        status = int(Task.objects.filter(pk=1).values('status')[0].get('status'))

        if status == 1:
            return True
        elif status == 2:
            return 'try to stop'
        else:
            return False

    def start_task(self) -> (True, False):
        """Start new parsing task"""
        # Create new thread, give it name ParserThread and run
        if self.is_parser_running() is False:
            self.change_parser_status(start=True)
            task = YandexParser(configs=self._get_all_params_from_db())
            task = threading.Thread(target=task.start_parsing)
            task.start()
            return True
        else:
            return False

    def stop_task(self) -> None:
        """Stop running task by change task status in database"""
        self.change_parser_status(stop=True)


class YandexParserInfoGetter:

    def create_csv_file_from_database(self):
        """Create csv file from database information"""
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="information.csv"'

        titles = ['Цена за кв метр', 'Количество комнат', 'Общая площадь', 'Жилая площадь', 'Площадь кухни', 'Этаж', 'Балкон', 'Тип дома',
                  'Название дома', 'Отделка', 'Парковки', 'Видеонаблюдение', 'Консьерж', 'Территория',
                  'Расстояние до станции', 'Ссылка на объявление']
        writer = csv.writer(response)
        writer.writerow(titles)
        information = ApartmentInfo.objects.all()
        for info in information:
            writer.writerow([info.price, info.rooms_info, info.total_area, info.living_space, info.kitchen_space,
                             info.floor, info.is_balcony, info.house_type, info.house_name, info.finishing,
                             info.is_parking, info.is_cctv, info.is_concierge, info.fenced_area,
                             info.distance_nearest_metro, info.apartment_link])
        return response


class YandexParser:

    def __init__(self, configs):
        self.page = 'https://realty.yandex.ru/moskva/kupit/kvartira/studiya,1,2,3,4-i-bolee-komnatnie/?newFlat=YES&' \
                    'deliveryDate=FINISHED&buildingClass=BUSINESS'
        self.apartments_config = configs[0]
        self.apartment_sections = configs[1]
        self.apartment = configs[2]
        self.proxies = ['http://a4fnJNrE:PDmfB1qB@45.134.25.49:47286', 'http://a4fnJNrE:PDmfB1qB@94.158.189.19:45664',
                        'http://a4fnJNrE:PDmfB1qB@194.32.222.100:59124', 'http://a4fnJNrE:PDmfB1qB@45.81.138.122:45629']
        self.proxy_server = {}

    def set_proxy_server(self) -> None:
        """Set proxy_server"""
        new_proxy = random.choice(self.proxies)
        print("NEW PROXY", new_proxy)
        self.proxy_server['http'] = new_proxy

    @staticmethod
    def stop_parsing() -> (True, False):
        """Stop parsing"""
        if int(Task.objects.filter(pk=1).values('status')[0].get('status')) == 2:
            ParserController().change_parser_status(from_parser_stop=True)
            return True
        else:
            return False

    def start_parsing(self) -> None:
        """Start parsing yandex site"""
        try:
            while True:
                print('New round')
                self.set_proxy_server()
                current_page_html_markup = self.get_html_markup_from_page(self.page)
                if self.stop_parsing():
                    return None
                apartments_links = self.get_all_apartments_links_from_page(current_page_html_markup)
                for apartment_link in apartments_links:
                    print(apartment_link)
                    self.set_proxy_server()
                    if self.stop_parsing():
                        return None
                    apartment_info = self.get_info_from_apartment_page(apartment_link)
                    self.add_info_in_db(apartment_info)
                    time_to_wait_low = random.randint(4, 10)
                    time.sleep(time_to_wait_low)
                self.go_to_next_page()
                time_to_wait = random.randint(25, 35)
                time.sleep(time_to_wait)
        finally:
            ParserController().change_parser_status(from_parser_stop=True)

    def load_page(self, page):
        """load page"""
        r = requests.get(page, proxies=self.proxy_server)
        print('Состояние запроса - ', r)
        return r

    def close_driver(self) -> None:
        """Close driver"""
        self.driver.close()

    def get_html_markup_from_page(self, page: str) -> BeautifulSoup:
        """Get html markup from the page"""
        r = self.load_page(page)
        return BeautifulSoup(r.content, 'html.parser')

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
        all_apartment_info = {'apartment_link': page}  # dict with all apartment info

        for param, markup in self.apartment.items():
            param_name, section_name = param.split('__')
            if section_name == 'none':
                continue
            if section_name != 'stations_info':
                new_apartment_info = self.get_another_info_from_apartment_page(sections_bs_markup, section_name,
                                                                               markup, param_name)
            else:
                new_apartment_info = self.get_stations_info_from_apartment_page(sections_bs_markup, section_name,
                                                                                markup, param_name)
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
            return False

    def get_stations_info_from_apartment_page(self, sections_bs_markup: dict, section_name: str,
                                              markup: dict, param_name: str) -> dict:
        """Get info about nearest metro stations to the house"""
        tags = self.get_tags_with_text_inside(sections_bs_markup, markup, section_name)

        if tags is False:
            return {param_name: "Нет информации"}

        time_to_nearest_station = []

        for tag in tags:
            try:
                clear_time = tag.get_text(strip=True).replace(' мин.', '')
                time_to_nearest_station.append(int(clear_time))
            except (AttributeError, ValueError, Exception):
                continue

        return {param_name: min(time_to_nearest_station)} if time_to_nearest_station else {param_name: None}

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

        tags = self.get_tags_with_text_inside(sections_bs_markup, markup, section_name)

        if not tags:
            return {param_name: "Нет информации"}

        for tag in tags:
            try:
                clear_text = tag.get_text(strip=True)
            except (AttributeError, Exception):
                continue
            subs_for_search = markup.get('subs')

            for sub in subs_for_search:
                if is_sub_in_clear_text(sub, clear_text):
                    needed_text = self.edit_text_by_section(section_name, clear_text, subs_for_search, sub)
                    if param_name == 'rooms_info' and '/' in needed_text:
                        needed_text = len(needed_text.split('/'))
                    return {param_name: needed_text}

        else:
            return {param_name: "Нет информации"}

    def go_to_next_page(self) -> None:
        """Paginate to the next page"""
        now_page_num = self.page.split('&')[-1].split('=')[-1]

        try:
            next_num = int(now_page_num) + 1
        except ValueError:
            next_num = 1

        self.page = self.page + f'&page={next_num}'

    def edit_text_by_section(self, section_name: str, clear_text: str, subs_for_search: str, sub: str) -> str:
        """Get normal text from clear_text"""
        if section_name == 'tech_info':
            return self.edit_text_for_tech_info(clear_text, subs_for_search)
        elif section_name == 'detail_info':
            return self.edit_text_for_detail_info(clear_text, sub)
        elif section_name == 'building_info':
            return self.edit_text_for_building_info(clear_text, sub)
        elif section_name == 'stations_info':
            return self.edit_text_for_stations_info(clear_text, subs_for_search)
        elif section_name == 'base_info':
            return self.edit_text_for_base_info(clear_text, subs_for_search)

    @staticmethod
    def edit_text_for_tech_info(clear_text: str, subs_for_search: str):
        """Get text for tech info"""
        additional_subs_to_remove = [u'\xa0', 'м²—']
        if type(subs_for_search) == list:
            for sub in subs_for_search:
                if sub in ["этаж из", "этажиз"]:
                    for num in clear_text.split(' '):
                        try:
                            return int(num)
                        except TypeError:
                            continue
                    else:
                        return None
                clear_text = clear_text.lower().replace(sub, '')
                for ad_sub in additional_subs_to_remove:
                    clear_text = clear_text.replace(ad_sub, '')
            return clear_text.replace(',', '.').strip()
        else:
            for ad_sub in additional_subs_to_remove:
                clear_text = clear_text.replace(ad_sub, '')
            return clear_text.replace(subs_for_search, '').replace(',', '.').strip()

    @staticmethod
    def edit_text_for_detail_info(clear_text: str, sub=None):
        """Get text for detail info"""
        return clear_text.replace('—', '')

    @staticmethod
    def edit_text_for_building_info(clear_text: str, sub=None):
        """Get text for building info"""
        new_text = clear_text.replace('Дом в', '')
        remove_sub_start_idx = new_text.find('(по данным Яндекса)')
        if remove_sub_start_idx != -1:
            return new_text.replace(new_text[remove_sub_start_idx:], '').strip()
        else:
            return new_text.strip()

    @staticmethod
    def edit_text_for_stations_info(clear_text: str, subs_for_search=None):
        """Get text for building info"""
        return clear_text

    @staticmethod
    def edit_text_for_base_info(clear_text: str, subs_for_search=None):
        """Get text for base info"""
        for sub in subs_for_search:
            clear_text = clear_text.replace(sub, '')
        return clear_text.strip().replace(' ', '').replace(u'\xa0', '')

    @staticmethod
    def add_info_in_db(apartments_info: dict) -> None:
        """Add into about apartment in database"""
        if not ApartmentInfo.objects.filter(apartment_link=apartments_info.get('apartment_link')):
            new_info = ApartmentInfo(price=apartments_info.get('price'),
                                     rooms_info=apartments_info.get('rooms_info'),
                                     total_area=apartments_info.get('total_area'),
                                     living_space=apartments_info.get('living_space'),
                                     kitchen_space=apartments_info.get('kitchen_space'),
                                     floor=apartments_info.get('floor'),
                                     is_balcony=apartments_info.get('is_balcony'),
                                     house_type=apartments_info.get('house_type'),
                                     house_name=apartments_info.get('house_name'),
                                     finishing=apartments_info.get('finishing'),
                                     is_parking=apartments_info.get('is_parking'),
                                     is_cctv=apartments_info.get('is_cctv'),
                                     is_concierge=apartments_info.get('is_concierge'),
                                     fenced_area=apartments_info.get('fenced_area'),
                                     distance_nearest_metro=apartments_info.get('distance_nearest_metro'),
                                     apartment_link=apartments_info.get('apartment_link'))
            new_info.save()


if __name__ == '__main__':
    test = YandexParser(1)
    test.start_parsing()