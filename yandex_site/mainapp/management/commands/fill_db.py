import json
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import BaseCommand

from mainapp.models import Task, ApartmentInfo


JSON_PATH = os.path.join(settings.BASE_DIR, 'mainapp/json')


def load_json_data(file_name):
    with open(os.path.join(JSON_PATH, file_name + '.json'), encoding='utf-8') as json_file:
        return json.load(json_file)


class Command(BaseCommand):

    def handle(self, *args, **options):
        apartments = load_json_data('json_page_with_apartments')
        apartment_sections = load_json_data('json_apartment_page_sections')
        apartment = load_json_data('json_apartment_page')

        # Task.objects.all().delete()

        Task(main_page_config={}, apartments_page_config=apartments, apartment_page_sections_config=apartment_sections,
             apartment_page_config=apartment, status=0).save()