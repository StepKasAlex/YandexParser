

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
        self.driver = None
        pass

    def start_driver(self):
        """initialize selenium webdriver"""
        pass

    def set_driver_options(self):
        """Set necessary driver options"""
        pass

    def load_page(self, page):
        """Load """
        pass

    def get_html_markup_from_page(self):



class YandexParser:

    def __init__(self):
        pass
