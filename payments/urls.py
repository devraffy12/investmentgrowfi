# urls.py - Fixed Galaxy Payment URLs
from django.urls import path, re_path
from . import views

app_name = 'payments'

urlpatterns = [
    # Main payment views
    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('history/', views.transaction_history, name='history'),
    
    # Payment flow URLs (where users get redirected after payment)
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),   
    path('processing/', views.payment_processing, name='payment_processing'),   # New processing page
    
    # Payment verification APIs
    path('api/verify-payment/', views.verify_payment_api, name='verify_payment_api'),
    path('api/check-status/', views.check_payment_status, name='check_payment_status_api'),   
    
    # Galaxy API callback endpoints (primary)
    path('api/galaxy/callback/', views.galaxy_callback_view, name='galaxy_callback'),
    path('api/callback/', views.galaxy_callback_view, name='callback_alias'),  # Alternative endpoint
    path('api/test-callback/', views.test_callback, name='test_callback'),  # Test endpoint
    
    # Status checking endpoints
    path('api/status/', views.check_payment_status, name='check_payment_status'),
    path('api/payment-status/<str:reference_id>/', views.payment_status_api, name='payment_status_api'),
    
    # Galaxy API query endpoints
    path('api/query/<str:order_id>/', views.query_transaction, name='query_transaction'),
    path('api/balance/', views.merchant_balance, name='merchant_balance'),
    
    # Admin/utility endpoints
    path('api/verify/', views.manual_payment_verify, name='manual_payment_verify'),
]

# Additional patterns for callback URL flexibility
# Galaxy might use different callback URL formats
urlpatterns += [
    # Handle callbacks with or without trailing slash
    re_path(r'^callback/?$', views.galaxy_callback_view, name='flexible_callback'),
    re_path(r'^api/notify/?$', views.galaxy_callback_view, name='notify_callback'),
]