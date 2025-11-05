from django.shortcuts import render

from django.http import HttpResponse


# Головна сторінка
def index(request):
    """Відображає головну сторінку сайту з боковим меню."""
    context = {
        'page_title': 'Ласкаво просимо!',
        'content_message': 'Оберіть потрібну опцію в меню.',
    }

    # Використовуємо наш базовий шаблон
    return render(request, 'credit_system/base.html', context)
