#!/usr/bin/env python3
"""
Test script to verify LA2568 payment API integration
This will test the actual API call to ensure redirect URLs are generated correctly
"""

import os
import sys
import django
import hashlib
import requests
from decimal import Decimal
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from payments.la2568_service import la2568_service

def test_la2568_api_direct():
    """Test direct LA2568 API call"""
    print("🔥 Testing Direct LA2568 API Call")
    print("=" * 50)
    
    # Test parameters
    test_amount = Decimal('500.00')
    test_order_id = f"TEST_{int(time.time())}"
    
    print(f"Amount: ₱{test_amount}")
    print(f"Order ID: {test_order_id}")
    print(f"Payment Method: GCash")
    print()
    
    # Prepare API parameters
    api_params = {
        'merchant': 'RodolfHitler',
        'payment_type': '1',  # QR Code deposit
        'amount': f"{float(test_amount):.2f}",
        'order_id': test_order_id,
        'bank_code': 'gcash',
        'callback_url': 'http://localhost:8000/payments/callback/',
        'return_url': 'http://localhost:8000/payments/success/'
    }
    
    # Generate signature
    sorted_params = sorted(api_params.items())
    query_string = '&'.join([f"{key}={value}" for key, value in sorted_params])
    sign_string = f"{query_string}&key=86cb40fe1666b41eb0ad21577d66baef"
    signature = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    api_params['sign'] = signature
    
    print("📤 API Request Parameters:")
    for key, value in api_params.items():
        if key == 'sign':
            print(f"  {key}: {value[:20]}...")
        else:
            print(f"  {key}: {value}")
    print()
    
    try:
        # Make API call
        print("🚀 Making API call to LA2568...")
        response = requests.post(
            'https://cloud.la2568.site/api/transfer',
            data=api_params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"� Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("📋 Response Data:")
                for key, value in result.items():
                    print(f"  {key}: {value}")
                
                # Check for redirect URL
                if result.get('redirect_url'):
                    print(f"\n✅ SUCCESS! Redirect URL received:")
                    print(f"🔗 {result['redirect_url']}")
                    
                    # Test if the URL is accessible
                    print(f"\n🧪 Testing redirect URL accessibility...")
                    try:
                        test_response = requests.head(result['redirect_url'], timeout=10)
                        print(f"✅ Redirect URL is accessible (Status: {test_response.status_code})")
                    except Exception as e:
                        print(f"⚠️ Redirect URL test failed: {e}")
                        
                else:
                    print(f"\n❌ No redirect_url in response")
                    
            except ValueError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response.text[:500]}")
                
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Exception during API call: {e}")


def test_la2568_service():
    """Test using the LA2568 service class"""
    print("\n\n🔧 Testing LA2568 Service Class")
    print("=" * 50)
    
    test_amount = Decimal('1000.00')
    test_order_id = f"SERVICE_TEST_{int(time.time())}"
    
    print(f"Amount: ₱{test_amount}")
    print(f"Order ID: {test_order_id}")
    
    try:
        # Test service configuration
        config_status = la2568_service.get_config_status()
        print(f"\n📊 Service Configuration:")
        for key, value in config_status.items():
            print(f"  {key}: {value}")
        
        # Test deposit creation
        print(f"\n🚀 Creating deposit via service...")
        result = la2568_service.create_deposit(
            amount=test_amount,
            order_id=test_order_id,
            payment_method='gcash'
        )
        
        print(f"📋 Service Response:")
        for key, value in result.items():
            if key == 'raw_response':
                print(f"  {key}: {type(value).__name__}")
            else:
                print(f"  {key}: {value}")
        
        if result.get('redirect_url'):
            print(f"\n✅ SUCCESS! Service returned redirect URL:")
            print(f"🔗 {result['redirect_url']}")
        else:
            print(f"\n❌ No redirect_url from service")
            
    except Exception as e:
        print(f"❌ Exception in service test: {e}")


def test_payment_flow():
    """Test the complete payment flow"""
    print("\n\n🎯 Testing Complete Payment Flow")
    print("=" * 50)
    
    # This simulates what happens when user clicks "Pay with GCash"
    test_cases = [
        {'amount': Decimal('500.00'), 'method': 'gcash'},
        {'amount': Decimal('1000.00'), 'method': 'gcash'},
        {'amount': Decimal('250.00'), 'method': 'maya'},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {case['method'].upper()} - ₱{case['amount']}")
        print("-" * 40)
        
        order_id = f"FLOW_TEST_{i}_{int(time.time())}"
        
        result = la2568_service.create_deposit(
            amount=case['amount'],
            order_id=order_id,
            payment_method=case['method']
        )
        
        if result.get('success'):
            print(f"✅ Payment creation successful")
            if result.get('redirect_url'):
                print(f"✅ Redirect URL: {result['redirect_url'][:60]}...")
            else:
                print(f"⚠️ No redirect URL")
        else:
            print(f"❌ Payment creation failed: {result.get('message', 'Unknown error')}")


if __name__ == "__main__":
    print("🧪 LA2568 Payment API Integration Test")
    print("=" * 60)
    
    # Run tests
    test_la2568_api_direct()
    test_la2568_service() 
    test_payment_flow()
    
    print("\n\n🏁 Testing completed!")
    print("=" * 60)
    print("\n💡 If you see redirect URLs in the results above, your integration is working!")
    print("💡 If you see errors, check your merchant credentials with LA2568 support.")
    print("\n� Next Steps:")
    print("1. If you get valid redirect URLs, users will be sent directly to GCash payment page")
    print("2. If you get 'Merchant does not exist' error, contact LA2568 support to activate your account")
    print("3. Test the payment flow on your website at http://localhost:8000/deposit/")
