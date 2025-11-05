from django.shortcuts import render

from django.http import HttpResponse


# Головна сторінка
def index(request):
    context = {
        'page_title': 'Ласкаво просимо!',
        'content_message': 'Оберіть потрібну опцію в меню.'
    }
    return render(request, 'credit_system/index.html', context)
