#!/usr/bin/env python
"""
Simple test for LA2568 payment integration
"""
import os
import sys
import django
import requests
import hashlib
import json
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.conf import settings

def test_la2568_deposit():
    """Test LA2568 deposit API with your credentials"""
    print("🔍 Testing LA2568 Deposit API Integration")
    print("=" * 50)
    
    config = settings.PAYMENT_API_CONFIG
    
    print(f"API URL: {config['DEPOSIT_URL']}")
    print(f"Merchant ID: {config['MERCHANT_ID']}")
    print(f"Secret Key: {config['SECRET_KEY'][:10]}...")
    
    # Test order data
    order_data = {
        'merchant': config['MERCHANT_ID'],           # RodolfHitler
        'payment_type': '3',                         # Third party payment
        'amount': '100.00',                          # Test amount (string format)
        'order_id': 'TEST20250819134500123',         # Test order ID
        'bank_code': 'GCASH',                        # GCash payment
        'callback_url': config['CALLBACK_URL'],     # Your callback URL
        'return_url': config['SUCCESS_URL'],        # Your return URL
        'notify_url': config['NOTIFY_URL']          # Your notify URL
    }
    
    print(f"\n📤 Request Data:")
    for key, value in order_data.items():
        print(f"  {key}: {value}")
    
    # Generate signature
    sorted_params = sorted(order_data.items())
    sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign_string += f"&key={config['SECRET_KEY']}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    order_data['sign'] = signature
    
    print(f"\n🔐 Signature Generation:")
    print(f"  Sign String: {sign_string}")
    print(f"  MD5 Hash: {signature}")
    
    # Make API request
    print(f"\n📡 Making API Request...")
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.post(
            config['DEPOSIT_URL'],
            data=order_data,
            timeout=30,
            headers=headers
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Content Type: {response.headers.get('content-type', 'unknown')}")
        
        # Print first 1000 characters of response
        response_text = response.text
        print(f"📥 Response Body (first 1000 chars):")
        print("-" * 50)
        print(response_text[:1000])
        if len(response_text) > 1000:
            print("... (truncated)")
        print("-" * 50)
        
        # Try to parse as JSON
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                print(f"\n✅ JSON Response:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                if result.get('status') == 'success' or result.get('code') == '200':
                    print("\n🎉 SUCCESS: Payment order created!")
                    payment_url = result.get('data', {}).get('payment_url') or result.get('payment_url')
                    if payment_url:
                        print(f"💳 Payment URL: {payment_url}")
                else:
                    print(f"\n❌ API Error: {result.get('message', 'Unknown error')}")
            else:
                print(f"\n⚠️ Non-JSON response received")
                
                # Check for common error patterns
                if "Merchant does not exist" in response_text:
                    print("❌ ERROR: Merchant not registered with LA2568")
                    print("🔧 SOLUTION: Contact LA2568 support to register your merchant account")
                elif "Invalid signature" in response_text:
                    print("❌ ERROR: Signature verification failed")
                    print("🔧 SOLUTION: Check your secret key and signature generation")
                elif "Missing required fields" in response_text:
                    print("❌ ERROR: Required fields missing")
                    print("🔧 SOLUTION: Check all required parameters are included")
                    
        except json.JSONDecodeError:
            print(f"\n⚠️ Could not parse response as JSON")
        
        if response.status_code == 200:
            print(f"\n✅ HTTP Request Successful")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_la2568_deposit()
