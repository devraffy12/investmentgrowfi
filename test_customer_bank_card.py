#!/usr/bin/env python
"""
Test Galaxy API with customer_bank_card_account parameter
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

def test_galaxy_customer_bank_card():
    """Test Galaxy API with customer_bank_card_account parameter"""
    
    galaxy = GalaxyPaymentService()
    
    print("🧪 Testing Galaxy API with customer_bank_card_account")
    print("=" * 60)
    
    # Test configurations
    test_configs = [
        {
            'name': 'GCash QR',
            'bank_code': 'gcash',
            'payment_type': '1',
            'mobile': '09171234567'
        },
        {
            'name': 'PayMaya Direct',
            'bank_code': 'PMP', 
            'payment_type': '3',
            'mobile': '09919067713'
        },
        {
            'name': 'Maya H5',
            'bank_code': 'mya',
            'payment_type': '7',
            'mobile': '09123456789'
        }
    ]
    
    for config in test_configs:
        print(f"\n🔍 Testing {config['name']}")
        print(f"   bank_code: {config['bank_code']}")
        print(f"   payment_type: {config['payment_type']}")
        print(f"   mobile: {config['mobile']}")
        
        try:
            # Test the API call with customer_bank_card_account
            result = galaxy.create_payment(
                amount=Decimal('300.00'),
                order_id=f"test_card_{config['bank_code']}",
                bank_code=config['bank_code'],
                payment_type=config['payment_type'],
                callback_url="https://investmentgrowfi.onrender.com/api/callback/",
                return_url="https://investmentgrowfi.onrender.com/deposit/success/",
                mobile_number=config['mobile']
            )
            
            print(f"   📤 API Status: {result.get('status', 'unknown')}")
            print(f"   📝 Message: {result.get('message', 'No message')}")
            
            if result.get('status') == '1':
                print(f"   🎉 SUCCESS! API accepts customer_bank_card_account")
                if 'redirect_url' in result:
                    print(f"   🔗 Redirect URL: {result['redirect_url'][:50]}...")
            else:
                print(f"   ❌ FAILED: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   💥 EXCEPTION: {str(e)}")
            
        print("   " + "-" * 50)
    
    print("\n" + "=" * 60)
    print("🎯 Expected API Payload Structure:")
    print(json.dumps({
        "merchant": "RodolfHitler",
        "payment_type": "3",
        "amount": "300.00", 
        "order_id": "test_order_123",
        "bank_code": "PMP",
        "customer_bank_card_account": "09919067713",
        "callback_url": "https://investmentgrowfi.onrender.com/api/callback/",
        "return_url": "https://investmentgrowfi.onrender.com/deposit/success/",
        "sign": "generated_md5_signature"
    }, indent=2))

if __name__ == "__main__":
    test_galaxy_customer_bank_card()
