#!/usr/bin/env python3
"""
Create default payment methods for testing
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from payments.models import PaymentMethod

def create_payment_methods():
    """Create default payment methods"""
    
    payment_methods = [
        {
            'name': 'GCash',
            'code': 'gcash',
            'logo': 'gcash.jpg',
            'is_active': True,
            'min_amount': 50.00,
            'max_amount': 50000.00,
            'fee_percentage': 0.00,
            'fee_fixed': 0.00,
            'la2568_type': 'gcash',
            'supports_qr': True,
            'supports_app_redirect': True,
            'display_order': 1
        },
        {
            'name': 'Maya',
            'code': 'maya',
            'logo': 'maya.jpg',
            'is_active': True,
            'min_amount': 50.00,
            'max_amount': 50000.00,
            'fee_percentage': 0.00,
            'fee_fixed': 0.00,
            'la2568_type': 'maya',
            'supports_qr': True,
            'supports_app_redirect': True,
            'display_order': 2
        },
        {
            'name': 'PayMaya',
            'code': 'paymaya',
            'logo': 'maya.jpg',
            'is_active': True,
            'min_amount': 50.00,
            'max_amount': 50000.00,
            'fee_percentage': 0.00,
            'fee_fixed': 0.00,
            'la2568_type': 'paymaya',
            'supports_qr': True,
            'supports_app_redirect': True,
            'display_order': 3
        }
    ]
    
    for method_data in payment_methods:
        method, created = PaymentMethod.objects.get_or_create(
            code=method_data['code'],
            defaults=method_data
        )
        
        if created:
            print(f"✅ Created payment method: {method.name}")
        else:
            print(f"ℹ️  Payment method already exists: {method.name}")
    
    print(f"\n📊 Total active payment methods: {PaymentMethod.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    create_payment_methods()
