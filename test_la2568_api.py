#!/usr/bin/env python
"""
Simple test script for LA2568 API integration
"""
import requests
import hashlib
import json
from datetime import datetime

# Your LA2568 credentials
MERCHANT_ID = 'RodolfHitler'
SECRET_KEY = '86cb40fe1666b41eb0ad21577d66baef'
API_URL = 'https://cloud.la2568.site/api/transfer'

def test_la2568_api():
    """Test LA2568 API with sample data"""
    print("🚀 Testing LA2568 API Integration")
    print("=" * 50)
    
    # Sample order data
    order_id = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    order_data = {
        'merchant': MERCHANT_ID,
        'payment_type': '1',  # GCash QR (updated per LA2568 instructions)
        'amount': '100.00',   # Test amount
        'order_id': order_id,
        'bank_code': 'gcash', # Updated to lowercase per LA2568 instructions
        'callback_url': 'http://localhost:8000/payment/callback/',
        'return_url': 'http://localhost:8000/payment/success/'
    }
    
    print(f"📝 Order Data: {order_data}")
    
    # Generate signature
    sorted_params = sorted(order_data.items())
    sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign_string += f"&key={SECRET_KEY}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    
    order_data['sign'] = signature
    
    print(f"🔐 Sign String: {sign_string}")
    print(f"🔐 Signature: {signature}")
    print(f"📤 Final Data: {order_data}")
    
    # Make API request
    try:
        print(f"\n📡 Sending request to: {API_URL}")
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.post(
            API_URL,
            data=order_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ JSON Response: {json.dumps(result, indent=2)}")
                
                if result.get('status') == 1:
                    print("✅ API call successful!")
                    payment_url = result.get('payment_url') or result.get('payurl')
                    if payment_url:
                        print(f"🔗 Payment URL: {payment_url}")
                    else:
                        print("❌ No payment URL in response")
                else:
                    print(f"❌ API Error: {result.get('msg', 'Unknown error')}")
            except json.JSONDecodeError:
                print(f"❌ Non-JSON response: {response.text}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_la2568_api()
