from django.contrib import admin
from django.urls import path
import mainapp.views as mainapp

app_name = 'mainapp'


urlpatterns = [
    path('', mainapp.data_view, name='main'),
    path('parser_start/', mainapp.start_parsing_view, name='parser_start'),
    path('parser_stop/', mainapp.stop_parsing_view, name='stop_parser'),
    path('parserview/', mainapp.ParserInfoTableView.as_view(), name='parser_view')
]