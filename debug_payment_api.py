#!/usr/bin/env python
"""
Debug script for LA2568 payment integration
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
from django.utils import timezone

def test_la2568_api():
    """Test LA2568 API with your exact credentials"""
    print("🔍 Testing LA2568 Payment API")
    print("=" * 50)
    
    config = settings.PAYMENT_API_CONFIG
    
    print(f"Merchant ID: {config['MERCHANT_ID']}")
    print(f"Secret Key: {config['SECRET_KEY'][:10]}...")
    print(f"API URL: {config['DEPOSIT_URL']}")
    print(f"Callback URL: {config['CALLBACK_URL']}")
    
    # Test order data
    order_id = f"TEST{timezone.now().strftime('%Y%m%d%H%M%S')}0001"
    
    order_data = {
        'merchant': config['MERCHANT_ID'],      # RodolfHitler
        'payment_type': '3',                    # Third party payment
        'amount': 100.00,                       # Test amount ₱100
        'order_id': order_id,                   # Unique order ID
        'bank_code': 'gcash',                   # GCash payment
        'callback_url': config['CALLBACK_URL'], # Your callback URL
        'return_url': config['SUCCESS_URL']     # Your return URL
    }
    
    print(f"\n📝 Order data: {order_data}")
    
    # Generate signature
    sorted_params = sorted([(k, str(v)) for k, v in order_data.items() if v is not None])
    sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    sign_string += f"&key={config['SECRET_KEY']}"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    order_data['sign'] = signature
    
    print(f"\n🔐 Sign string: {sign_string}")
    print(f"🔐 Signature: {signature}")
    print(f"\n📤 Final request: {order_data}")
    
    # Make API request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/html, */*'
    }
    
    try:
        print(f"\n📡 Sending request to: {config['DEPOSIT_URL']}")
        response = requests.post(
            config['DEPOSIT_URL'],
            data=order_data,
            timeout=30,
            headers=headers,
            allow_redirects=False
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Body:")
        print("-" * 30)
        print(response.text)
        print("-" * 30)
        
        # Try to parse as JSON
        try:
            result = response.json()
            print(f"\n✅ JSON Response: {json.dumps(result, indent=2)}")
            
            # Check for success indicators
            if (result.get('status') == 'success' or 
                result.get('status') == '1' or 
                result.get('code') == '200' or
                'payment_url' in result or
                'redirect_url' in result):
                print("✅ API call appears successful!")
                
                # Look for payment URL
                payment_url = (
                    result.get('payment_url') or 
                    result.get('redirect_url') or
                    result.get('qr_code_url') or
                    (result.get('data', {}).get('payment_url') if isinstance(result.get('data'), dict) else None)
                )
                
                if payment_url:
                    print(f"🔗 Payment URL: {payment_url}")
                else:
                    print("⚠️ No payment URL found in response")
                    print(f"Available keys: {list(result.keys())}")
            else:
                print("❌ API call failed")
                error_msg = result.get('message', result.get('msg', result.get('error', 'Unknown error')))
                print(f"Error: {error_msg}")
                
        except json.JSONDecodeError:
            print("⚠️ Response is not JSON")
            
            # Check for common errors in HTML response
            error_checks = [
                ("Merchant does not exist", "❌ Merchant not registered"),
                ("Invalid signature", "❌ Signature error"),
                ("Missing required fields", "❌ Missing fields"),
                ("Parameter error", "❌ Parameter format error")
            ]
            
            for error_text, error_desc in error_checks:
                if error_text.lower() in response.text.lower():
                    print(f"{error_desc}: Found '{error_text}' in response")
                    break
        
        # Handle redirect responses
        if response.status_code == 302:
            redirect_url = response.headers.get('Location')
            if redirect_url:
                print(f"🔀 Redirect to: {redirect_url}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_connection():
    """Test basic connection to LA2568"""
    print("\n🌐 Testing basic connection...")
    try:
        response = requests.get("https://cloud.la2568.site", timeout=10)
        print(f"✅ Base URL accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
    test_la2568_api()
