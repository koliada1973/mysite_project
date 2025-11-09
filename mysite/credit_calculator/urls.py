from django.urls import path
from . import views

urlpatterns = [
    path('', views.CalculatorView.as_view(), name='credit_calculator'),
]