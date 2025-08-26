#!/usr/bin/env python
"""
Test Galaxy API deposit with correct configurations
"""
import os
import sys
import django
import json
from decimal import Decimal

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
django.setup()

from payments.views import GalaxyPaymentService

def test_galaxy_payment_methods():
    """Test all Galaxy payment methods with correct configurations"""
    
    # Initialize Galaxy service
    galaxy = GalaxyPaymentService()
    
    # Test configurations based on your specs
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
    
    print("🧪 Testing Galaxy API Payment Methods")
    print("=" * 50)
    
    for config in test_configs:
        print(f"\n🔍 Testing {config['name']}")
        print(f"   bank_code: {config['bank_code']}")
        print(f"   payment_type: {config['payment_type']}")
        print(f"   amount: ₱{config['amount']}")
        
        try:
            # Test the API call
            result = galaxy.create_payment(
                amount=Decimal(str(config['amount'])),
                order_id=f"test_{config['bank_code']}_{config['payment_type']}",
                bank_code=config['bank_code'],
                payment_type=config['payment_type'],
                callback_url="https://investmentgrowfi.onrender.com/api/callback/",
                return_url="https://investmentgrowfi.onrender.com/deposit/success/",
                mobile_number="09919067713"  # Using default mobile number
            )
            
            print(f"   ✅ API Response: {json.dumps(result, indent=2)}")
            
            if result.get('status') == '1':
                print(f"   🎉 SUCCESS: Payment URL available")
                if 'redirect_url' in result:
                    print(f"   🔗 Redirect URL: {result['redirect_url']}")
            else:
                print(f"   ❌ FAILED: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   💥 ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Galaxy API Test Complete")

if __name__ == "__main__":
    test_galaxy_payment_methods()
