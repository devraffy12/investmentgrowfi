#!/usr/bin/env python
"""
Test Exact LA2568 Specification
"""

import requests
import hashlib

def test_exact_specification():
    """Test the exact parameters from LA2568 specification"""
    print("🔧 Testing Exact LA2568 Specification")
    print("=" * 50)
    
    # Exact parameters from your specification
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
    
    # Generate signature exactly as in specification
    query_parts = []
    for key, value in params.items():
        query_parts.append(f"{key}={value}")
    
    query_string = '&'.join(query_parts)
    sign_string = f"{query_string}&key={secret_key}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    print(f"📋 Parameters: {params}")
    print(f"🔐 Query string: {query_string}")
    print(f"🔐 Sign string: {sign_string}")
    print(f"🔐 Signature: {signature}")
    
    # Expected signature from specification
    expected = "C7DD8BE42931AE10069B5577B7C4D304"
    print(f"📋 Expected: {expected}")
    print(f"✅ Match: {signature == expected}")
    
    if signature == expected:
        print(f"\n✅ Signature matches! Testing API call...")
        
        # Add signature to params
        params['sign'] = signature
        
        # Make API call
        url = "https://cloud.la2568.site/api/transfer"
        response = requests.post(
            url,
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"📡 API Response Status: {response.status_code}")
        print(f"📄 API Response: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('status') == '1':
                    print(f"🎉 SUCCESS! Got redirect URL: {result.get('redirect_url')}")
                    return True
                else:
                    print(f"❌ API Error: {result.get('message')}")
            except:
                print(f"❌ Invalid JSON response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    
    return False

if __name__ == "__main__":
    success = test_exact_specification()
    
    if success:
        print(f"\n🎯 LA2568 API works with specification example!")
    else:
        print(f"\n🔧 Need to check merchant credentials or API status.")
