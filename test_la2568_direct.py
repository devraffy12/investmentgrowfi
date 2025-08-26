#!/usr/bin/env python3
"""
Direct test of LA2568 API without Django
Run: python test_la2568_direct.py
"""
import requests
import hashlib
import json

# LA2568 API Configuration
MERCHANT_ID = "RodolfHitler"
SECRET_KEY = "86cb40fe1666b41eb0ad21577d66baef"
BASE_URL = "https://cloud.la2568.site"
DEPOSIT_URL = f"{BASE_URL}/api/transfer"

def generate_signature(params, secret_key):
    """Generate LA2568 signature"""
    # Use LA2568 specification order for deposit
    ordered_keys = ['merchant', 'payment_type', 'amount', 'order_id', 'bank_code', 'callback_url', 'return_url']
    parts = []
    for key in ordered_keys:
        if key in params:
            parts.append(f"{key}={params[key]}")
    query_string = '&'.join(parts)
    sign_string = f"{query_string}&key={secret_key}"
    print(f"🔐 Sign string: {sign_string}")
    return hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()

def test_la2568_deposit():
    """Test LA2568 deposit API"""
    
    # Test parameters
    params = {
        "merchant": MERCHANT_ID,
        "payment_type": "2",
        "amount": "100.00",
        "order_id": "TEST_12345",
        "bank_code": "gcash",
        "callback_url": "http://127.0.0.1:8000/api/callback",
        "return_url": "http://127.0.0.1:8000/payment/success/"
    }
    
    # Generate signature
    signature = generate_signature(params, SECRET_KEY)
    params["sign"] = signature
    
    print(f"🚀 Testing LA2568 API at {DEPOSIT_URL}")
    print(f"📋 Request params: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.post(
            DEPOSIT_URL,
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Body: {response.text}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"✅ JSON Response: {json.dumps(json_response, indent=2)}")
            except json.JSONDecodeError:
                print(f"⚠️  Non-JSON response (possibly HTML or plain text)")
                
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

if __name__ == "__main__":
    print("🔥 LA2568 Direct API Test")
    print("=" * 50)
    test_la2568_deposit()
