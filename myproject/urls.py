from django.urls import path
from . import views
from payments import views as payment_views

urlpatterns = [
    # Public pages
    path('', views.register, name='index'),  # Changed to register as default page
    path('home/', views.index, name='home'),  # Moved index to /home/
    path('about/', views.about, name='about'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # User Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Investment System
    path('plans/', views.investment_plans, name='investment_plans'),
    path('invest/<int:plan_id>/', views.make_investment, name='make_investment'),
    path('my-investments/', views.my_investments, name='my_investments'),
    path('calculator/', views.calculator, name='calculator'),
    path('calculate/', views.calculate_investment, name='calculate_investment'),
    
    # Financial Management
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('deposit/', payment_views.deposit_view, name='deposit'),
    path('deposit/success/', views.deposit_success, name='deposit_success'),
    path('withdraw/', payment_views.withdraw_view, name='withdraw'),
    path('payments/callback/', payment_views.payment_callback, name='payment_callback'),
    
    # Bank Accounts
    path('bank-accounts/', views.bank_accounts, name='bank_accounts'),
    path('bank-accounts/add/', views.add_bank_account, name='add_bank_account'),
    path('bank-accounts/delete/<int:account_id>/', views.delete_bank_account, name='delete_bank_account'),
    path('bank-accounts/set-primary/<int:account_id>/', views.set_primary_account, name='set_primary_account'),
    
    # Referral System
    path('referrals/', views.referrals, name='referrals'),
    path('team/', views.team, name='team'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    
    # Support System
    path('support/', views.support, name='support'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
    # API endpoints
    path('api/notification-count/', views.api_notification_count, name='api_notification_count'),
    path('api/payment-status/<str:reference_id>/', views.payment_status_api, name='payment_status_api'),
    path('api/la2568/callback/', views.la2568_callback, name='la2568_callback'),
    path('api/gcash/webhook/', views.gcash_webhook, name='gcash_webhook'),
    path('api/recent-activities/', views.recent_activities_api, name='recent_activities_api'),
    path('api/recent-investments/', views.recent_investments_api, name='recent_investments_api'),
    path('api/deposits-withdrawals/', views.deposits_withdrawals_api, name='api_deposits_withdrawals'),
    path('api/private/deposits-withdrawals/', views.private_deposits_withdrawals_api, name='api_private_deposits_withdrawals'),
    path('api/auth/firebase-login/', views.firebase_login, name='firebase_login'),
]
