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
    # В адмін-панелі (тільки для адміна) буде випадаючий список з ролями:
    ROLE_CHOICES = (
        ('admin', 'Адмін'),
        ('manager', 'Менеджер'),
        ('client', 'Клієнт'),
    )

    # Далі йдуть поля, яких немає в звичайному User:
    # Роль:
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Роль користувача"
    )
    # По-батькові:
    middle_name = models.CharField(max_length=100, verbose_name="По батькові", blank=True)
    IPN = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="ІПН",
        validators=[numeric_validator],
        null=True,
        blank=True
    )
    # Телефон, адреса, дата народження
    # (це все для прикладу, бо реально телефонів може бути кілька,
    # адреси поділяються на адресу прописки та проживання...)
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефону", blank=True)
    address = models.CharField(max_length=255, verbose_name="Адреса", blank=True)
    date_of_birth = models.DateField(verbose_name="Дата народження", null=True, blank=True)

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name} {self.middle_name}".strip()
        return full_name or self.username

    # Метод перевірки чи є користувач менеджером або адміном:
    @property
    def is_manager(self):
        return self.role == 'manager' or self.is_superuser

    # Метод для перевірки чи є користувач клієнтом:
    @property
    def is_client(self):
        return self.role == 'client'

    # Ці змінні працюють в адмін-панелі на сторінці юзерів:
    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"


class Credit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='credits', verbose_name="Користувач")
    number = models.CharField(max_length=100, verbose_name="Номер кредиту", blank=True)
    summa_credit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума кредиту")
    percent = models.DecimalField(max_digits=5, decimal_places=3, verbose_name="Добова відсоткова ставка (%)")
    start_date = models.DateField(verbose_name="Дата видачі")
    srok_months = models.IntegerField(verbose_name="Термін кредиту (місяці)")
    day_of_pay = models.IntegerField(
        verbose_name="Плановий день оплати",
        help_text="День місяця (від 1 до 28).",
        default=15
    )
    purpose = models.CharField(max_length=255, verbose_name="Ціль кредиту", blank=True)
    note = models.TextField(verbose_name="Примітка", blank=True)
    ostatok = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Залишок кредиту")
    closed = models.BooleanField(default=False, verbose_name="Кредит закрит")

    def __str__(self):
        return f"Кредит №{self.id} — {self.summa_credit} грн ({self.percent}%)"

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