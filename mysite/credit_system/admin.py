from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Credit, Payment
from django.contrib.auth.models import Group

admin.site.unregister(Group)    # Ховаємо групи в адмін-панелі


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'last_name', 'first_name', 'role', 'IPN', 'phone_number', 'address')

    # Поля, які показуються у формі редагування користувача
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Особиста інформація', {
            'fields': ('first_name', 'last_name', 'middle_name', 'email', 'phone_number', 'address', 'date_of_birth'),
        }),
        ('Ідентифікаційні дані', {
            'fields': ('IPN',),
        }),
        ('Роль та права доступу', {
            'fields': ('role', 'is_active', 'last_login', 'date_joined'),
        }),
    )

    # Поля, які показуються при створенні нового користувача
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2',
                'first_name', 'last_name', 'middle_name',
                'email', 'phone_number', 'address', 'date_of_birth',
                'IPN', 'role',
            ),
        }),
    )

    readonly_fields = ('last_login', 'date_joined')

    # Фільтр "роль" тільки для суперюзера
    def get_list_filter(self, request):
        if request.user.is_superuser:
            return ('role',)
        return ()

    # Показуємо лише дозволених користувачів
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(role='client')

    # Автоматично призначаємо роль "client" для нових користувачів, створених менеджером
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.role = 'client'

        if obj.role == 'admin':
            obj.is_superuser = True
            obj.is_staff = True
        elif obj.role == 'manager':
            obj.is_superuser = False
            obj.is_staff = True
        else:
            obj.is_superuser = False
            obj.is_staff = False

        super().save_model(request, obj, form, change)

    # Сховати поле "роль" від менеджера
    def get_fieldsets(self, request, obj=None):
        fieldsets = list(self.fieldsets)
        if not request.user.is_superuser:
            filtered = []
            for name, section in fieldsets:
                fields = list(section.get('fields', []))
                if 'role' in fields:
                    fields.remove('role')
                filtered.append((name, {'fields': fields}))
            return filtered
        return fieldsets

    # Сховати системні поля від менеджера
    def get_readonly_fields(self, request, obj=None):
        base = list(super().get_readonly_fields(request, obj))
        base += ['is_staff', 'is_superuser', 'user_permissions', 'groups']
        return base



@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    # Відображення у списку кредитів
    list_display = (
         'number','id', 'user', 'summa_credit', 'percent',
        'start_date', 'srok_months', 'dolg_percent', 'ostatok', 'closed'
    )

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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('credit', 'pay', 'date_pay')

    # Заборона додавання нового платежу через адмін-панель,
    # бо при додаванні платежу потрібно робити розрахунки (це робиться через сторінку add_payment.html)
    def has_add_permission(self, request):
        return False  # Повертаємо False, щоб приховати кнопку "Додати"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_manager:
            return qs
        # Для простого клієнта вибираємо тільки його платежі
        return qs.filter(credit__user=request.user)