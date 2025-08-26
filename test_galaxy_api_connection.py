#!/usr/bin/env python3
"""
Test script for Galaxy LA2568 API connection
"""
import requests
import hashlib
import json
from decimal import Decimal

# LA2568 API Configuration
API_BASE_URL = "https://cloud.la2568.site"
MERCHANT_ID = "RodolfHitler"
SECRET_KEY = "86cb40fe1666b41eb0ad21577d66baef"

def generate_signature(params, secret_key):
    """Generate Galaxy API MD5 signature"""
    # Remove sign parameter if present
    filtered_params = {k: v for k, v in params.items() if k != 'sign' and v is not None}
    
    # Sort parameters in ASCII ascending order
    sorted_params = sorted(filtered_params.items())
    
    # Create query string
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    
    # Add secret key at the end
    sign_string = f"{query_string}&key={secret_key}"
    
    print(f"Sign string: {sign_string}")
    
    # Generate MD5 hash
    signature = hashlib.md5(sign_string.encode("utf-8")).hexdigest()
    return signature

def test_merchant_balance():
    """Test merchant balance endpoint"""
    print("🔍 Testing merchant balance endpoint...")
    
    params = {
        'merchant': MERCHANT_ID,
    }
    
    params['sign'] = generate_signature(params, SECRET_KEY)
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/me",
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"JSON Response: {json.dumps(json_response, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_payment_creation():
    """Test payment creation"""
    print("\n💳 Testing payment creation...")
    
    params = {
        'merchant': MERCHANT_ID,
        'payment_type': '2',  # WEB_H5
        'amount': '100.00',
        'order_id': 'TEST_12345',
        'bank_code': 'gcash',
        'callback_url': 'http://127.0.0.1:8000/api/galaxy/callback/',
        'return_url': 'http://127.0.0.1:8000/payment/success/',
    }
    
    params['sign'] = generate_signature(params, SECRET_KEY)
    
    print(f"Request params: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/transfer",
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"JSON Response: {json.dumps(json_response, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("🚀 Galaxy LA2568 API Test")
    print("=" * 50)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Merchant ID: {MERCHANT_ID}")
    print(f"Secret Key: {SECRET_KEY[:10]}...")
    print("=" * 50)
    
    # Test API connection
    print("\n📡 Testing API connection...")
    try:
        response = requests.get(API_BASE_URL, timeout=10)
        print(f"✅ API is reachable - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ API is not reachable: {e}")
        return
    
    # Test merchant balance endpoint
    balance_ok = test_merchant_balance()
    
    # Test payment creation if balance check works
    if balance_ok:
        test_payment_creation()
    else:
        print("\n⚠️ Skipping payment test due to balance check failure")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()
