from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from datetime import date

# Валідатор для ІПН — лише 10 цифр
numeric_validator = RegexValidator(
    r'^\d{10}$',
    'Введіть коректний ІПН — рівно 10 цифр.'
)

class CustomUser(AbstractUser):
    """Розширена модель користувача (об’єднана з клієнтом)"""
    ROLE_CHOICES = (
        ('admin', 'Адмін'),
        ('manager', 'Менеджер'),
        ('client', 'Клієнт'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Роль користувача"
    )

    middle_name = models.CharField(max_length=100, verbose_name="По батькові", blank=True)
    IPN = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="ІПН",
        validators=[numeric_validator],
        null=True,
        blank=True
    )
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефону", blank=True)
    address = models.CharField(max_length=255, verbose_name="Адреса", blank=True)
    date_of_birth = models.DateField(verbose_name="Дата народження", null=True, blank=True)

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name} {self.middle_name}".strip()
        return full_name or self.username

    @property
    def is_manager(self):
        return self.role == 'manager' or self.is_superuser

    @property
    def is_client(self):
        return self.role == 'client'

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"


class Credit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='credits', verbose_name="Користувач")
    summa_credit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Основна сума кредиту")
    percent = models.DecimalField(max_digits=5, decimal_places=3, verbose_name="Добова відсоткова ставка (%)")
    start_date = models.DateField(verbose_name="Дата видачі")
    srok_months = models.IntegerField(verbose_name="Термін кредиту (місяці)")
    day_of_pay = models.IntegerField(
        verbose_name="Плановий день оплати",
        help_text="День місяця (від 1 до 28).",
        default=15
    )

    def __str__(self):
        return f"Кредит №{self.id} ({self.summa_credit} грн) для {self.user}"


    class Meta:
        verbose_name = "Кредит"
        verbose_name_plural = "Кредити"

class Payment(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name='payments', verbose_name="Кредит")
    pay = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума платежу")
    date_pay = models.DateField(default=date.today, verbose_name="Дата платежу")

    def __str__(self):
        return f"Платіж {self.pay} грн по кредиту №{self.credit.id} від {self.date_pay}"

    class Meta:
        verbose_name = "Платіж"
        verbose_name_plural = "Платежі"