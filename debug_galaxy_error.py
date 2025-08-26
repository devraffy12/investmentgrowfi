#!/usr/bin/env python3
"""
Debug Galaxy API Error - Tagalog Version
Troubleshoot "wrong mobile, username, or account number" error
"""

import requests
import hashlib
import time
from datetime import datetime

def debug_galaxy_api():
    """
    Debug Galaxy API para malaman kung bakit may error
    """
    
    # Galaxy API Configuration
    MERCHANT_ID = 'RodolfHitler'
    SECRET_KEY = '86cb40fe1666b41eb0ad21577d66baef'
    BASE_URL = 'https://cloud.la2568.site'
    
    print("🔍 GALAXY API ERROR DEBUGGING")
    print("=" * 50)
    print(f"📅 Oras: {datetime.now()}")
    print(f"🏪 Merchant ID: {MERCHANT_ID}")
    print(f"🌐 Base URL: {BASE_URL}")
    print()
    
    # Test different mobile number formats
    test_cases = [
        {
            'name': 'GCash - Standard Format',
            'mobile': '09171234567',
            'bank_code': 'gcash',
            'amount': '100.00'
        },
        {
            'name': 'GCash - With +63',
            'mobile': '+639171234567',
            'bank_code': 'gcash',
            'amount': '100.00'
        },
        {
            'name': 'PayMaya - PMP Code',
            'mobile': '09171234567',
            'bank_code': 'PMP',
            'amount': '100.00'
        },
        {
            'name': 'PayMaya - mya Code',
            'mobile': '09171234567',
            'bank_code': 'mya',
            'amount': '100.00'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🧪 TEST CASE {i}: {test_case['name']}")
        print("-" * 30)
        
        # Generate order ID
        order_id = f"TEST{int(time.time())}{i}"
        
        # Prepare parameters
        params = {
            'merchant': MERCHANT_ID,
            'payment_type': '2',  # WEB_H5
            'amount': test_case['amount'],
            'order_id': order_id,
            'bank_code': test_case['bank_code'],
            'callback_url': 'https://yoursite.com/callback',
            'return_url': 'https://yoursite.com/return',
        }
        
        # Generate signature
        sign_string = "&".join([f"{key}={value}" for key, value in sorted(params.items())])
        sign_string += f"&key={SECRET_KEY}"
        params['sign'] = hashlib.md5(sign_string.encode('utf-8')).hexdigest().lower()
        
        print(f"📱 Mobile: {test_case['mobile']}")
        print(f"🏦 Bank Code: {test_case['bank_code']}")
        print(f"💰 Amount: {test_case['amount']}")
        print(f"🔑 Order ID: {order_id}")
        print(f"✍️  Signature: {params['sign'][:20]}...")
        
        try:
            # Make API request
            response = requests.post(
                f"{BASE_URL}/api/transfer",
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"✅ Response: {result}")
                    
                    if 'status' in result:
                        if result['status'] == 'success':
                            print("✅ SUCCESS - API call working!")
                        else:
                            print(f"❌ ERROR: {result.get('message', 'Unknown error')}")
                            if 'wrong mobile' in result.get('message', '').lower():
                                print("🚨 MOBILE NUMBER FORMAT ISSUE DETECTED")
                                print("💡 Subukan mo:")
                                print("   - I-check kung tama yung format ng mobile number")
                                print("   - Siguraduhin na valid yung GCash/PayMaya account")
                                print("   - Contact Galaxy support para sa account verification")
                    
                except ValueError:
                    print(f"❌ Invalid JSON Response: {response.text[:200]}...")
            else:
                print(f"❌ HTTP Error: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {str(e)}")
        
        print()
    
    print("🔧 TROUBLESHOOTING TIPS:")
    print("=" * 50)
    print("1. 📱 Mobile Number Format:")
    print("   - Gamitin: 09XXXXXXXXX (11 digits)")
    print("   - O kaya: +639XXXXXXXXX (13 characters)")
    print()
    print("2. 🏦 Bank Codes:")
    print("   - GCash: 'gcash'")
    print("   - PayMaya: 'PMP' or 'mya'")
    print()
    print("3. 👤 Account Issues:")
    print("   - I-verify kung active pa yung merchant account")
    print("   - I-check kung tama yung secret key")
    print("   - Contact Galaxy support kung tuloy-tuloy yung error")
    print()
    print("4. 🔍 API Status:")
    print("   - Tignan kung down ba yung Galaxy API")
    print("   - I-check yung network connectivity")

if __name__ == "__main__":
    debug_galaxy_api()
