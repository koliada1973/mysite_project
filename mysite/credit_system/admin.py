from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Credit, Payment
from django.contrib.auth.models import Group, Permission
from .forms import CustomUserCreationForm, CustomUserChangeForm

admin.site.unregister(Group)    # Скриваємо групи в адмін-панелі


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('full_name', 'IPN', 'phone_number', 'email', 'username', 'role')
    readonly_fields = ('last_login', 'date_joined')
    list_filter = ('role',)

    # Повний набір полів для суперкористувача (адміністратора)
    SUPERUSER_FIELDSETS = (
        (None, {'fields': ('username', 'password',)}),
        ('Особиста інформація', {
            'fields': (
                'first_name', 'last_name', 'middle_name', 'sex',
                'date_of_birth', 'place_of_birth',
                'work_place', 'position', 'email', 'phone_number', 'notes'
            ),
        }),
        ('Ідентифікаційні дані', {
            'fields': (
                'IPN', 'passport_series', 'passport_number', 'passport_vidan',
                'passport_date', 'address_registration', 'address_residential',
            ),
        }),
        ('Роль та права доступу', {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions', 'last_login', 'date_joined',
            ),
        }),
    )

    # Набір полів для менеджера (без is_active, is_staff, is_superuser, groups, user_permissions)
    MANAGER_FIELDSETS = (
        (None, {'fields': ('username', 'password',)}),
        ('Особиста інформація', {
            'fields': (
                'first_name', 'last_name', 'middle_name', 'sex',
                'date_of_birth', 'place_of_birth',
                'work_place', 'position', 'email', 'phone_number', 'notes'
            ),
        }),
        ('Ідентифікаційні дані', {
            'fields': (
                'IPN', 'passport_series', 'passport_number', 'passport_vidan',
                'passport_date', 'address_registration', 'address_residential',
            ),
        }),
        ('Роль та права доступу', {
            'fields': (
                # 'role',  # 'role'
                'last_login', 'date_joined',
            ),
        }),
    )

    # Додаткові набори полів для форми створення (add form)
    ADD_SUPERUSER_FIELDSETS = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
            ),
        }),
        ('Особиста інформація', {
            'fields': (
                'first_name', 'last_name', 'middle_name', 'sex',
                'date_of_birth', 'place_of_birth',
                'work_place', 'position', 'email', 'phone_number', 'notes'
            ),
        }),
        ('Ідентифікаційні дані', {
            'fields': (
                'IPN', 'passport_series', 'passport_number', 'passport_vidan',
                'passport_date', 'address_registration', 'address_residential',
            ),
        }),
        ('Роль та права доступу', {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            ),
        }),
    )

    ADD_MANAGER_FIELDSETS = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
            ),
        }),
        ('Особиста інформація', {
            'fields': (
                'first_name', 'last_name', 'middle_name', 'sex',
                'date_of_birth', 'place_of_birth',
                'work_place', 'position', 'email', 'phone_number', 'notes'
            ),
        }),
        ('Ідентифікаційні дані', {
            'fields': (
                'IPN', 'passport_series', 'passport_number', 'passport_vidan',
                'passport_date', 'address_registration', 'address_residential',
            ),
        }),
        # ('Роль та права доступу', {
        #     'fields': (
        #         'role',
        #     ),
        # }),
    )


    def get_fieldsets(self, request, obj=None):     # obj=None означає, що це форма створення, але ми використаємо add_fieldsets
        """Повертає fieldsets для форми редагування."""
        if request.user.is_superuser:
            return self.SUPERUSER_FIELDSETS     # Суперкористувач бачить повний набір полів
        else:
            return self.MANAGER_FIELDSETS       # Менеджер бачить обмежений набір

    def get_add_fieldsets(self, request):
        """Повертає fieldsets для форми створення."""
        if request.user.is_superuser:
            return self.ADD_SUPERUSER_FIELDSETS # Суперкористувач бачить повний набір полів для створення
        else:
            return self.ADD_MANAGER_FIELDSETS   # Менеджер бачить обмежений набір полів для створення

    # Додаткова рекомендація: обмежити, які об'єкти може бачити менеджер
    # щоб він не міг редагувати/створювати суперкористувачів
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Якщо користувач - не суперкористувач, він не може бачити суперкористувачів
        return qs.exclude(is_superuser=True)

    search_fields = ('last_name', 'first_name')
    list_display_links = ('full_name',)

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    # Відображення у списку кредитів
    list_display = (
         'id','number', 'user', 'formatted_start_date', 'srok_months',
         'summa_credit','ostatok', 'closed'
    )

    def formatted_start_date(self, obj):
        """Форматує дату початку кредиту у dd.mm.yyyy"""
        if obj.start_date:
            return obj.start_date.strftime('%d.%m.%Y')
        return "-"
    # formatted_start_date.admin_order_field = 'start_date'     # Сортування буде відбуватись за оригінальним полем 'start_date' в БД
    formatted_start_date.short_description = 'Дата видачі'      # Додаємо заголовок стовпця для відображення в адмін-панелі

    # Поля для створення та редагування
    def get_fields(self, request, obj=None):
        """Визначає, які поля показувати у формі"""
        if obj:  # якщо редагуємо існуючий кредит
            return [
                'user', 'number', 'start_date', 'last_pay_date',
                'summa_credit', 'srok_months', 'purpose', 'note',
                'ostatok', 'percent', 'dolg_percent', 'closed'
            ]
        else:  # якщо створюємо новий кредит
            return [
                'user', 'number', 'summa_credit', 'start_date',
                 'srok_months', 'percent', 'purpose', 'note',
                 'closed'
            ]

    # При створенні нового кредиту копіюємо суму в залишок
    def save_model(self, request, obj, form, change):
        if not change or obj.ostatok is None:
            obj.ostatok = obj.summa_credit
        super().save_model(request, obj, form, change)

    # Фільтрація для різних користувачів
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, 'is_manager', False):
            return qs
        return qs.filter(user=request.user)

    list_display_links = ('number',)



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'credit', 'formatted_date_pay', 'pay')
    ordering = ('-date_pay',)

    # Заборона додавання нового платежу через адмін-панель,
    # бо при додаванні платежу потрібно робити розрахунки (це робиться через сторінку add_payment.html)
    def has_add_permission(self, request):
        return False  # Повертаємо False, щоб приховати кнопку "Додати"


    def formatted_date_pay(self, obj):
        if obj.date_pay:
            return obj.date_pay.strftime('%d.%m.%Y')
        return "-"
    formatted_date_pay.admin_order_field = 'date_pay'       # Сортування буде відбуватись за оригінальним полем 'date_pay' в БД
    formatted_date_pay.short_description = 'Дата платежу'   # Додаємо заголовок стовпця для відображення в адмін-панелі


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_manager:
            return qs
        # Для простого клієнта вибираємо тільки його платежі
        return qs.filter(credit__user=request.user)