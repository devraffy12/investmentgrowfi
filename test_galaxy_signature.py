#!/usr/bin/env python
"""
Test Galaxy API signature generation
"""
import sys
import os
import hashlib

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
import django
django.setup()

from payments.views import generate_galaxy_signature

def test_signature_generation():
    """Test signature generation with Galaxy API parameters"""
    
    # Test parameters for PayMaya deposit
    test_params = {
        'merchant': 'RodolfHitler',
        'payment_type': '3',
        'amount': '300.00',
        'order_id': 'test_12345',
        'bank_code': 'PMP',
        'mobile': '09919067713',  # This should NOT be included in signature
        'callback_url': 'https://investmentgrowfi.onrender.com/api/callback/',
        'return_url': 'https://investmentgrowfi.onrender.com/deposit/success/'
    }
    
    secret_key = '86cb40fe1666b41eb0ad21577d66baef'
    
    print("🧪 Testing Galaxy API Signature Generation")
    print("=" * 50)
    print(f"Parameters: {test_params}")
    print(f"Secret Key: {secret_key}")
    print()
    
    # Generate signature
    signature = generate_galaxy_signature(test_params, secret_key)
    
    print(f"Generated Signature: {signature}")
    
    # Manual verification - what should be included in signature
    expected_params = ['merchant', 'payment_type', 'amount', 'order_id', 'bank_code', 'callback_url', 'return_url']
    query_parts = []
    for key in expected_params:
        if key in test_params:
            query_parts.append(f"{key}={test_params[key]}")
    
    query_string = '&'.join(query_parts)
    sign_string = f"{query_string}&key={secret_key}"
    expected_signature = hashlib.md5(sign_string.encode("utf-8")).hexdigest().upper()
    
    print(f"Expected Query: {query_string}")
    print(f"Expected Sign String: {sign_string}")
    print(f"Expected Signature: {expected_signature}")
    print()
    
    if signature == expected_signature:
        print("✅ Signature generation CORRECT!")
    else:
        print("❌ Signature generation INCORRECT!")
        
    print("=" * 50)

if __name__ == "__main__":
    test_signature_generation()
