#!/usr/bin/env python
"""
Test Updated LA2568 Integration
"""

import os
import sys
import django
import requests
import hashlib

# Setup Django environment
sys.path.append('c:\\Users\\raffy\\OneDrive\\Desktop\\investment')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from payments.la2568_service import la2568_service

def test_updated_la2568():
    """Test the updated LA2568 integration"""
    print("🚀 Testing Updated LA2568 Integration")
    print("=" * 50)
    
    # Test the signature generation
    params = {
        'merchant': 'RodolfHitler',
        'payment_type': '3',
        'amount': '100.00',
        'order_id': 'TEST123456',
        'bank_code': 'gcash',
        'callback_url': 'https://investmentgrowfi.onrender.com/api/callback',
        'return_url': 'https://investmentgrowfi.onrender.com/deposit/success'
    }
    
    signature = la2568_service.generate_signature(params)
    print(f"🔐 Generated signature: {signature}")
    
    # Test actual API call
    print(f"\n📡 Testing actual LA2568 API call...")
    import time
    from decimal import Decimal
    
    test_order_id = f"TEST_FIX_{int(time.time())}"
    result = la2568_service.create_deposit(
        amount=Decimal('100.00'),
        order_id=test_order_id,
        payment_method='gcash'
    )
    
    print(f"📊 API Result:")
    print(f"  Success: {result.get('success')}")
    print(f"  Status: {result.get('status')}")
    print(f"  Message: {result.get('message', 'N/A')}")
    print(f"  Order ID: {result.get('order_id', 'N/A')}")
    print(f"  Redirect URL: {result.get('redirect_url', 'N/A')}")
    
    if result.get('redirect_url'):
        print(f"\n🎉 SUCCESS! Got redirect URL: {result['redirect_url']}")
        print(f"✅ PAY WITH GCASH button should now work!")
        return True
    else:
        print(f"\n❌ Still no redirect URL")
        print(f"📄 Raw response: {result.get('raw_response', {})}")
        return False

if __name__ == "__main__":
    success = test_updated_la2568()
    
    if success:
        print(f"\n🎯 Integration Fixed! Ready to deploy.")
    else:
        print(f"\n🔧 Still needs fixing. Check LA2568 API response.")
