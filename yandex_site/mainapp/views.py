from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView
from mainapp.buisness_logic.Parser import yandex_parser

from mainapp.models import ApartmentInfo


def data_view(request):
    context = {
        'is_start': yandex_parser.ParserController.is_parser_running()
    }
    print(context)
    return render(request, 'mainapp/index.html', context=context)


def start_parsing_view(request):
    yandex_parser.ParserController().start_task()
    return HttpResponseRedirect(reverse('mainapp:main'))


def stop_parsing_view(request):
    yandex_parser.ParserController().stop_task()
    return HttpResponseRedirect(reverse('mainapp:main'))


class ParserInfoTableView(ListView):
    model = ApartmentInfo
    template_name = 'mainapp/parser_view.html'


