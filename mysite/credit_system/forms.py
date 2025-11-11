from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from credit_system.models import Credit, Payment, CustomUser



class AddPaymentForm(forms.Form):
    date_pay = forms.DateField(
        label="Дата платежу",
        input_formats=["%Y-%m-%d"],
        initial=date.today,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))

    pay = forms.FloatField(
        label="Сума платежу (грн)",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", 'autofocus': True}))

    # Приховане поле, в яке передається last_pay_date з view
    last_pay_date = forms.DateField(widget=forms.HiddenInput())

    # Перевірка введених даних
    def clean(self):
        cleaned_data = super().clean()

        date_pay = cleaned_data.get('date_pay')
        pay = cleaned_data.get('pay')
        last_pay_date = cleaned_data.get('last_pay_date') # Отримуємо дату попереднього платежу

        # Перевірка, що сума платежу більше нуля:
        if pay is not None and pay <= 0:
            # raise ValidationError("Сума платежу має бути додатною.", code='invalid_pay_amount')
            self.add_error('pay', "Сума платежу має бути додатною.")

        # Перевірка чи дата платежу пізніше дати попереднього платежу
        if date_pay and last_pay_date:
            if date_pay < last_pay_date:
                # raise ValidationError("Дата платежу не може бути раніше або такою ж, як дата попереднього платежу.",code='invalid_payment_date')
                self.add_error('date_pay', "Дата платежу не може бути раніше дати попереднього платежу.")

        return cleaned_data



class ClientDetailForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username',  'last_name', 'first_name', 'middle_name',
            'IPN', 'phone_number', 'address',
            'date_of_birth', 'is_active'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'IPN': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'phone_number': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'disabled': True}),
        }


# Для адмін-панелі
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username', 'password1', 'password2',
            'first_name', 'last_name', 'middle_name', 'sex',
            'date_of_birth', 'place_of_birth', 'work_place', 'position',
            'email', 'phone_number', 'notes', 'IPN',
            'passport_series', 'passport_number', 'passport_vidan', 'passport_date',
            'address_registration', 'address_residential', 'role', 'is_active'
        )


# Для адмін-панелі
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'



class AddCreditForm(forms.Form):
    start_date = forms.DateField(
        label="Дата видачі",
        input_formats=["%Y-%m-%d"],
        initial=date.today,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))

    srok_months = forms.IntegerField(
        label="Термін (міс.)",
        initial=12,
        widget=forms.NumberInput(attrs={"class": "form-control"}))

    day_of_pay = forms.IntegerField(
        label="День оплати",
        initial=15,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": "1",
            "max": "31",
            "step": "1"
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
        widget=forms.Select(attrs={"class": "form-select"}))

    credit_sum = forms.FloatField(
        label="Сума (грн)",
        initial=10000,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", 'autofocus': True}))

    purpose = forms.CharField(
        max_length=255,
        required=False,
        label="Ціль кредиту",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 1})
    )

    note = forms.CharField(
        required=False,
        label="Примітка",
        # Це поле вже було з Textarea та rows=2
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 1})
    )

    # Перевірка даних
    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('start_date')
        srok = cleaned_data.get('srok_months')  # Змінено назву
        day_of_pay = cleaned_data.get('day_of_pay')  # day_of_pay вже Integer, не int(cleaned_data.get('day_of_pay'))
        percent = cleaned_data.get('percent')
        credit_sum = cleaned_data.get('credit_sum')  # Змінено назву

        # Перевірка терміну (місяці)
        if srok is not None and srok <= 0:
            self.add_error('srok_months', "Термін кредиту має бути більше нулю.")

        # Перевірка дати видачі
        today_date = date.today()
        if start_date and start_date < today_date:
            self.add_error('start_date', "Дата видачі кредиту не може бути раніше поточної дати.")

        # Перевірка дня оплати
        if day_of_pay is not None and (day_of_pay < 1 or day_of_pay > 31):
            self.add_error('day_of_pay', "День оплати має бути від 1 до 31")

        # Переведення % ставки з рядку в число
        if percent is not None:
            try:
                percent = float(percent)
                cleaned_data['percent'] = percent
            except ValueError:
                self.add_error('percent', "Некоректне значення відсоткової ставки.")

        # Перевірка суми кредиту
        if credit_sum is not None and credit_sum < 1000:
            self.add_error('credit_sum', "Сума кредиту має бути не менше 1000 грн")

        return cleaned_data


class ClientCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label="Підтвердження Пароля",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser

        fields = (
            'username',
            'password1',  # Явно додаємо
            'password2',  # Явно додаємо
            'last_name',
            'first_name',
            'middle_name',
            'IPN',
            'date_of_birth',
            'place_of_birth',
            'sex',
            'address_registration',
            'address_residential',
            'passport_series',
            'passport_number',
            'passport_vidan',
            'passport_date',
            'work_place',
            'position',
            'phone_number',
            'email',
            'notes',
        )

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'IPN': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-control'}),
            'sex': forms.Select(attrs={'class': 'form-select'}),
            'address_registration': forms.TextInput(attrs={'class': 'form-control'}),
            'address_residential': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_series': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_vidan': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'work_place': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)

        user.role = 'client'
        user.is_active = True

        if commit:
            user.save()
        return user