#!/usr/bin/env python
"""
Debug LA2568 API Response in Detail
"""

import requests
import hashlib
import base64
import json

def decode_error_message():
    """Decode the base64 error message"""
    print("🔍 Decoding Error Message")
    print("=" * 30)
    
    error_code = "QXBpQ29udHJvbGxlci5waHA="
    decoded = base64.b64decode(error_code).decode('utf-8')
    print(f"📄 Error code: {error_code}")
    print(f"📄 Decoded: {decoded}")
    print(f"📄 Number: 1937")
    
    # This suggests the error is coming from ApiController.php line 1937

def test_minimal_request():
    """Test with minimal required parameters"""
    print("\n🔧 Testing Minimal Request")
    print("=" * 30)
    
    params = {
        'merchant': 'RodolfHitler',
        'payment_type': '3',
        'amount': '100.00',
        'order_id': 'TEST123',
        'bank_code': 'gcash'
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
    
    params['sign'] = signature
    
    print(f"🔐 Parameters: {params}")
    print(f"🔐 Signature: {signature}")
    
    url = "https://cloud.la2568.site/api/transfer"
    response = requests.post(
        url,
        data=params,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30
    )
    
    print(f"📡 Status: {response.status_code}")
    print(f"📄 Response: {response.text}")
    
    return response

def test_different_merchant():
    """Test if the merchant ID is the issue"""
    print("\n🔧 Testing Different Merchant Format")
    print("=" * 40)
    
    # Try different merchant formats
    merchants = ['RodolfHitler', 'rodolfhitler', 'RODOLFHITLER']
    
    for merchant in merchants:
        print(f"\n🧪 Testing merchant: {merchant}")
        
        params = {
            'merchant': merchant,
            'payment_type': '3',
            'amount': '100.00',
            'order_id': 'TEST123',
            'bank_code': 'gcash'
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
        
        params['sign'] = signature
        
        url = "https://cloud.la2568.site/api/transfer"
        response = requests.post(
            url,
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"  📡 Status: {response.status_code}")
        print(f"  📄 Response: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('status') == '1':
                    print(f"  🎉 SUCCESS with merchant: {merchant}")
                    return True
            except:
                pass

def test_api_status():
    """Test if the API endpoint is working at all"""
    print("\n🔧 Testing API Status")
    print("=" * 25)
    
    # Try GET request to see if endpoint exists
    url = "https://cloud.la2568.site/api/transfer"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📡 GET Status: {response.status_code}")
        print(f"📄 GET Response: {response.text}")
    except Exception as e:
        print(f"❌ GET Error: {e}")
    
    # Try POST with no data
    try:
        response = requests.post(url, data={}, timeout=10)
        print(f"📡 Empty POST Status: {response.status_code}")
        print(f"📄 Empty POST Response: {response.text}")
    except Exception as e:
        print(f"❌ Empty POST Error: {e}")

if __name__ == "__main__":
    print("🔍 Debugging LA2568 API Issues")
    print("=" * 50)
    
    decode_error_message()
    
    response = test_minimal_request()
    
    test_different_merchant()
    
    test_api_status()
    
    print(f"\n📝 CONCLUSIONS:")
    print(f"   - API returns 200 status but 'Sign Error' message")
    print(f"   - Error comes from ApiController.php line 1937")
    print(f"   - Even specification example fails")
    print(f"   - May be merchant credential or API configuration issue")
    print(f"   - Recommend contacting LA2568 support for verification")
