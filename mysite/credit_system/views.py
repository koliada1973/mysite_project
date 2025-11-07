from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from django.http import HttpResponse, request
from django.views.generic import ListView, DetailView

from credit_system.forms import CreditDetailForm
from credit_system.models import Credit


# Головна сторінка
def index(request):
    context = {
        'page_title': 'Ласкаво просимо!',
        'content_message': 'Оберіть потрібну опцію в меню'
    }
    return render(request, 'credit_system/index.html', context)


class UserCreditsView(LoginRequiredMixin, ListView):
    model = Credit
    template_name = 'credit_system/my_credits.html'
    context_object_name = 'credits'  # Як називатиметься список об'єктів у шаблоні

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Фільтруємо об'єкти Order, де поле 'user' дорівнює поточному користувачеві (self.request.user)
            return Credit.objects.filter(user=self.request.user).order_by('closed', '-start_date')

        # Якщо з якоїсь причини не автентифікований, повертаємо пустий список
        return Credit.objects.none()

# Для штатних працівників показувати список всіх кредитів
class AllCreditsView(LoginRequiredMixin, ListView):
    model = Credit
    template_name = 'credit_system/all_credits.html'
    context_object_name = 'credits'

    def get_queryset(self):
        user = self.request.user
        # Якщо користувач — менеджер або адмін, показуємо всі кредити
        if user.is_superuser or user.is_manager:
            return Credit.objects.all().order_by('closed', '-start_date')
        # Інакше повертаємо лише свої кредити (на випадок, якщо клієнт спробує вручну відкрити сторінку)
        return Credit.objects.filter(user=user)


class CreditDetailView(LoginRequiredMixin, DetailView):
    model = Credit
    template_name = 'credit_system/credit_detail.html'
    context_object_name = 'credit'

    # Обмежуємо доступ: клієнт бачить лише свої кредити
    # def get_object(self, queryset=None):
        # if self.request.user.is_authenticated:
        #     # Фільтруємо об'єкти Order, де поле 'user' дорівнює поточному користувачеві (self.request.user)
        #     return Credit.objects.filter(user=self.request.user).order_by('closed', '-start_date')
        #
        # # Якщо з якоїсь причини не автентифікований, повертаємо пустий список
        # return Credit.objects.none()
        # obj = super().get_object(queryset)
        # user = self.request.user
        # if user.is_superuser or user.is_manager or obj.user == user:
        #     return obj
        # else:
        #     raise PermissionDenied  # 🚫 клієнт не може бачити чужий кредит
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_manager:
            return Credit.objects.all()
        return Credit.objects.filter(user=user)

    def get_object(self, queryset=None):
        credit = super().get_object(queryset)
        user = self.request.user
        if not (user.is_superuser or user.is_manager or credit.user == user):
            raise PermissionDenied
        return credit

    # # Це потрібно тільки для форми
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = CreditDetailForm(instance=self.object)
    #     return context