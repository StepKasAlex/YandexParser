from django.shortcuts import render
from django.views.generic import ListView


def data_view(request):
    return render(request, 'mainapp/index.html')
