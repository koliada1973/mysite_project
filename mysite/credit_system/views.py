from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return HttpResponse("Мій проект mysite — застосунок credit_system!")
