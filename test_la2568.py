#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from myproject.la2568_api import la2568_api
from decimal import Decimal

def test_la2568_api():
    print("Testing LA2568 API Configuration:")
    print(f"Merchant Key: {la2568_api.merchant_key}")
    print(f"Merchant ID: {la2568_api.merchant_id}")
    print(f"Base URL: {la2568_api.base_url}")
    
    # Test signature generation with corrected merchant ID
    test_params = {
        'payment_type': 'online',
        'merchant': la2568_api.merchant_id,
        'order_id': 'TEST_123',
        'amount': '100.00',
        'bank_code': 'GCASH'
    }
    
    signature = la2568_api.generate_signature(test_params)
    print(f"Test signature: {signature}")
    
    # Test order creation
    print("\nTesting order creation...")
    result = la2568_api.create_direct_deposit_order(
        amount=Decimal('100.00'),
        user_id=1,
        payment_method='gcash',
        auto_redirect=True
    )
    
    print(f"Success: {result['success']}")
    if not result['success']:
        print(f"Error: {result['error']}")
        if 'error_details' in result:
            print(f"Details: {result['error_details']}")
    else:
        print(f"Order ID: {result['order_id']}")
        print(f"Deep links available: {list(result['mobile_deep_link'].keys())}")
        if 'raw_response' in result:
            print(f"API Response: {result['raw_response']}")

if __name__ == "__main__":
    test_la2568_api()
