#!/usr/bin/env python
"""
Test script for GCash deposit functionality
This will test the Galaxy API integration without making actual payments
"""

import os
import django
import json
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from django.contrib.auth.models import User
from payments.views import GalaxyPaymentService
from myproject.models import UserProfile, Transaction
from payments.models import Transaction as PaymentTransaction

def test_gcash_deposit():
    """Test GCash deposit flow"""
    print("🧪 Testing GCash Deposit Functionality...")
    print("=" * 50)
    
    # Initialize Galaxy service
    galaxy_service = GalaxyPaymentService()
    
    # Test data
    test_amount = Decimal('500.00')
    test_order_id = "TEST_GCASH_001"
    
    print(f"📊 Test Parameters:")
    print(f"   Amount: ₱{test_amount}")
    print(f"   Order ID: {test_order_id}")
    print(f"   Payment Method: GCash QR")
    print()
    
    try:
        # Test Galaxy API configuration
        print("🔧 Testing Galaxy API Configuration...")
        print(f"   Merchant ID: {galaxy_service.merchant_id}")
        print(f"   API Domain: {galaxy_service.api_domain}")
        print(f"   Secret Key: {'*' * 10}...")
        print()
        
        # Test GCash QR payment creation
        print("💳 Testing GCash QR Payment Creation...")
        gcash_qr_result = galaxy_service.create_payment(
            amount=test_amount,
            order_id=f"{test_order_id}_QR",
            bank_code='gcash',
            payment_type='1',  # QR Code
            callback_url='https://test.com/callback',
            return_url='https://test.com/return'
        )
        
        print("📋 GCash QR API Response:")
        print(json.dumps(gcash_qr_result, indent=2, default=str))
        print()
        
        # Test GCash Mobile payment creation
        print("📱 Testing GCash Mobile Payment Creation...")
        gcash_mobile_result = galaxy_service.create_payment(
            amount=test_amount,
            order_id=f"{test_order_id}_MOBILE",
            bank_code='mya',
            payment_type='7',  # Mobile redirect
            callback_url='https://test.com/callback',
            return_url='https://test.com/return'
        )
        
        print("📋 GCash Mobile API Response:")
        print(json.dumps(gcash_mobile_result, indent=2, default=str))
        print()
        
        # Analyze results
        print("🔍 Analysis:")
        print("-" * 30)
        
        # Check GCash QR
        if gcash_qr_result.get('status') == '1':
            print("✅ GCash QR: SUCCESS")
            if gcash_qr_result.get('qrcode_url') or gcash_qr_result.get('redirect_url'):
                print("   ✅ Payment URL available")
            else:
                print("   ⚠️  No payment URL in response")
        else:
            print("❌ GCash QR: FAILED")
            print(f"   Error: {gcash_qr_result.get('message', 'Unknown error')}")
        
        # Check GCash Mobile
        if gcash_mobile_result.get('status') == '1':
            print("✅ GCash Mobile: SUCCESS")
            if gcash_mobile_result.get('redirect_url'):
                print("   ✅ Redirect URL available")
            else:
                print("   ⚠️  No redirect URL in response")
        else:
            print("❌ GCash Mobile: FAILED")
            print(f"   Error: {gcash_mobile_result.get('message', 'Unknown error')}")
        
        print()
        print("🏥 Health Check Summary:")
        print("-" * 30)
        
        # Overall health check
        qr_healthy = gcash_qr_result.get('status') == '1'
        mobile_healthy = gcash_mobile_result.get('status') == '1'
        
        if qr_healthy and mobile_healthy:
            print("🟢 EXCELLENT: Both GCash methods working")
        elif qr_healthy or mobile_healthy:
            print("🟡 PARTIAL: One GCash method working")
        else:
            print("🔴 CRITICAL: Both GCash methods failing")
        
        # Recommendations
        print()
        print("💡 Recommendations:")
        print("-" * 30)
        
        if not qr_healthy:
            print("• Check GCash QR configuration (bank_code: gcash, payment_type: 1)")
        if not mobile_healthy:
            print("• Check GCash Mobile configuration (bank_code: mya, payment_type: 7)")
        
        if qr_healthy and mobile_healthy:
            print("• All GCash methods are working correctly!")
            print("• Users can make deposits via GCash QR and Mobile")
        
    except Exception as e:
        print(f"❌ Critical Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gcash_deposit()
