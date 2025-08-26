#!/usr/bin/env python
"""
Test different mobile number formats with Maya API
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

def test_maya_mobile_formats():
    """Test different mobile number formats for Maya API"""
    
    galaxy = GalaxyPaymentService()
    
    # Different mobile number formats to test
    mobile_formats = [
        "09919067713",      # Current format (CloudPay specified)
        "+639919067713",    # International format
        "639919067713",     # International without +
        "9919067713",       # Without leading 0
        "09171234567",      # Different Globe number
        "+639171234567",    # Different Globe number (international)
        "09123456789",      # Smart number
        "+639123456789"     # Smart number (international)
    ]
    
    print("🧪 Testing Maya API Mobile Number Formats")
    print("=" * 60)
    
    for mobile in mobile_formats:
        print(f"\n📱 Testing mobile format: {mobile}")
        
        try:
            # Test PayMaya Direct with different mobile formats
            result = galaxy.create_payment(
                amount=Decimal('100.00'),  # Smaller test amount
                order_id=f"test_mobile_{mobile.replace('+', '').replace('0', 'o')}",
                bank_code='PMP',  # PayMaya Direct
                payment_type='3',
                callback_url="https://investmentgrowfi.onrender.com/api/callback/",
                return_url="https://investmentgrowfi.onrender.com/deposit/success/",
                mobile_number=mobile
            )
            
            print(f"   📤 Status: {result.get('status', 'unknown')}")
            print(f"   📝 Message: {result.get('message', 'No message')}")
            
            if result.get('status') == '1':
                print(f"   🎉 SUCCESS! Mobile format works")
            elif 'mobile' in str(result.get('message', '')).lower():
                print(f"   ❌ MOBILE ERROR: {result.get('message', '')}")
            elif 'username' in str(result.get('message', '')).lower():
                print(f"   ❌ USERNAME ERROR: {result.get('message', '')}")
            else:
                print(f"   ⚠️  OTHER ERROR: {result.get('message', '')}")
                
        except Exception as e:
            print(f"   💥 EXCEPTION: {str(e)}")
            
        print("   " + "-" * 40)
    
    print("\n" + "=" * 60)
    print("🔍 Analysis Complete")
    print("💡 Look for SUCCESS messages to find working mobile format")

if __name__ == "__main__":
    test_maya_mobile_formats()
