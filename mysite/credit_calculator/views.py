from django.shortcuts import render
from django.views import View

from credit_calculator.forms import CalculatorForm
from credit_calculator.plan_pay import rozrahunok_plan_pay


# def calculator_view(request):
#     return render(request, 'credit_calculator/calculator.html')

class CalculatorView(View):
    template_name = 'credit_calculator/calculator.html'

    def get(self, request):
        form = CalculatorForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # Обробка форми після натискання "Розрахувати"
        form = CalculatorForm(request.POST)

        if form.is_valid():
            # Отримуємо дані з форми
            start_date = form.cleaned_data['start_date']
            srok = form.cleaned_data['srok']
            percent = form.cleaned_data['percent']/100
            credit_sum = form.cleaned_data['credit_sum']
            day_of_pay = form.cleaned_data['day_of_pay']

            plan_pay, grafik, total_pays_sum, pereplata = rozrahunok_plan_pay(credit_sum, percent, srok, start_date, day_of_pay)

            context = {
                'form': form,
                'plan_pay': plan_pay,
                'grafik': grafik,
                'total_pays_sum': total_pays_sum,
                'pereplata': pereplata,
            }

            return render(request, self.template_name, context)

        # Якщо форма невалідна — повертаємо її з помилками
        return render(request, self.template_name, {'form': form})