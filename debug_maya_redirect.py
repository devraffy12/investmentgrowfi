#!/usr/bin/env python
"""
Debug Maya redirect URL to see what's happening
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

def debug_maya_redirect():
    """Debug the exact Maya redirect URL we're getting"""
    
    galaxy = GalaxyPaymentService()
    
    print("🔍 Debugging Maya Redirect URL")
    print("=" * 50)
    
    try:
        # Test PayMaya Direct without mobile number
        result = galaxy.create_payment(
            amount=Decimal('300.00'),
            order_id="debug_maya_redirect_001",
            bank_code='PMP',  # PayMaya Direct
            payment_type='3',
            callback_url="https://investmentgrowfi.onrender.com/api/callback/",
            return_url="https://investmentgrowfi.onrender.com/deposit/success/"
            # NO mobile_number parameter
        )
        
        print(f"📤 Galaxy API Status: {result.get('status')}")
        print(f"📝 Galaxy API Message: {result.get('message')}")
        
        if result.get('status') == '1':
            print("✅ Galaxy API SUCCESS!")
            
            redirect_url = result.get('redirect_url')
            qrcode_url = result.get('qrcode_url')
            
            print(f"\n🔗 Redirect URL: {redirect_url}")
            print(f"📱 QR Code URL: {qrcode_url}")
            
            if redirect_url:
                print(f"\n📋 URL Analysis:")
                print(f"   Domain: {redirect_url.split('/')[2] if '/' in redirect_url else 'N/A'}")
                print(f"   Full URL: {redirect_url}")
                
                # Check if it contains Maya/PayMaya indicators
                if 'maya' in redirect_url.lower() or 'paymaya' in redirect_url.lower():
                    print("   🎯 This redirects to Maya/PayMaya")
                elif 'cloudhub' in redirect_url.lower():
                    print("   🌐 This redirects to CloudHub (Gateway)")
                else:
                    print("   ❓ Unknown redirect destination")
                    
        else:
            print(f"❌ Galaxy API FAILED: {result.get('message')}")
            
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 CONCLUSION:")
    print("If Galaxy API returns success and redirect URL,")
    print("then the 'mobile error' is happening on Maya's payment page,")
    print("NOT in our code or Galaxy API.")

if __name__ == "__main__":
    debug_maya_redirect()
