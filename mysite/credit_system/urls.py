from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import UserCreditsView, index

urlpatterns = [
    # path('', views.index, name='index'),
    path('', index, name='index'),
    path('my-credits/', UserCreditsView.as_view(), name='user_credits_list'),
    path('login/', auth_views.LoginView.as_view(template_name='credit_system/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
]