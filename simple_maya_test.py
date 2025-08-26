#!/usr/bin/env python
"""
Simple Maya Payment Test - No Django dependency
"""
import requests
import json
import hashlib

def test_maya_payment_simple():
    """Test Maya payment directly with Galaxy API"""
    
    print("🧪 SIMPLE MAYA PAYMENT TEST")
    print("=" * 50)
    
    # Galaxy API parameters (with customer_bank_card_account)
    params = {
        'merchant': 'RodolfHitler',
        'payment_type': '3',  # PayMaya Direct
        'amount': '300.00',
        'order_id': 'simple_test_002',
        'bank_code': 'PMP',  # PayMaya Direct
        'customer_bank_card_account': '09919067713',
        'callback_url': 'https://investmentgrowfi.onrender.com/api/callback/',
        'return_url': 'https://investmentgrowfi.onrender.com/deposit/success/'
    }
    
    # Generate signature (exclude customer_bank_card_account)
    signature_params = {k: v for k, v in params.items() if k != 'customer_bank_card_account'}
    ordered_keys = sorted(signature_params.keys())
    query_string = '&'.join([f"{k}={signature_params[k]}" for k in ordered_keys])
    secret_key = '86cb40fe1666b41eb0ad21577d66baef'
    sign_string = f"{query_string}&key={secret_key}"
    signature = hashlib.md5(sign_string.encode()).hexdigest().lower()
    
    params['sign'] = signature
    
    print("📤 Request Parameters:")
    for key, value in params.items():
        if key != 'sign':
            print(f"   {key}: {value}")
    print(f"   sign: {signature}")
    print()
    
    try:
        response = requests.post(
            'https://cloud.la2568.site/api/transfer',
            data=params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        result = response.json()
        print(f"📤 API Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('status') == '1':
            print("\n✅ GALAXY API SUCCESS!")
            print("🔗 Payment URL available - Galaxy integration is working")
            print("🎯 If users still get errors, it's on Maya's payment page")
        else:
            print(f"\n❌ GALAXY API ERROR: {result.get('message')}")
            print("🔧 Need to fix Galaxy API integration")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_maya_payment_simple()
