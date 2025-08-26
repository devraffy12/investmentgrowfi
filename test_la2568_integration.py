#!/usr/bin/env python3
"""
Test LA2568 Payment Integration
Tests the LA2568 API integration to ensure proper GCash payment flow
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from payments.la2568_service import la2568_service
import json

def test_la2568_payment_api():
    """Test LA2568 payment API integration"""
    print("🧪 Testing LA2568 Payment API Integration...")
    print(f"📍 Base URL: {la2568_service.base_url}")
    print(f"🔑 Merchant Key: {la2568_service.merchant_key[:8]}...")
    
    # Test payment creation
    print("\n💳 Testing Payment Creation...")
    
    test_cases = [
        {
            'order_id': 'TEST-GCASH-001',
            'amount': 100.00,
            'payment_method': 'gcash',
            'description': 'Test GCash payment'
        },
        {
            'order_id': 'TEST-MAYA-001', 
            'amount': 250.50,
            'payment_method': 'maya',
            'description': 'Test Maya payment'
        }
    ]
    
    for case in test_cases:
        print(f"\n🔄 Testing {case['payment_method'].upper()} payment...")
        print(f"   Amount: ₱{case['amount']}")
        print(f"   Order ID: {case['order_id']}")
        
        try:
            # Test payment creation
            result = la2568_service.create_payment(
                order_id=case['order_id'],
                amount=case['amount'],
                payment_method=case['payment_method'],
                callback_url='http://localhost:8000/payments/callback/',
                success_url='http://localhost:8000/payments/success/',
                cancel_url='http://localhost:8000/payments/cancel/'
            )
            
            print(f"   📊 API Response:")
            print(f"   Success: {result.get('success')}")
            
            if result.get('success'):
                print(f"   ✅ Payment created successfully!")
                print(f"   Order ID: {result.get('order_id')}")
                print(f"   Payment URL: {result.get('payment_url', 'Not provided')[:50]}...")
                print(f"   QR Code URL: {result.get('qr_code_url', 'Not provided')[:50]}...")
                
                if result.get('qr_code_base64'):
                    print(f"   QR Code Base64: {len(result.get('qr_code_base64', ''))} characters")
                else:
                    print(f"   QR Code Base64: Not provided")
                    
            else:
                print(f"   ❌ Payment creation failed!")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                print(f"   Details: {result.get('data', {})}")
                
        except Exception as e:
            print(f"   💥 Exception occurred: {e}")
    
    # Test signature generation
    print(f"\n🔐 Testing Signature Generation...")
    try:
        test_data = {
            'merchant': la2568_service.merchant_key,
            'order_id': 'TEST-001',
            'amount': '100.00',
            'pay_type': 'gcash'
        }
        
        signature = la2568_service.generate_signature(test_data)
        print(f"   ✅ Signature generated: {signature[:16]}...")
        
        # Verify signature
        is_valid = la2568_service.verify_signature(test_data, signature)
        print(f"   ✅ Signature verification: {is_valid}")
        
    except Exception as e:
        print(f"   ❌ Signature test failed: {e}")
    
    # Test merchant ID validation
    print(f"\n🏪 Testing Merchant Configuration...")
    print(f"   Merchant Key Length: {len(la2568_service.merchant_key)}")
    print(f"   Secret Key Length: {len(la2568_service.secret_key)}")
    print(f"   Deposit URL: {la2568_service.deposit_url}")
    
    if len(la2568_service.merchant_key) > 30:
        print(f"   ⚠️  Warning: Merchant key might be too long (LA2568 limit: 30 chars)")
    else:
        print(f"   ✅ Merchant key length is acceptable")
    
    print(f"\n📋 Summary:")
    print(f"   🔧 LA2568 Service: Initialized")
    print(f"   🌐 API Endpoint: {la2568_service.base_url}")
    print(f"   🔑 Authentication: Configured")
    print(f"   💰 Payment Methods: GCash, Maya")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Verify merchant account with LA2568 support")
    print(f"   2. Test with real payment amounts")
    print(f"   3. Verify webhook callbacks work properly")
    print(f"   4. Test on mobile device for app redirects")

if __name__ == '__main__':
    test_la2568_payment_api()
