from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from django.http import HttpResponse
from django.views.generic import ListView

from credit_system.models import Credit


# Головна сторінка
def index(request):
    context = {
        'page_title': 'Ласкаво просимо!',
        'content_message': 'Оберіть потрібну опцію в меню.'
    }
    return render(request, 'credit_system/index.html', context)


class UserCreditsView(LoginRequiredMixin, ListView):
    model = Credit
    template_name = 'credit_system/my_credits.html'
    context_object_name = 'credits'  # Як називатиметься список об'єктів у шаблоні

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Фільтруємо об'єкти Order, де поле 'user' дорівнює поточному користувачеві (self.request.user)
            return Credit.objects.filter(user=self.request.user).order_by('-start_date')

        # Якщо з якоїсь причини не автентифікований, повертаємо пустий список
        return Credit.objects.none()