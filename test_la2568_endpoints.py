#!/usr/bin/env python3
"""
Test LA2568 API Endpoints to find the correct one
"""

import requests
import hashlib
import time
import json

def test_endpoints():
    """Test different possible API endpoints"""
    
    base_url = "https://cloud.la2568.site"
    
    # Possible API endpoints
    endpoints = [
        "/api/payment/create",
        "/api/payments/create", 
        "/api/deposit/create",
        "/api/deposit",
        "/api/payment",
        "/payment/create",
        "/create_payment",
        "/api/v1/payment/create",
        "/api/v1/payments/create",
        "/gateway/create",
        "/gateway/payment/create"
    ]
    
    # Test data
    test_data = {
        'amount': '100.00',
        'merchant_id': 'RodolfHitler',
        'order_id': f'TEST_{int(time.time())}',
        'bank_code': 'MAYA',
        'signature': 'test_signature',
        'return_url': 'https://test.com/success',
        'cancel_url': 'https://test.com/cancel',
        'notify_url': 'https://test.com/callback'
    }
    
    print("🔍 Testing LA2568 API Endpoints")
    print("=" * 60)
    
    for endpoint in endpoints:
        full_url = base_url + endpoint
        print(f"\n📡 Testing: {full_url}")
        
        try:
            response = requests.post(full_url, data=test_data, timeout=10)
            print(f"   Status: {response.status_code}")
            
            # Check if it's JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                try:
                    json_data = response.json()
                    print(f"   JSON Response: {json.dumps(json_data, indent=2)[:200]}...")
                    if response.status_code == 200:
                        print("   ✅ POSSIBLE WORKING ENDPOINT!")
                    elif 'error' in json_data or 'message' in json_data:
                        print("   ⚠️  Returns JSON error (might be correct endpoint)")
                except:
                    print("   ❌ Invalid JSON")
            else:
                print(f"   Content-Type: {content_type}")
                if response.status_code == 404:
                    print("   ❌ Not Found")
                elif response.status_code == 405:
                    print("   ⚠️  Method Not Allowed (endpoint exists but wrong method)")
                elif response.status_code < 500:
                    print("   ⚠️  Client error (might be correct endpoint)")
                else:
                    print("   ❌ Server error")
                    
        except requests.exceptions.Timeout:
            print("   ❌ Timeout")
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection Error")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 Testing GET requests to find API documentation")
    print("=" * 60)
    
    # Test GET requests for documentation
    doc_endpoints = [
        "/api",
        "/api/docs",
        "/docs", 
        "/documentation",
        "/api/v1",
        "/swagger",
        "/openapi.json"
    ]
    
    for endpoint in doc_endpoints:
        full_url = base_url + endpoint
        print(f"\n📖 Testing: {full_url}")
        
        try:
            response = requests.get(full_url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text[:200]
                if 'api' in content.lower() or 'payment' in content.lower() or 'swagger' in content.lower():
                    print(f"   ✅ FOUND DOCUMENTATION!")
                    print(f"   Content preview: {content}...")
            elif response.status_code == 404:
                print("   ❌ Not Found")
            else:
                print(f"   ⚠️  Status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints()
