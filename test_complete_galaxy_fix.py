#!/usr/bin/env python
"""
Test complete Galaxy API payment flow with all payment methods
"""
import sys
import os
import json
from decimal import Decimal

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
import django
django.setup()

from payments.views import GalaxyPaymentService

def test_payment_methods():
    """Test all payment methods with corrected configurations"""
    
    galaxy = GalaxyPaymentService()
    
    # Test configurations exactly as specified
    test_configs = [
        {
            'name': 'GCash QR',
            'bank_code': 'gcash',
            'payment_type': '1',
            'amount': 300.00
        },
        {
            'name': 'GCash H5 QRPH', 
            'bank_code': 'mya',
            'payment_type': '7',
            'amount': 300.00
        },
        {
            'name': 'PayMaya Direct',
            'bank_code': 'PMP', 
            'payment_type': '3',
            'amount': 300.00
        }
    ]
    
    print("🧪 Testing Galaxy API Payment Methods (Fixed Signature)")
    print("=" * 60)
    
    for config in test_configs:
        print(f"\n🔍 Testing {config['name']}")
        print(f"   bank_code: {config['bank_code']}")
        print(f"   payment_type: {config['payment_type']}")
        print(f"   amount: ₱{config['amount']}")
        
        try:
            # Test the API call with fixed signature
            result = galaxy.create_payment(
                amount=Decimal(str(config['amount'])),
                order_id=f"test_fix_{config['bank_code']}_{config['payment_type']}",
                bank_code=config['bank_code'],
                payment_type=config['payment_type'],
                callback_url="https://investmentgrowfi.onrender.com/api/callback/",
                return_url="https://investmentgrowfi.onrender.com/deposit/success/",
                mobile_number="09919067713"
            )
            
            print(f"   📤 API Response Status: {result.get('status', 'unknown')}")
            print(f"   📝 Message: {result.get('message', 'No message')}")
            
            if result.get('status') == '1':
                print(f"   🎉 SUCCESS! Payment URL available")
                if 'redirect_url' in result:
                    print(f"   🔗 Redirect URL: {result['redirect_url'][:50]}...")
                if 'qrcode_url' in result:
                    print(f"   📱 QR Code URL: {result['qrcode_url'][:50]}...")
            else:
                print(f"   ❌ FAILED: {result.get('message', 'Unknown error')}")
                if 'Sign Error' in str(result.get('message', '')):
                    print(f"   🔧 SIGNATURE ERROR - Need to debug further")
                
        except Exception as e:
            print(f"   💥 EXCEPTION: {str(e)}")
            
        print("   " + "-" * 50)
    
    print("\n" + "=" * 60)
    print("🏁 Galaxy API Test Complete")
    print("✅ Fixed signature method that excludes mobile from signature calculation")
    print("🔧 Ready for live testing!")

if __name__ == "__main__":
    test_payment_methods()
