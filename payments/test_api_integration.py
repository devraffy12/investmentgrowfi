#!/usr/bin/env python
"""
Test script for LA2568 API integration
"""
import hashlib
import requests
import json
from datetime import datetime

# LA2568 API Configuration
API_CONFIG = {
    'MERCHANT_KEY': '86cb40fe1666b41eb0ad21577d66baef',
    'SECRET_KEY': '86cb40fe1666b41eb0ad21577d66baef',
    'DEPOSIT_URL': 'https://cloud.la2568.site/api/transfer',
    'CALLBACK_URL': 'http://localhost:8000/payments/callback/',
    'RETURN_URL': 'http://localhost:8000/payment/success/'
}

def test_deposit_api():
    """Test deposit API call"""
    print("🧪 Testing LA2568 Deposit API...")
    
    # Generate test order
    order_id = f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Prepare payment data according to Galaxy API docs
    order_data = {
        'merchant': 'RodolfHitler',  # Use the actual merchant ID from settings
        'payment_type': '3',  # Fast Direct payment
        'amount': 100.00,  # Number type as per docs
        'order_id': order_id,
        'bank_code': 'gcash',
        'callback_url': API_CONFIG['CALLBACK_URL'],
        'return_url': API_CONFIG['RETURN_URL']
    }
    
    # Generate MD5 signature according to Galaxy docs
    # Sort parameters in ASCII ascending order
    sorted_params = sorted([(k, str(v)) for k, v in order_data.items() if v is not None])
    sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign_string += f"&key={API_CONFIG['SECRET_KEY']}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    order_data['sign'] = signature
    
    print(f"📝 Order ID: {order_id}")
    print(f"🔑 Sign String: {sign_string}")
    print(f"🔐 Signature: {signature}")
    print(f"📋 Request Data: {json.dumps(order_data, indent=2)}")
    
    try:
        # Make API request
        response = requests.post(
            API_CONFIG['DEPOSIT_URL'],
            data=order_data,
            timeout=30,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📋 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ JSON Response: {json.dumps(result, indent=2)}")
                
                # Check for success according to Galaxy docs: status = "1"
                if result.get('status') == '1' or result.get('status') == 1:
                    redirect_url = result.get('redirect_url') or result.get('qrcode_url')
                    if redirect_url:
                        print(f"🔗 Payment URL: {redirect_url}")
                        print("✅ Test successful! User should be redirected to GCash.")
                    else:
                        print("❌ No redirect URL in response")
                else:
                    print(f"❌ API Error: {result.get('message', 'Unknown error')}")
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")

def test_signature_verification():
    """Test signature verification"""
    print("\n🔐 Testing Signature Verification...")
    
    # Test callback data
    callback_data = {
        'order_id': 'TEST_20250819130000',
        'status': '1',
        'amount': '100.00',
        'merchant': API_CONFIG['MERCHANT_KEY']
    }
    
    # Generate signature
    sorted_params = sorted(callback_data.items())
    sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign_string += f"&key={API_CONFIG['SECRET_KEY']}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    
    print(f"📝 Callback Data: {json.dumps(callback_data, indent=2)}")
    print(f"🔑 Sign String: {sign_string}")
    print(f"🔐 Generated Signature: {signature}")
    
    # Verify signature
    callback_data['sign'] = signature
    received_sign = callback_data.get('sign', '')
    verify_data = {k: v for k, v in callback_data.items() if k != 'sign' and v}
    
    sorted_verify = sorted(verify_data.items())
    verify_string = '&'.join([f"{k}={v}" for k, v in sorted_verify])
    verify_string += f"&key={API_CONFIG['SECRET_KEY']}"
    expected_sign = hashlib.md5(verify_string.encode('utf-8')).hexdigest()
    
    if received_sign.lower() == expected_sign.lower():
        print("✅ Signature verification successful!")
    else:
        print(f"❌ Signature verification failed!")
        print(f"   Expected: {expected_sign}")
        print(f"   Received: {received_sign}")

if __name__ == "__main__":
    print("🚀 LA2568 API Integration Test")
    print("=" * 50)
    
    test_deposit_api()
    test_signature_verification()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("1. Check API response for success status")
    print("2. Verify redirect URL is returned")
    print("3. Test signature generation and verification")
    print("4. Monitor Django logs for detailed information")
