#!/usr/bin/env python
"""
Debug Maya mobile number issue - test different scenarios
"""
import sys
import os
import json
from decimal import Decimal
import requests

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')
import django
django.setup()

from payments.views import GalaxyPaymentService, generate_galaxy_signature

def debug_maya_mobile_issue():
    """Debug the exact Maya mobile number issue"""
    
    print("🔍 Debugging Maya Mobile Number Issue")
    print("=" * 60)
    
    # Test the exact number that CloudPay specified
    test_cases = [
        {
            'name': 'CloudPay Specified Number',
            'mobile': '09919067713',
            'description': 'Exact number from CloudPay team'
        },
        {
            'name': 'Same Number +63 Format',
            'mobile': '+639919067713',
            'description': 'International format'
        },
        {
            'name': 'Same Number 63 Format',
            'mobile': '639919067713',
            'description': 'International without +'
        },
        {
            'name': 'No Mobile Parameter',
            'mobile': None,
            'description': 'Test without mobile parameter'
        }
    ]
    
    galaxy = GalaxyPaymentService()
    
    for case in test_cases:
        print(f"\n📱 Testing: {case['name']}")
        print(f"   Mobile: {case['mobile']}")
        print(f"   Description: {case['description']}")
        
        try:
            # Prepare Galaxy API parameters manually
            params = {
                'merchant': galaxy.merchant_id,
                'payment_type': '3',  # PayMaya Direct
                'amount': '100.00',
                'order_id': f"debug_maya_{case['name'].replace(' ', '_').lower()}",
                'bank_code': 'PMP',  # PayMaya
                'callback_url': 'https://investmentgrowfi.onrender.com/api/callback/',
                'return_url': 'https://investmentgrowfi.onrender.com/deposit/success/'
            }
            
            # Add mobile only if provided
            if case['mobile']:
                params['mobile'] = case['mobile']
                print(f"   📤 Including mobile parameter: {case['mobile']}")
            else:
                print(f"   📤 NO mobile parameter included")
            
            # Generate signature manually to see what's included
            signature = generate_galaxy_signature(params, galaxy.secret_key)
            params['sign'] = signature
            
            print(f"   🔐 Generated signature: {signature}")
            print(f"   📋 Full parameters: {json.dumps(params, indent=4)}")
            
            # Make direct API call to see exact response
            response = requests.post(
                f"{galaxy.api_domain}/api/transfer",
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            print(f"   📊 Response Status: {response.status_code}")
            
            try:
                result = response.json()
                print(f"   📋 Response Data: {json.dumps(result, indent=4)}")
                
                if result.get('status') == '1':
                    print(f"   ✅ SUCCESS!")
                    print(f"   🔗 Redirect URL: {result.get('redirect_url', 'N/A')}")
                else:
                    print(f"   ❌ FAILED: {result.get('message', 'Unknown error')}")
                    
                    # Check if it's mobile number related error
                    message = str(result.get('message', '')).lower()
                    if 'mobile' in message or 'username' in message or 'account' in message:
                        print(f"   🚨 MOBILE NUMBER ERROR DETECTED!")
                        
            except json.JSONDecodeError:
                print(f"   💥 Invalid JSON response: {response.text}")
                
        except Exception as e:
            print(f"   💥 EXCEPTION: {str(e)}")
            
        print("   " + "-" * 50)
    
    print("\n" + "=" * 60)
    print("🔍 Debug Analysis Complete")
    print("💡 Look for patterns in successful vs failed responses")

if __name__ == "__main__":
    debug_maya_mobile_issue()
