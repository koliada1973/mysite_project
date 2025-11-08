from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpResponse, request
from django.views import View
from django.views.generic import ListView, DetailView

# from credit_system.forms import CreditDetailForm
from credit_system.forms import AddPaymentForm
from credit_system.models import Credit, Payment
from credit_system.services import process_payment


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



class AddPaymentView(LoginRequiredMixin, View):
    template_name = 'credit_system/add_payment.html'

    def get(self, request, credit_id):
        credit = get_object_or_404(Credit, pk=credit_id)
        credit.refresh_from_db()  # на випадок, якщо дані не актуальні

        # Додавати платіж могуть тільки штатні працівники
        if not (request.user.is_superuser or request.user.is_manager):
            raise PermissionDenied

        form = AddPaymentForm()
        return render(request, self.template_name, {'form': form, 'credit': credit})

    def post(self, request, credit_id):
        credit = get_object_or_404(Credit, pk=credit_id)

        last_pay_date = credit.last_pay_date
        print(">>> DEBUG last_pay_date:", last_pay_date)
        # last_pay_date = last_pay_date.date()
        # print(">>> DEBUG last_pay_date.date():", last_pay_date)

        if not (request.user.is_superuser or request.user.is_manager):
            raise PermissionDenied

        form = AddPaymentForm(request.POST)
        if form.is_valid():
            pay = form.cleaned_data['pay']
            date_pay = form.cleaned_data['date_pay']

            delta_days = (date_pay - last_pay_date).days

            try:
                result = process_payment(credit, pay, date_pay, delta_days)
                print(result)  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, self.template_name, {'form': form, 'credit': credit})

            # Зберігаємо сам платіж
            Payment.objects.create(credit=credit, pay=pay, date_pay=date_pay, dolg_percent=result["dolg_percent"], ostatok=result["ostatok"], pog_credit=result["pog_credit"], pog_summa_percent=result["pog_summa_percent"], summa_percent=result["summa_percent"], ost_payment=result["ost_payment"])

            # Повідомлення
            messages.success(request, f"Платіж {pay:.2f} грн додано ({delta_days} днів, нараховано {result['summa_percent']:.2f} грн відсотків).")
            for line in result['log']:
                messages.info(request, line)

            return redirect('credit_detail', pk=credit.id)

        return render(request, self.template_name, {'form': form, 'credit': credit})


class PaymentsView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'credit_system/credit_payments.html'
    context_object_name = 'payments'

    def get_queryset(self):
        credit_id = self.kwargs.get('credit_id')

        if not credit_id:
            return self.model.objects.none()

        queryset = self.model.objects.filter(credit__id=credit_id)

        # Перевіряємо, чи користувач не є суперкористувачем (якщо це так, він бачить усе)
        if not (self.request.user.is_superuser or self.request.user.is_manager):
            queryset = queryset.filter(credit__user=self.request.user)

        return queryset.order_by('date_pay')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        credit_id = self.kwargs.get('credit_id')

        if credit_id:
            filters = {'pk': credit_id}

            if not (self.request.user.is_superuser or self.request.user.is_manager):
                filters['user'] = self.request.user

            context['credit'] = get_object_or_404(Credit, **filters)

        return context
