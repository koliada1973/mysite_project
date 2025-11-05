from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Credit, Payment

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'last_name', 'first_name', 'role', 'IPN', 'phone_number', 'is_staff')
    list_filter = ('role', 'is_staff')

    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {
            'fields': ('role', 'middle_name', 'IPN', 'phone_number', 'address', 'date_of_birth'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'first_name', 'last_name', 'email'),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        - admin може створювати будь-кого;
        - manager може створювати лише клієнтів;
        """
        creator = request.user

        # Якщо користувач — менеджер, він створює тільки клієнтів
        if creator.role == 'manager' and not change:
            obj.role = 'client'
            obj.is_staff = False
            obj.is_superuser = False

        # Якщо користувач — адмін, дозволяємо будь-яку роль
        if creator.role == 'admin':
            if obj.role == 'admin':
                obj.is_staff = True
                obj.is_superuser = True
            elif obj.role == 'manager':
                obj.is_staff = True
                obj.is_superuser = False
            else:
                obj.is_staff = False
                obj.is_superuser = False

        super().save_model(request, obj, form, change)


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'summa_credit', 'percent', 'start_date', 'srok_months')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Менеджер бачить усіх клієнтів, клієнт — лише свої кредити
        if request.user.is_superuser or request.user.is_manager:
            return qs
        return qs.filter(user=request.user)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('credit', 'pay', 'date_pay')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_manager:
            return qs
        # Клієнт бачить тільки свої платежі
        return qs.filter(credit__user=request.user)