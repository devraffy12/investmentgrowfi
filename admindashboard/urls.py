from django.urls import path
from . import views

app_name = 'admindashboard'
# admindlogin
urlpatterns = [
    path('admindlogin/', views.admin_login, name='admindlogin'),
    path('logout/', views.admin_logout, name='logout'),
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.admin_users, name='users'),
    path('deposits/', views.admin_deposits, name='deposits'),
    path('withdrawals/', views.admin_withdrawals, name='withdrawals'),
    path('transactions/', views.admin_transactions, name='transactions'),
]
