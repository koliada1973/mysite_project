from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import UserCreditsView, index, AllCreditsView, CreditDetailView, AddPaymentView, AllClientsView, \
    AddClientView

urlpatterns = [
    # path('', views.index, name='index'),
    path('', index, name='index'),
    path('my-credits/', UserCreditsView.as_view(), name='user_credits_list'),
    path('all-credits/', AllCreditsView.as_view(), name='all_credits_list'),
    path('all-clients/', AllClientsView.as_view(), name='all_clients_list'),
    path('credit/<int:pk>/', views.CreditDetailView.as_view(), name='credit_detail'),
    path('client/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('client/new/', AddClientView.as_view(), name='add_new_client'),
    path('clients/<int:client_id>/new-credit/', views.AddCreditView.as_view(), name='add_new_credit'),
    path('credit/<int:credit_id>/add-payment/', AddPaymentView.as_view(), name='add_payment'),
    path('login/', auth_views.LoginView.as_view(template_name='credit_system/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

]

