#!/usr/bin/env python3
"""
Test script for Galaxy API callback endpoint
This script simulates the callback that Galaxy API sends to verify the response format
"""

import requests
import json
import hashlib
from datetime import datetime

def generate_galaxy_signature(params, secret_key):
    """Generate Galaxy API MD5 signature"""
    # Remove sign parameter
    filtered_params = {k: v for k, v in params.items() if k != 'sign' and v is not None}
    
    # Use alphabetical order
    ordered_keys = sorted(filtered_params.keys())
    
    # Create query string
    query_parts = []
    for key in ordered_keys:
        query_parts.append(f"{key}={filtered_params[key]}")
    
    query_string = '&'.join(query_parts)
    sign_string = f"{query_string}&key={secret_key}"
    
    # Generate MD5 hash - lowercase
    signature = hashlib.md5(sign_string.encode("utf-8")).hexdigest().lower()
    return signature

def test_callback_endpoint():
    """Test the Galaxy callback endpoint"""
    
    # Galaxy API configuration
    merchant_id = 'RodolfHitler'
    secret_key = '86cb40fe1666b41eb0ad21577d66baef'
    
    # Test callback data (similar to what Galaxy sends)
    callback_data = {
        'merchant': merchant_id,
        'order_id': 'DEP_62_1756076135',  # Same as in your message
        'amount': '300.0000',
        'status': '5',  # Success status
        'message': '成功'  # Success message in Chinese
    }
    
    # Generate signature
    callback_data['sign'] = generate_galaxy_signature(callback_data, secret_key)
    
    print("=== TESTING GALAXY CALLBACK ENDPOINT ===")
    print(f"Timestamp: {datetime.now()}")
    print(f"Test Data: {json.dumps(callback_data, indent=2, ensure_ascii=False)}")
    
    # Test URLs
    test_urls = [
        'http://127.0.0.1:8000/payment/api/galaxy/callback/',
        'http://127.0.0.1:8000/payment/api/callback/',
        'http://127.0.0.1:8000/payment/api/test-callback/'
    ]
    
    for url in test_urls:
        print(f"\n--- Testing URL: {url} ---")
        
        try:
            # Send POST request with form data (same as Galaxy API)
            response = requests.post(
                url,
                data=callback_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Content: {response.text}")
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            # Check if response is what Galaxy expects
            if response.status_code == 200 and response.text.strip().upper() == "SUCCESS":
                print("✅ CORRECT: Returns 'SUCCESS' as expected by Galaxy API")
            else:
                print("❌ INCORRECT: Galaxy API expects 'SUCCESS' as plain text response")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ REQUEST FAILED: {str(e)}")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n=== TEST COMPLETED ===")
    print("Expected Galaxy response: HTTP 200 with 'SUCCESS' as plain text")
    print("If you see 'SUCCESS' response, the callback should work with Galaxy API")

if __name__ == "__main__":
    test_callback_endpoint()
