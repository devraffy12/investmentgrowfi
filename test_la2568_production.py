#!/usr/bin/env python3
"""
Test LA2568 Production Integration
Tests the LA2568 API with production configuration to verify payment gateway functionality
"""

import os
import sys
import django
import hashlib
import time
import requests
import json

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.conf import settings
from payments.models import Transaction

def test_la2568_config():
    """Test LA2568 configuration"""
    print("=" * 60)
    print("TESTING LA2568 PRODUCTION CONFIGURATION")
    print("=" * 60)
    
    # Test config access
    try:
        config = getattr(settings, 'PAYMENT_API_CONFIG', None)
        if config:
            print("✓ PAYMENT_API_CONFIG found in settings")
            print(f"  Base URL: {config.get('base_url', 'NOT FOUND')}")
            print(f"  Merchant ID: {config.get('merchant_id', 'NOT FOUND')}")
            print(f"  API Key: {'*' * len(config.get('api_key', '')) if config.get('api_key') else 'NOT FOUND'}")
        else:
            print("✗ PAYMENT_API_CONFIG not found in settings")
            print("Using fallback configuration...")
            config = {
                'base_url': 'https://cloud.la2568.site',
                'merchant_id': 'RodolfHitler',
                'api_key': '86cb40fe1666b41eb0ad21577d66baef'
            }
            print(f"  Fallback Base URL: {config['base_url']}")
            print(f"  Fallback Merchant ID: {config['merchant_id']}")
            print(f"  Fallback API Key: {'*' * len(config['api_key'])}")
    except Exception as e:
        print(f"✗ Error accessing config: {e}")
        return False
    
    return config

def generate_signature(amount, merchant_id, order_id, api_key):
    """Generate LA2568 signature"""
    # Create signature string: amount + merchant_id + order_id + api_key
    signature_string = f"{amount}{merchant_id}{order_id}{api_key}"
    # Generate MD5 hash
    signature = hashlib.md5(signature_string.encode()).hexdigest()
    return signature

def test_la2568_api(config):
    """Test LA2568 API call"""
    print("\n" + "=" * 60)
    print("TESTING LA2568 API CALL")
    print("=" * 60)
    
    # Test parameters
    amount = "100.00"
    order_id = f"TEST_{int(time.time())}"
    bank_code = "MAYA"
    
    try:
        # Generate signature
        signature = generate_signature(amount, config['merchant_id'], order_id, config['api_key'])
        print(f"✓ Generated signature: {signature}")
        
        # Prepare API payload
        payload = {
            'amount': amount,
            'merchant_id': config['merchant_id'],
            'order_id': order_id,
            'bank_code': bank_code,
            'signature': signature,
            'return_url': 'https://your-site.com/payment/success/',
            'cancel_url': 'https://your-site.com/payment/cancel/',
            'notify_url': 'https://your-site.com/payment/callback/'
        }
        
        print(f"✓ API Payload prepared:")
        for key, value in payload.items():
            if key == 'signature':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        
        # Make API request
        api_url = f"{config['base_url']}/api/payment/create"
        print(f"\n✓ Making request to: {api_url}")
        
        response = requests.post(api_url, data=payload, timeout=30)
        
        print(f"✓ Response Status: {response.status_code}")
        print(f"✓ Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"✓ Response JSON: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                payment_url = response_data.get('payment_url')
                if payment_url:
                    print(f"\n🎉 SUCCESS! Payment URL generated: {payment_url}")
                    return True
                else:
                    print(f"\n❌ No payment URL in response")
                    return False
            else:
                print(f"\n❌ API returned error: {response_data}")
                return False
                
        except json.JSONDecodeError:
            print(f"✗ Response is not valid JSON: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_bank_codes(config):
    """Test different bank codes"""
    print("\n" + "=" * 60)
    print("TESTING DIFFERENT BANK CODES")
    print("=" * 60)
    
    bank_codes = ['MAYA', 'GCSH']
    
    for bank_code in bank_codes:
        print(f"\n--- Testing {bank_code} ---")
        amount = "50.00"
        order_id = f"TEST_{bank_code}_{int(time.time())}"
        
        try:
            signature = generate_signature(amount, config['merchant_id'], order_id, config['api_key'])
            
            payload = {
                'amount': amount,
                'merchant_id': config['merchant_id'],
                'order_id': order_id,
                'bank_code': bank_code,
                'signature': signature,
                'return_url': 'https://your-site.com/payment/success/',
                'cancel_url': 'https://your-site.com/payment/cancel/',
                'notify_url': 'https://your-site.com/payment/callback/'
            }
            
            api_url = f"{config['base_url']}/api/payment/create"
            response = requests.post(api_url, data=payload, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'success':
                        print(f"  ✓ {bank_code}: SUCCESS - {data.get('payment_url', 'No URL')}")
                    else:
                        print(f"  ✗ {bank_code}: FAILED - {data}")
                except:
                    print(f"  ✗ {bank_code}: Invalid JSON response")
            else:
                print(f"  ✗ {bank_code}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ {bank_code}: Error - {e}")

def main():
    """Main test function"""
    print("🚀 Starting LA2568 Production Test")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test configuration
    config = test_la2568_config()
    if not config:
        print("\n❌ Configuration test failed!")
        return
    
    # Test basic API call
    api_success = test_la2568_api(config)
    
    # Test different bank codes
    test_bank_codes(config)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    if api_success:
        print("🎉 LA2568 API integration is working!")
        print("✓ Configuration loaded successfully")
        print("✓ API requests are successful")
        print("✓ Payment URLs are being generated")
        print("\nThe production error might be related to:")
        print("1. Different environment settings in production")
        print("2. Network connectivity issues")
        print("3. Different Django settings configuration")
    else:
        print("❌ LA2568 API integration has issues")
        print("Please check the API credentials and network connectivity")

if __name__ == "__main__":
    main()
