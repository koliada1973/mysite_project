from django import forms
from datetime import date


class CalculatorForm(forms.Form):
    start_date = forms.DateField(
        label="Дата видачі",
        input_formats=["%Y-%m-%d"],
        initial=date.today,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))

    srok = forms.IntegerField(
        label="Срок (міс.)",
        initial=12,
        widget=forms.NumberInput(attrs={"class": "form-control"}))


    day_of_pay = forms.IntegerField(
        label="День оплати",
        initial=15,
        # help_text="Виберіть плановий день щомісячної оплати від 1 до 31",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": "1",  # Мінімальне значення
            "max": "31",  # Максимальне значення
            "step": "1"  # Крок зміни значення
        }))


    PERCENT_CHOICES = [
        (0.08, "0,08"),
        (0.10, "0,10"),
        (0.12, "0,12"),
        (0.15, "0,15"),
    ]
    percent = forms.ChoiceField(
        label="% за добу",
        choices=PERCENT_CHOICES,
        initial=0.10,
        # help_text="Виберіть добову % ставку",
        widget=forms.Select(attrs={"class": "form-select"}))

    credit_sum = forms.FloatField(
            label="Сума (грн)",
            initial=10000,
            widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", 'autofocus': True}))

    # Перевірка введених даних
    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        srok = cleaned_data.get('srok')
        day_of_pay = int(cleaned_data.get('day_of_pay'))
        percent = cleaned_data.get('percent')
        credit_sum = cleaned_data.get('credit_sum')


        # Перевірка, що термін кредиту (місяці) більше нуля:
        if srok is not None and srok <= 0:
            self.add_error('srok', "Термін кредиту має бути більше нулю.")

        # Перевірка чи дата видачі кредиту пізніше поточної дати (сьогодні)
        today_date = date.today()
        if start_date:
            if start_date < today_date:
                self.add_error('start_date', "Дата видачі кредиту не може бути раніше поточної дати.")

        # Перевірка чи день оплати від 1 до 31
        if day_of_pay is not None:
            if day_of_pay < 1 or day_of_pay > 31:
                self.add_error('day_of_pay', "День оплати має бути від 1 до 31")

        # # Перевірка чи введена % ставка більше нулю, та меньше 1 % (добових)
        # if percent is not None:
        #     if percent <= 0 or percent > 1:
        #         self.add_error('percent', "Відсоткова ставка має бути від 0 до 1 %.")

        # Переведення % ставки з рядку в число (вона вибирається зі списку):
        if percent is not None:
            try:
                percent = float(percent)
                cleaned_data['percent'] = percent
            except ValueError:
                self.add_error('percent', "Некоректне значення відсоткової ставки.")

        # Перевірка чи введена сума кредиту менше 1000 грн.
        if credit_sum is not None:
            if credit_sum < 1000:
                self.add_error('credit_sum', "Сума кредиту має бути не менше 1000 грн")

        return cleaned_data