from datetime import date

from django import forms
from credit_system.models import Credit, Payment

# class CreditDetailForm(forms.ModelForm):
#     class Meta:
#         model = Credit
#         fields = [
#             'user', 'number', 'summa_credit', 'percent',
#             'start_date', 'srok_months', 'ostatok',
#             'purpose', 'note', 'closed'
#         ]
#         widgets = {
#             'user': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
#             'number': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
#             'summa_credit': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
#             'percent': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
#             'start_date': forms.DateInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
#             'srok_months': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
#             'ostatok': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
#             'purpose': forms.Textarea(attrs={'readonly': 'readonly', 'class': 'form-control', 'rows': 2}),
#             'note': forms.Textarea(attrs={'readonly': 'readonly', 'class': 'form-control', 'rows': 2}),
#             'closed': forms.CheckboxInput(attrs={'disabled': True}),
#         }


class AddPaymentForm(forms.Form):
    date_pay = forms.DateField(
        label="Дата платежу",
        input_formats=["%Y-%m-%d"],
        initial=date.today,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})     # "class": "form-control" це для bootstrap
    )
    pay = forms.FloatField(
        label="Сума платежу (грн)",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"})   # "class": "form-control" це для bootstrap
    )