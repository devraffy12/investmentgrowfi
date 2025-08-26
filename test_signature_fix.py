#!/usr/bin/env python
"""
Fix LA2568 Signature Issue
Test different signature methods to find the correct one for LA2568
"""

import os
import sys
import django
import hashlib

# Setup Django environment
sys.path.append('c:\\Users\\raffy\\OneDrive\\Desktop\\investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

def test_signature_methods():
    """Test different signature generation methods"""
    
    # Test parameters exactly as shown in your specification
    params = {
        'merchant': 'RodolfHitler',
        'payment_type': '3',
        'amount': '100.00',
        'order_id': 'ORDER123456',
        'bank_code': 'gcash',
        'callback_url': 'https://investmentgrowfi.onrender.com/payment/callback/',
        'return_url': 'https://investmentgrowfi.onrender.com/payment/success/'
    }
    
    secret_key = '86cb40fe1666b41eb0ad21577d66baef'
    
    print("🔧 Testing LA2568 Signature Methods")
    print("=" * 60)
    
    # Method 1: Alphabetical sort (current implementation)
    sorted_params = sorted(params.items())
    query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
    sign_string = f"{query_string}&key={secret_key}"
    signature1 = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    print(f"Method 1 (Alphabetical sort):")
    print(f"Query: {query_string}")
    print(f"Sign string: {sign_string}")
    print(f"Signature: {signature1}")
    print()
    
    # Method 2: Original order
    query_string2 = '&'.join([f"{key}={value}" for key, value in params.items()])
    sign_string2 = f"{query_string2}&key={secret_key}"
    signature2 = hashlib.md5(sign_string2.encode('utf-8')).hexdigest().upper()
    
    print(f"Method 2 (Original order):")
    print(f"Query: {query_string2}")
    print(f"Sign string: {sign_string2}")
    print(f"Signature: {signature2}")
    print()
    
    # Method 3: Specific order from specification
    ordered_keys = ['merchant', 'payment_type', 'amount', 'order_id', 'bank_code', 'callback_url', 'return_url']
    query_parts = []
    for key in ordered_keys:
        if key in params:
            query_parts.append(f"{key}={params[key]}")
    query_string3 = '&'.join(query_parts)
    sign_string3 = f"{query_string3}&key={secret_key}"
    signature3 = hashlib.md5(sign_string3.encode('utf-8')).hexdigest().upper()
    
    print(f"Method 3 (Specification order):")
    print(f"Query: {query_string3}")
    print(f"Sign string: {sign_string3}")
    print(f"Signature: {signature3}")
    print()
    
    # Expected signature from your specification
    expected_signature = "C7DD8BE42931AE10069B5577B7C4D304"  # From your example
    
    print(f"Expected signature: {expected_signature}")
    print(f"Method 1 matches: {signature1 == expected_signature}")
    print(f"Method 2 matches: {signature2 == expected_signature}")
    print(f"Method 3 matches: {signature3 == expected_signature}")
    
    # Try without URL encoding
    print("\n🔧 Testing without URL encoding...")
    
    # Method 4: Try with different callback URLs
    params_alt = params.copy()
    params_alt['callback_url'] = 'https://yourwebsite.com/api/callback'
    params_alt['return_url'] = 'https://yourwebsite.com/deposit/success'
    
    query_string4 = '&'.join([f"{key}={value}" for key, value in sorted(params_alt.items())])
    sign_string4 = f"{query_string4}&key={secret_key}"
    signature4 = hashlib.md5(sign_string4.encode('utf-8')).hexdigest().upper()
    
    print(f"Method 4 (With spec URLs):")
    print(f"Query: {query_string4}")
    print(f"Signature: {signature4}")
    print(f"Matches expected: {signature4 == expected_signature}")
    
    return signature4 == expected_signature

if __name__ == "__main__":
    success = test_signature_methods()
    
    if success:
        print("\n✅ Found correct signature method!")
        print("🔧 Updating LA2568 service...")
    else:
        print("\n❌ None of the methods match the expected signature.")
        print("🔧 Will try the specification order method anyway...")
