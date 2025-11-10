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

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'