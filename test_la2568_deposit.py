#!/usr/bin/env python3
"""
Test LA2568 /api/deposit endpoint with proper parameters
"""

import requests
import hashlib
import time
import json

def generate_signature(amount, merchant_id, order_id, api_key):
    """Generate LA2568 signature"""
    signature_string = f"{amount}{merchant_id}{order_id}{api_key}"
    signature = hashlib.md5(signature_string.encode()).hexdigest()
    return signature

def test_deposit_endpoint():
    """Test the /api/deposit endpoint with various parameters"""
    
    base_url = "https://cloud.la2568.site"
    endpoint = "/api/deposit"
    
    config = {
        'merchant_id': 'RodolfHitler',
        'api_key': '86cb40fe1666b41eb0ad21577d66baef'
    }
    
    print("🧪 Testing LA2568 /api/deposit endpoint")
    print("=" * 60)
    
    # Test different parameter combinations
    test_cases = [
        {
            'name': 'Basic parameters with MAYA',
            'data': {
                'amount': '100.00',
                'merchant_id': config['merchant_id'],
                'order_id': f'TEST_MAYA_{int(time.time())}',
                'bank_code': 'MAYA',
                'return_url': 'https://test.com/success',
                'cancel_url': 'https://test.com/cancel',
                'notify_url': 'https://test.com/callback'
            }
        },
        {
            'name': 'Basic parameters with GCSH',
            'data': {
                'amount': '100.00',
                'merchant_id': config['merchant_id'],
                'order_id': f'TEST_GCSH_{int(time.time())}',
                'bank_code': 'GCSH',
                'return_url': 'https://test.com/success',
                'cancel_url': 'https://test.com/cancel',
                'notify_url': 'https://test.com/callback'
            }
        },
        {
            'name': 'With signature (MAYA)',
            'data': {
                'amount': '100.00',
                'merchant_id': config['merchant_id'],
                'order_id': f'TEST_SIG_MAYA_{int(time.time())}',
                'bank_code': 'MAYA',
                'return_url': 'https://test.com/success',
                'cancel_url': 'https://test.com/cancel',
                'notify_url': 'https://test.com/callback'
            }
        },
        {
            'name': 'Alternative parameter names',
            'data': {
                'deposit_amount': '100.00',
                'merchantId': config['merchant_id'],
                'orderId': f'TEST_ALT_{int(time.time())}',
                'paymentMethod': 'MAYA',
                'returnUrl': 'https://test.com/success',
                'cancelUrl': 'https://test.com/cancel',
                'notifyUrl': 'https://test.com/callback'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        data = test_case['data'].copy()
        
        # Add signature if needed
        if 'order_id' in data and test_case['name'].startswith('With signature'):
            signature = generate_signature(data['amount'], data['merchant_id'], data['order_id'], config['api_key'])
            data['signature'] = signature
            print(f"   Generated signature: {signature}")
        
        # Print test data
        print("   Test Data:")
        for key, value in data.items():
            print(f"     {key}: {value}")
        
        try:
            # Test POST request
            print(f"\n   📡 POST {base_url}{endpoint}")
            response = requests.post(f"{base_url}{endpoint}", data=data, timeout=15)
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            # Try to parse response
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                try:
                    json_data = response.json()
                    print(f"   JSON Response: {json.dumps(json_data, indent=4)}")
                    
                    # Check for success indicators
                    if 'payment_url' in json_data or 'redirect_url' in json_data:
                        print("   🎉 SUCCESS! Found payment URL!")
                    elif 'error' in json_data:
                        print(f"   ⚠️  API Error: {json_data.get('error')}")
                    elif 'message' in json_data:
                        print(f"   ⚠️  API Message: {json_data.get('message')}")
                        
                except json.JSONDecodeError:
                    print("   ❌ Invalid JSON in response")
            else:
                # Show first 300 chars of response
                response_text = response.text[:300]
                print(f"   Response preview: {response_text}...")
                
                if response.status_code == 500:
                    print("   ❌ Server Error")
                elif response.status_code == 400:
                    print("   ⚠️  Bad Request (check parameters)")
                elif response.status_code == 401:
                    print("   ⚠️  Unauthorized (check credentials)")
                elif response.status_code == 422:
                    print("   ⚠️  Validation Error (check required fields)")
                    
        except requests.exceptions.Timeout:
            print("   ❌ Request timeout")
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection error")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        print()

    # Test GET request to see if endpoint accepts GET
    print("\n🔍 Testing GET request")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}{endpoint}", timeout=10)
        print(f"GET Status: {response.status_code}")
        if response.status_code == 200:
            print("GET Response:", response.text[:200])
        elif response.status_code == 405:
            print("✓ Endpoint exists but only accepts POST")
    except Exception as e:
        print(f"GET Error: {e}")

if __name__ == "__main__":
    test_deposit_endpoint()
