from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from datetime import date

from django.db.models import Max

# Валідатор для ІПН — лише 10 цифр (ChatGPT)
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
    # Податковий номер
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

    SEX_CHOICES = (
        ('m', 'Чоловіча'),  # Значення в базі: 'm', Зображається: 'Чоловіча'
        ('w', 'Жіноча'),  # Значення в базі: 'w', Зображається: 'Жіноча'
    )
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
        default='m',
        verbose_name="Стать",
        blank=True,
        null=True
    )

    address_registration = models.CharField(max_length=255, verbose_name="Адреса прописки", blank=True)
    address_residential = models.CharField(max_length=255, verbose_name="Адреса проживання", blank=True)
    place_of_birth = models.CharField(max_length=255, verbose_name="Місце народження", blank=True)
    passport_series = models.CharField(max_length=2, verbose_name="Серія паспорту", blank=True)
    passport_number = models.CharField(max_length=10, verbose_name="Номер паспорту", blank=True)
    passport_vidan = models.CharField(max_length=255, verbose_name="Орган що видав паспорт", blank=True)
    passport_date = models.DateField(verbose_name="Дата видачі паспорта", null=True, blank=True)
    work_place = models.CharField(max_length=100, verbose_name="Місце роботи", blank=True)
    position = models.CharField(max_length=100, verbose_name="Посада", blank=True)
    notes = models.CharField(max_length=255, verbose_name="Нотатки", blank=True)

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

    # Ці змінні працюють в адмін-панелі на сторінці Користувачі:
    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"


class Credit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='credits', verbose_name="Користувач")
    number = models.CharField(max_length=100, verbose_name="Номер кредиту", blank=True)
    number1 = models.IntegerField(verbose_name="Порядковий номер", null=True, blank=True)
    number2 = models.IntegerField(verbose_name="Рік видачі", null=True, blank=True)
    number3 = models.CharField(max_length=20, verbose_name="Постфікс/Підрозділ", blank=True)
    summa_credit = models.FloatField(verbose_name="Сума кредиту")
    percent = models.FloatField(verbose_name="Добова відсоткова ставка (%)")
    start_date = models.DateField(verbose_name="Дата видачі")
    srok_months = models.IntegerField(verbose_name="Термін кредиту (місяці)")
    day_of_pay = models.IntegerField(default=15, verbose_name="Плановий день оплати")
    purpose = models.CharField(max_length=255, verbose_name="Ціль кредиту", blank=True)
    note = models.TextField(verbose_name="Примітка", blank=True)
    ostatok = models.FloatField(verbose_name="Залишок кредиту")
    closed = models.BooleanField(default=False, verbose_name="Кредит закрит")
    last_pay_date = models.DateField(null=True, blank=True, verbose_name="Дата останнього платежу")
    dolg_percent = models.FloatField(default=0, verbose_name="Борг по оплаті %")
    plan_pay = models.FloatField(verbose_name="Плановий платіж", blank=True)

    def full_number(self):
        # Логіка формування повного номера, використовуючи поточні значення
        if self.number1 and self.number2:
            # Доповнення нулями до 4 знаків
            seq = str(self.number1).zfill(4)
            # Формат: NNNN/YYYY-POSTFIX
            return f"{seq}/{self.number2}-{self.number3}"
        return "Н/Д"

    def __str__(self):
        # Виводимо повний номер, що зберігається в полі number
        return f"Кредит №{self.number or self.full_number()}"

    def generate_new_number1(self):
        # Використовуємо self.start_date, оскільки рік залежить від дати видачі
        current_year = self.start_date.year

        max_number1 = Credit.objects.filter(number2=current_year).aggregate(Max('number1'))['number1__max']

        return (max_number1 or 0) + 1

    def save(self, *args, **kwargs):
        # 1. Логіка автозаповнення номера (працює лише для нового об'єкта)
        if not self.pk:
            # 1.1. Встановлюємо рік (number2)
            if self.number2 is None:
                # ВАЖЛИВО: self.start_date має бути встановлено перед save(),
                # якщо воно не валідується формою, то буде помилка.
                self.number2 = self.start_date.year

            # 1.2. Встановлюємо порядковий номер (number1)
            if self.number1 is None:
                self.number1 = self.generate_new_number1()

            # 1.3. Встановлюємо фіксований постфікс (number3)
            # Якщо ви хочете, щоб він був "Credit", можете встановити його тут
            if not self.number3:
                self.number3 = "Credit"

            # 1.4. Заповнюємо фінальне поле number
            if not self.number:
                self.number = self.full_number()

                # 2. Встановлення last_pay_date
        if not self.last_pay_date and self.start_date:
            self.last_pay_date = self.start_date

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Кредит"
        verbose_name_plural = "Кредити"
        unique_together = ('number1', 'number2')


class Payment(models.Model):
    credit = models.ForeignKey(Credit, on_delete=models.CASCADE, related_name='payments', verbose_name="Кредит")
    date_pay = models.DateField(default=date.today, verbose_name="Дата платежу")
    summa_percent = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Нараховано %")
    pay = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сума платежу")
    pog_summa_percent = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Погашено %")
    dolg_percent = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Борг по оплаті %")
    pog_credit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Погашено кредиту")
    ostatok = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Залишок кредиту")
    ost_payment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Залишок платежу")

    def __str__(self):
        return f"Платіж {self.pay} грн по кредиту №{self.credit.id} від {self.date_pay}"

    class Meta:
        verbose_name = "Платіж"
        verbose_name_plural = "Платежі"