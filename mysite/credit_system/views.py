from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpResponse, request, Http404
from django.views import View
from django.views.generic import ListView, DetailView


from credit_system.forms import AddPaymentForm, ClientDetailForm, AddCreditForm
from credit_system.models import Credit, Payment, CustomUser
from credit_system.plan_pay import rozrahunok_plan_pay
from credit_system.services import process_payment



# Головна сторінка
def index(request):
    context = {
        'page_title': 'Ласкаво просимо!',
        'content_message': 'Оберіть потрібну опцію в меню'
    }
    return render(request, 'credit_system/index.html', context)



# Для клієнтів показуємо список їх кредитів
class UserCreditsView(LoginRequiredMixin, ListView):
    model = Credit
    template_name = 'credit_system/my_credits.html'
    context_object_name = 'credits'  # Як називатиметься список об'єктів у шаблоні

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Фільтруємо об'єкти Credit, де поле 'user' дорівнює поточному користувачеві (self.request.user)
            return Credit.objects.filter(user=self.request.user).order_by('closed', '-start_date')

        # Якщо з якоїсь причини не автентифікований, повертаємо пустий список
        return Credit.objects.none()



# Для штатних працівників показуємо список всіх кредитів
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



# Для штатних працівників показуємо список всіх клієнтів
class AllClientsView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'credit_system/all_clients.html'
    context_object_name = 'clients'

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_manager:
            return CustomUser.objects.filter(role='client').order_by('last_name')
        else:
            raise Http404("У вас немає дозволу на перегляд списку клієнтів.")



# Деталі кредиту
class CreditDetailView(LoginRequiredMixin, DetailView):
    model = Credit
    template_name = 'credit_system/credit_detail.html'
    context_object_name = 'credit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Отримуємо поточний об'єкт кредиту
        current_credit = context['credit']

        # 2. Отримуємо всі платежі, пов'язані з цим кредитом
        queryset = Payment.objects.filter(credit=current_credit).order_by('date_pay')

        # 3. Застосовуємо логіку безпеки, щоб користувач не бачив чужі платежі (якщо потрібно)
        if not (self.request.user.is_superuser or self.request.user.is_manager):
            queryset = queryset.filter(credit__user=self.request.user)

        # 4. Додаємо список платежів до контексту
        context['payments'] = queryset

        return context



# Деталі клієнта
class ClientDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'credit_system/client_detail.html'
    context_object_name = 'client'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        client_object = get_object_or_404(self.model, pk=pk)

        if not (self.request.user.is_superuser or self.request.user.is_manager):
            if client_object != self.request.user:
                raise Http404("Ви не маєте доступу до цього профілю клієнта.")

        return client_object



# Додавання платежу
class AddPaymentView(LoginRequiredMixin, View):
    template_name = 'credit_system/add_payment.html'

    def get(self, request, credit_id):
        credit = get_object_or_404(Credit, pk=credit_id)
        credit.refresh_from_db()

        if not (request.user.is_superuser or request.user.is_manager):
            raise PermissionDenied  # <--- Зверніть увагу: ми кидаємо виняток, не повертаємо None

        # Отримання даних для форми
        last_pay_date = credit.last_pay_date
        initial_data = {'last_pay_date': last_pay_date}

        # Створення форми з початковими даними
        form = AddPaymentForm(initial=initial_data)

        return render(request, self.template_name, {'form': form, 'credit': credit})

    def post(self, request, credit_id):
        credit = get_object_or_404(Credit, pk=credit_id)

        last_pay_date = credit.last_pay_date

        if not (request.user.is_superuser or request.user.is_manager):
            raise PermissionDenied

        initial_data = {'last_pay_date': last_pay_date}
        form = AddPaymentForm(request.POST, initial=initial_data)

        if form.is_valid():
            pay = form.cleaned_data['pay']
            date_pay = form.cleaned_data['date_pay']

            delta_days = (date_pay - last_pay_date).days

            try:
                result = process_payment(credit, pay, date_pay, delta_days)
            except ValueError as e:
                messages.error(request, str(e))
                # Якщо помилка, повертаємо користувача на ту ж сторінку з формою
                return render(request, self.template_name, {'form': form, 'credit': credit})

            # У випадку, коли кредит закривається
            # і сума платежу більше залишку кредиту - зменшуємо останній платіж:
            if result['ost_payment'] > 0:
                pay -= result['ost_payment']

            # Зберігаємо сам платіж
            Payment.objects.create(credit=credit, pay=pay, date_pay=date_pay, dolg_percent=result["dolg_percent"], ostatok=result["ostatok"], pog_credit=result["pog_credit"], pog_summa_percent=result["pog_summa_percent"], summa_percent=result["summa_percent"], ost_payment=result["ost_payment"])

            return redirect('credit_detail', pk=credit.id)

        # Якщо з якихось причин дійшло до цього місця (помилки з даними) - повертаємо форму знову
        return render(request, self.template_name, {'form': form, 'credit': credit})


class AddCreditView(LoginRequiredMixin, View):
    template_name = 'credit_system/add_new_credit.html'
    form_class = AddCreditForm

    def dispatch(self, request, *args, **kwargs):
        # Перевірка дозволів: лише менеджери та адміни
        if not (request.user.is_superuser or request.user.is_manager):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, client_id):
        client = get_object_or_404(CustomUser, pk=client_id, role='client')
        form = self.form_class()

        context = {
            'form': form,
            'client': client,
        }
        return render(request, self.template_name, context)

    def post(self, request, client_id):
        client = get_object_or_404(CustomUser, pk=client_id, role='client')
        form = self.form_class(request.POST)

        # Перевіряємо, чи натиснута кнопка "Створити кредит"
        if 'create_credit' in request.POST:
            action = 'create_credit'
        else:
            action = 'calculate'  # За замовчуванням - розрахунок

        context = {
            'form': form,
            'client': client,
        }

        if form.is_valid():
            cleaned_data = form.cleaned_data

            # Дані для розрахунку/збереження
            credit_sum = cleaned_data['credit_sum']
            percent_for_calc = cleaned_data['percent'] / 100
            srok_months = cleaned_data['srok_months']
            start_date = cleaned_data['start_date']
            day_of_pay = cleaned_data['day_of_pay']

            # РОЗРАХУНОК (завжди відбувається, якщо форма валідна)
            plan_pay, grafik, total_pays_sum, pereplata = rozrahunok_plan_pay(
                credit_sum, percent_for_calc, srok_months, start_date, day_of_pay
            )

            # Додаємо результати розрахунку до контексту
            context.update({
                'plan_pay': plan_pay,
                'grafik': grafik,
                'total_pays_sum': total_pays_sum,
                'pereplata': pereplata,
            })

            # ЗБЕРЕЖЕННЯ (якщо натиснуто "Створити кредит")
            if action == 'create_credit':
                new_credit = Credit(
                    user=client,

                    summa_credit=credit_sum,
                    percent=cleaned_data['percent'],
                    start_date=start_date,
                    srok_months=srok_months,
                    day_of_pay=day_of_pay,
                    purpose=cleaned_data.get('purpose', ''),
                    note=cleaned_data.get('note', ''),
                    ostatok=credit_sum,
                    plan_pay=plan_pay,
                )

                new_credit.save()

                messages.success(request, f'Кредит №{new_credit.number} для клієнта {client} успішно створено!')
                # Використовуємо new_credit.number, оскільки повний номер тепер там зберігається
                return redirect('credit_detail', pk=new_credit.pk)

            # Якщо не "Створити кредит", то повертаємо форму з результатами розрахунку
            return render(request, self.template_name, context)

        # Якщо форма невалідна — повертаємо її з помилками
        return render(request, self.template_name, context)