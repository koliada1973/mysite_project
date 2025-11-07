from django import forms
from credit_system.models import Credit

class CreditDetailForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = [
            'user', 'number', 'summa_credit', 'percent',
            'start_date', 'srok_months', 'ostatok',
            'purpose', 'note', 'closed'
        ]
        widgets = {
            'user': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'number': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'summa_credit': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'percent': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'srok_months': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'ostatok': forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'readonly': 'readonly', 'class': 'form-control', 'rows': 2}),
            'note': forms.Textarea(attrs={'readonly': 'readonly', 'class': 'form-control', 'rows': 2}),
            'closed': forms.CheckboxInput(attrs={'disabled': True}),
        }