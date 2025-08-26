#!/usr/bin/env python3
"""
Test CloudPay parameters quickly
"""
import requests
import hashlib
import json

# LA2568 API Configuration
API_BASE_URL = "https://cloud.la2568.site"
MERCHANT_ID = "RodolfHitler"
SECRET_KEY = "86cb40fe1666b41eb0ad21577d66baef"

def generate_signature(params, secret_key):
    """Generate Galaxy API MD5 signature"""
    filtered_params = {k: v for k, v in params.items() if k != 'sign' and v is not None}
    sorted_params = sorted(filtered_params.items())
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    sign_string = f"{query_string}&key={secret_key}"
    signature = hashlib.md5(sign_string.encode("utf-8")).hexdigest()
    return signature

def test_cloudpay_method(bank_code, payment_type, method_name):
    """Test CloudPay method"""
    print(f"\n💳 Testing {method_name}")
    print(f"   bank_code={bank_code}, payment_type={payment_type}")
    
    params = {
        'merchant': MERCHANT_ID,
        'payment_type': payment_type,
        'amount': '100.00',
        'order_id': f'TEST_{method_name.replace(" ", "")}_12345',
        'bank_code': bank_code,
        'callback_url': 'http://127.0.0.1:8000/api/galaxy/callback/',
        'return_url': 'http://127.0.0.1:8000/payment/success/',
    }
    
    params['sign'] = generate_signature(params, SECRET_KEY)
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/transfer",
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                if json_response.get('status') == '1':
                    print(f"   ✅ SUCCESS! Payment URL available")
                    if 'redirect_url' in json_response:
                        print(f"   🔗 Redirect: {json_response['redirect_url'][:50]}...")
                    return True
                else:
                    print(f"   ❌ FAILED: {json_response.get('message', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🚀 Testing CloudPay Methods")
    print("=" * 60)
    
    # CloudPay methods from Telegram response
    methods = [
        ('gcash', '1', 'GCash QR'),
        ('mya', '7', 'GCash H5 QRPH'), 
        ('PMP', '3', 'PayMaya Direct'),
    ]
    
    working_methods = []
    
    for bank_code, payment_type, method_name in methods:
        if test_cloudpay_method(bank_code, payment_type, method_name):
            working_methods.append(method_name)
    
    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    if working_methods:
        print(f"✅ Working methods: {', '.join(working_methods)}")
        print("\n🎉 Ready to test sa Django app!")
        print("👉 Go to http://127.0.0.1:8000/deposit/ and try a payment")
    else:
        print("❌ Still having issues - contact CloudPay again")

if __name__ == "__main__":
    main()
