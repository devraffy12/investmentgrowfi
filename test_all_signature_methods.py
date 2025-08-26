#!/usr/bin/env python
"""
Test Different Signature Approaches for LA2568
"""

import requests
import hashlib
import urllib.parse

def test_alphabetical_order():
    """Test signature with alphabetical parameter order"""
    print("🔧 Testing Alphabetical Order")
    print("=" * 30)
    
    # Parameters from specification
    params = {
        'merchant': 'RodolfHitler',
        'payment_type': '3',
        'amount': '100.00',
        'order_id': 'ORDER123456',
        'bank_code': 'gcash',
        'callback_url': 'https://yourwebsite.com/api/callback',
        'return_url': 'https://yourwebsite.com/deposit/success'
    }
    
    secret_key = '86cb40fe1666b41eb0ad21577d66baef'
    
    # Sort alphabetically
    sorted_params = dict(sorted(params.items()))
    
    query_parts = []
    for key, value in sorted_params.items():
        query_parts.append(f"{key}={value}")
    
    query_string = '&'.join(query_parts)
    sign_string = f"{query_string}&key={secret_key}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    print(f"🔐 Sorted params: {sorted_params}")
    print(f"🔐 Query string: {query_string}")
    print(f"🔐 Sign string: {sign_string}")
    print(f"🔐 Signature: {signature}")
    print(f"📋 Expected: C7DD8BE42931AE10069B5577B7C4D304")
    print(f"✅ Match: {signature == 'C7DD8BE42931AE10069B5577B7C4D304'}")
    
    return signature

def test_url_encoded():
    """Test with URL encoding"""
    print("\n🔧 Testing URL Encoded")
    print("=" * 30)
    
    params = {
        'merchant': 'RodolfHitler',
        'payment_type': '3',
        'amount': '100.00',
        'order_id': 'ORDER123456',
        'bank_code': 'gcash',
        'callback_url': 'https://yourwebsite.com/api/callback',
        'return_url': 'https://yourwebsite.com/deposit/success'
    }
    
    secret_key = '86cb40fe1666b41eb0ad21577d66baef'
    
    # URL encode values
    encoded_params = {}
    for key, value in params.items():
        encoded_params[key] = urllib.parse.quote(str(value))
    
    # Sort alphabetically
    sorted_params = dict(sorted(encoded_params.items()))
    
    query_parts = []
    for key, value in sorted_params.items():
        query_parts.append(f"{key}={value}")
    
    query_string = '&'.join(query_parts)
    sign_string = f"{query_string}&key={secret_key}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    print(f"🔐 Encoded params: {sorted_params}")
    print(f"🔐 Query string: {query_string}")
    print(f"🔐 Sign string: {sign_string}")
    print(f"🔐 Signature: {signature}")
    print(f"📋 Expected: C7DD8BE42931AE10069B5577B7C4D304")
    print(f"✅ Match: {signature == 'C7DD8BE42931AE10069B5577B7C4D304'}")
    
    return signature

def test_no_encoding():
    """Test with alphabetical order but no encoding of URLs"""
    print("\n🔧 Testing No URL Encoding (Alphabetical)")
    print("=" * 45)
    
    params = {
        'amount': '100.00',
        'bank_code': 'gcash', 
        'callback_url': 'https://yourwebsite.com/api/callback',
        'merchant': 'RodolfHitler',
        'order_id': 'ORDER123456',
        'payment_type': '3',
        'return_url': 'https://yourwebsite.com/deposit/success'
    }
    
    secret_key = '86cb40fe1666b41eb0ad21577d66baef'
    
    query_parts = []
    for key, value in params.items():
        query_parts.append(f"{key}={value}")
    
    query_string = '&'.join(query_parts)
    sign_string = f"{query_string}&key={secret_key}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    print(f"🔐 Query string: {query_string}")
    print(f"🔐 Sign string: {sign_string}")
    print(f"🔐 Signature: {signature}")
    print(f"📋 Expected: C7DD8BE42931AE10069B5577B7C4D304")
    print(f"✅ Match: {signature == 'C7DD8BE42931AE10069B5577B7C4D304'}")
    
    return signature

def test_with_working_signature():
    """Test with the expected signature directly"""
    print("\n🔧 Testing With Expected Signature")
    print("=" * 40)
    
    params = {
        'merchant': 'RodolfHitler',
        'payment_type': '3',
        'amount': '100.00',
        'order_id': 'ORDER123456',
        'bank_code': 'gcash',
        'callback_url': 'https://yourwebsite.com/api/callback',
        'return_url': 'https://yourwebsite.com/deposit/success',
        'sign': 'C7DD8BE42931AE10069B5577B7C4D304'
    }
    
    url = "https://cloud.la2568.site/api/transfer"
    response = requests.post(
        url,
        data=params,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30
    )
    
    print(f"📡 API Response Status: {response.status_code}")
    print(f"📄 API Response: {response.text}")
    
    return response.status_code == 200

if __name__ == "__main__":
    print("Testing Different Signature Methods for LA2568")
    print("=" * 60)
    
    sig1 = test_alphabetical_order()
    sig2 = test_url_encoded()
    sig3 = test_no_encoding()
    
    print(f"\n📊 SUMMARY:")
    print(f"Method 1 (Alphabetical): {sig1}")
    print(f"Method 2 (URL Encoded):   {sig2}")
    print(f"Method 3 (No Encoding):   {sig3}")
    print(f"Expected:                 C7DD8BE42931AE10069B5577B7C4D304")
    
    # Test with expected signature
    success = test_with_working_signature()
    
    if success:
        print(f"\n🎉 API accepts expected signature!")
    else:
        print(f"\n❌ API rejects even expected signature - may be merchant issue")
